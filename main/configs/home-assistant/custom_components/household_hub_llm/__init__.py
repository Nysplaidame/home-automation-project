"""Expose read-only Household Hub knowledge tools to Home Assistant."""

from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.const import CONF_TIMEOUT, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv, llm
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.json import JsonObjectType

DOMAIN = "household_hub_llm"
CONF_SECRET = "secret"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_URL): cv.url,
                vol.Required(CONF_SECRET): cv.string,
                vol.Optional(CONF_TIMEOUT, default=45): vol.All(
                    vol.Coerce(int), vol.Range(min=3, max=120)
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


class HubTool(llm.Tool):
    def __init__(self, url: str, secret: str, timeout: int) -> None:
        self._url = url.rstrip("/")
        self._secret = secret
        self._timeout = timeout

    async def _post(
        self,
        hass: HomeAssistant,
        path: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        session = async_get_clientsession(hass)
        try:
            async with session.post(
                f"{self._url}{path}",
                headers={"X-Household-Hub-Secret": self._secret},
                json=body,
                timeout=aiohttp.ClientTimeout(total=self._timeout),
            ) as response:
                response.raise_for_status()
                return await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise HomeAssistantError(f"Household Hub request failed: {err}") from err


class HouseholdKnowledgeTool(HubTool):
    name = "household_knowledge_query"
    description = (
        "Search the household knowledge archive and transcript citations. Use "
        "for how-to, provenance, research, and general gardening knowledge. Do "
        "not use for current GardenKeeper task state or device control."
    )
    parameters = vol.Schema(
        {
            vol.Required("question"): vol.All(
                cv.string, vol.Length(min=3, max=1000)
            ),
            vol.Optional("tags", default=[]): [
                vol.All(cv.string, vol.Length(min=1, max=100))
            ],
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> JsonObjectType:
        args = self.parameters(tool_input.tool_args)
        payload = await self._post(
            hass,
            "/api/assistant/knowledge-query",
            {"question": args["question"], "top_k": 3, "tags": args["tags"]},
        )
        return {
            "answer": payload.get("answer", ""),
            "sources": [
                {
                    "title": citation.get("source_title") or "Untitled source",
                    "url": citation.get("source_url", ""),
                }
                for citation in payload.get("citations", [])[:3]
            ],
        }


class RecipeResearchTool(HubTool):
    name = "household_recipe_research"
    description = (
        "Research new recipe candidates with Household Hub provenance. Use for "
        "finding recipes not already saved. This tool does not import or modify "
        "Mealie."
    )
    parameters = vol.Schema(
        {
            vol.Required("query"): vol.All(
                cv.string, vol.Length(min=2, max=300)
            ),
            vol.Optional("ingredients", default=[]): [
                vol.All(cv.string, vol.Length(min=1, max=100))
            ],
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> JsonObjectType:
        args = self.parameters(tool_input.tool_args)
        payload = await self._post(
            hass,
            "/api/assistant/recipes/search",
            {"query": args["query"], "ingredients": args["ingredients"], "limit": 5},
        )
        return {
            "query": payload.get("query", args["query"]),
            "results": [
                {
                    "title": result.get("title", "")[:300],
                    "url": result.get("url", "")[:500],
                    "summary": result.get("summary", "")[:500],
                }
                for result in payload.get("results", [])[:5]
            ],
        }


class HouseholdHubAPI(llm.API):
    def __init__(self, hass: HomeAssistant, url: str, secret: str, timeout: int) -> None:
        super().__init__(
            hass=hass,
            id="household_knowledge",
            name="Household Knowledge Hub",
        )
        self._tools = [
            HouseholdKnowledgeTool(url, secret, timeout),
            RecipeResearchTool(url, secret, timeout),
        ]

    async def async_get_api_instance(
        self, llm_context: llm.LLMContext
    ) -> llm.APIInstance:
        return llm.APIInstance(
            api=self,
            api_prompt=(
                "Household Hub owns research, transcript RAG, and provenance. "
                "Use it for knowledge questions and new recipe research. It is "
                "read-only from voice and never owns current garden task state."
            ),
            llm_context=llm_context,
            tools=self._tools,
        )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    settings = config[DOMAIN]
    hass.data[DOMAIN] = llm.async_register_api(
        hass,
        HouseholdHubAPI(
            hass,
            settings[CONF_URL],
            settings[CONF_SECRET],
            settings[CONF_TIMEOUT],
        ),
    )
    return True
