"""Expose the local SearXNG instance as a Home Assistant LLM tool."""

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

DOMAIN = "searxng_llm"
CONF_RESULT_COUNT = "result_count"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_URL): cv.url,
                vol.Optional(CONF_RESULT_COUNT, default=3): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=5)
                ),
                vol.Optional(CONF_TIMEOUT, default=15): vol.All(
                    vol.Coerce(int), vol.Range(min=3, max=30)
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


class WebSearchTool(llm.Tool):
    """Search the web through the local SearXNG service."""

    name = "web_search"
    description = (
        "Search the internet for current or detailed information. Use this for "
        "recipes, news, recommendations, products, documentation, and facts "
        "that may have changed. Base the answer on the returned sources."
    )
    parameters = vol.Schema(
        {
            vol.Required("query", description="Focused web search query"): vol.All(
                cv.string, vol.Length(min=2, max=300)
            )
        }
    )

    def __init__(self, url: str, result_count: int, timeout: int) -> None:
        """Initialize the search tool."""
        self._url = url.rstrip("/")
        self._result_count = result_count
        self._timeout = timeout

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> JsonObjectType:
        """Run a bounded SearXNG JSON search."""
        query = self.parameters(tool_input.tool_args)["query"]
        session = async_get_clientsession(hass)

        try:
            async with session.get(
                f"{self._url}/search",
                params={"q": query, "format": "json"},
                timeout=aiohttp.ClientTimeout(total=self._timeout),
            ) as response:
                response.raise_for_status()
                payload: dict[str, Any] = await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise HomeAssistantError(f"SearXNG search failed: {err}") from err

        results = []
        for result in payload.get("results", [])[: self._result_count]:
            results.append(
                {
                    "title": str(result.get("title", ""))[:200],
                    "url": str(result.get("url", ""))[:500],
                    "snippet": str(result.get("content", ""))[:700],
                }
            )

        return {
            "success": bool(results),
            "query": query,
            "results": results,
        }


class SearXNGAPI(llm.API):
    """Home Assistant LLM API backed by SearXNG."""

    def __init__(
        self, hass: HomeAssistant, url: str, result_count: int, timeout: int
    ) -> None:
        """Initialize the API."""
        super().__init__(hass=hass, id="searxng_search", name="SearXNG Web Search")
        self._tool = WebSearchTool(url, result_count, timeout)

    async def async_get_api_instance(
        self, llm_context: llm.LLMContext
    ) -> llm.APIInstance:
        """Return the search API instance."""
        return llm.APIInstance(
            api=self,
            api_prompt=(
                "Use web_search before answering requests that need internet "
                "research or detailed recipes. Do not claim that no results were "
                "found unless the tool was called and returned no results."
            ),
            llm_context=llm_context,
            tools=[self._tool],
        )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the SearXNG LLM API."""
    settings = config[DOMAIN]
    hass.data[DOMAIN] = llm.async_register_api(
        hass,
        SearXNGAPI(
            hass,
            settings[CONF_URL],
            settings[CONF_RESULT_COUNT],
            settings[CONF_TIMEOUT],
        ),
    )
    return True
