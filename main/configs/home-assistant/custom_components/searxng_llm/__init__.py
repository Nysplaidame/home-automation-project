"""Expose the local SearXNG instance as a Home Assistant LLM tool."""

from __future__ import annotations

import re
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
            ),
            vol.Optional(
                "news",
                description=(
                    "true for news, headlines, sports results, scores and anything from today or "
                    "yesterday: searches recent news stories instead of general web pages"
                ),
            ): cv.boolean,
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
        args = self.parameters(tool_input.tool_args)
        query = args["query"]
        news = bool(args.get("news"))
        session = async_get_clientsession(hass)

        # News mode asks SearXNG's news category for the last day, then the last week, then falls back to the
        # plain search. The default search returns news-site home pages with no headlines in them, and the
        # news engines return nothing for a bare "latest headlines" (6 stories for "latest headlines news"),
        # so the word "news" is added to the query when it is missing.
        news_query = query if re.search(r"\bnews\b", query, re.IGNORECASE) else f"{query} news"
        attempts: list[tuple[str, dict[str, str]]] = (
            [
                (news_query, {"categories": "news", "time_range": "day"}),
                (news_query, {"categories": "news", "time_range": "week"}),
                (query, {}),
            ]
            if news
            else [(query, {})]
        )
        payload: dict[str, Any] = {}
        for text, extra in attempts:
            try:
                async with session.get(
                    f"{self._url}/search",
                    params={"q": text, "format": "json", **extra},
                    timeout=aiohttp.ClientTimeout(total=self._timeout),
                ) as response:
                    response.raise_for_status()
                    payload = await response.json(content_type=None)
            except (aiohttp.ClientError, TimeoutError) as err:
                raise HomeAssistantError(f"SearXNG search failed: {err}") from err
            if payload.get("results"):
                break

        results = []
        for result in payload.get("results", [])[: max(self._result_count, 6) if news else self._result_count]:
            results.append(
                {
                    "title": str(result.get("title", ""))[:200],
                    "url": str(result.get("url", ""))[:500],
                    "snippet": str(result.get("content", ""))[:700],
                }
            )

        answer: dict[str, Any] = {
            "success": bool(results),
            "query": query,
            "results": results,
        }
        if news:
            answer["news"] = True
        return answer


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
