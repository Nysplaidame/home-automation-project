"""Expose Mealie recipe actions as Home Assistant LLM tools."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import aiohttp
import voluptuous as vol

from homeassistant.const import CONF_TIMEOUT, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv, llm
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.json import JsonObjectType

DOMAIN = "mealie_llm"
CONF_TOKEN = "token"
CONF_RESULT_COUNT = "result_count"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_URL): cv.url,
                vol.Required(CONF_TOKEN): cv.string,
                vol.Optional(CONF_RESULT_COUNT, default=5): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=10)
                ),
                vol.Optional(CONF_TIMEOUT, default=30): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=120)
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def _clean_text(value: Any, limit: int = 1200) -> str:
    """Return a bounded plain string."""
    return str(value or "").strip()[:limit]


def _recipe_summary(recipe: dict[str, Any]) -> dict[str, Any]:
    """Return the small recipe shape useful to an LLM."""
    return {
        "name": _clean_text(recipe.get("name"), 200),
        "slug": _clean_text(recipe.get("slug"), 200),
        "description": _clean_text(recipe.get("description"), 500),
        "source_url": _clean_text(recipe.get("orgURL"), 500),
        "total_time": _clean_text(recipe.get("totalTime"), 100),
        "prep_time": _clean_text(recipe.get("prepTime"), 100),
        "cook_time": _clean_text(recipe.get("cookTime"), 100),
        "servings": recipe.get("recipeServings") or recipe.get("recipeYield"),
    }


def _recipe_details(recipe: dict[str, Any]) -> dict[str, Any]:
    """Return ingredients and method in a voice-friendly form."""
    ingredients = []
    for ingredient in recipe.get("recipeIngredient") or []:
        ingredients.append(
            _clean_text(
                ingredient.get("display")
                or ingredient.get("originalText")
                or ingredient.get("note"),
                300,
            )
        )

    steps = []
    for step in recipe.get("recipeInstructions") or []:
        steps.append(
            {
                "title": _clean_text(step.get("title"), 120),
                "text": _clean_text(step.get("text"), 1200),
            }
        )

    return {
        **_recipe_summary(recipe),
        "ingredients": [item for item in ingredients if item],
        "steps": [step for step in steps if step["text"]],
    }


class MealieTool(llm.Tool):
    """Base class for Mealie tools."""

    def __init__(self, url: str, token: str, timeout: int) -> None:
        """Initialize the Mealie API client bits."""
        self._url = url.rstrip("/")
        self._token = token
        self._timeout = timeout

    async def _request(
        self,
        hass: HomeAssistant,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """Run an authenticated Mealie request."""
        session = async_get_clientsession(hass)
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._token}"

        try:
            async with session.request(
                method,
                f"{self._url}{path}",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self._timeout),
                **kwargs,
            ) as response:
                response.raise_for_status()
                return await response.json(content_type=None)
        except aiohttp.ClientResponseError as err:
            raise HomeAssistantError(
                f"Mealie request failed: HTTP {err.status} {err.message}"
            ) from err
        except (aiohttp.ClientError, TimeoutError) as err:
            raise HomeAssistantError(f"Mealie request failed: {err!r}") from err


class ImportRecipeUrlTool(MealieTool):
    """Import a recipe URL into Mealie."""

    name = "import_recipe_url"
    description = (
        "Save a specific recipe URL into Mealie after the user has chosen that "
        "recipe. Do not use this for generic searches or without an explicit URL."
    )
    parameters = vol.Schema(
        {
            vol.Required("url", description="Recipe page URL to save"): cv.url,
            vol.Optional(
                "include_tags",
                default=True,
                description="Import recipe tags when Mealie can parse them",
            ): cv.boolean,
            vol.Optional(
                "include_categories",
                default=True,
                description="Import recipe categories when Mealie can parse them",
            ): cv.boolean,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> JsonObjectType:
        """Import a recipe by URL."""
        args = self.parameters(tool_input.tool_args)
        imported = await self._request(
            hass,
            "POST",
            "/api/recipes/create/url",
            json={
                "url": args["url"],
                "includeTags": args["include_tags"],
                "includeCategories": args["include_categories"],
            },
        )
        if isinstance(imported, str):
            recipe = await self._request(hass, "GET", f"/api/recipes/{imported}")
        else:
            recipe = imported

        return {
            "success": True,
            "recipe": _recipe_summary(recipe),
        }


class FindRecipesTool(MealieTool):
    """Search recipes already saved in Mealie."""

    name = "find_saved_recipes"
    description = "Search recipes already saved in Mealie."
    parameters = vol.Schema(
        {
            vol.Required("query", description="Recipe search text"): vol.All(
                cv.string, vol.Length(min=1, max=200)
            )
        }
    )

    def __init__(self, url: str, token: str, timeout: int, result_count: int) -> None:
        """Initialize the search tool."""
        super().__init__(url, token, timeout)
        self._result_count = result_count

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> JsonObjectType:
        """Search saved recipes."""
        query = self.parameters(tool_input.tool_args)["query"]
        payload = await self._request(
            hass,
            "GET",
            "/api/recipes",
            params={"search": query, "page": 1, "perPage": self._result_count},
        )
        recipes = payload.get("items", payload if isinstance(payload, list) else [])

        return {
            "success": bool(recipes),
            "query": query,
            "recipes": [_recipe_summary(recipe) for recipe in recipes],
        }


class GetRecipeTool(MealieTool):
    """Read one saved recipe from Mealie."""

    name = "get_saved_recipe"
    description = (
        "Read ingredients and method from a recipe already saved in Mealie. "
        "Use the recipe slug returned by find_saved_recipes or import_recipe_url. "
        "If the user gives a recipe name instead, pass that name."
    )
    parameters = vol.Schema(
        {
            vol.Required("slug", description="Mealie recipe slug or name"): vol.All(
                cv.string, vol.Length(min=1, max=300)
            )
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> JsonObjectType:
        """Fetch one saved recipe."""
        slug = self.parameters(tool_input.tool_args)["slug"]
        looks_like_slug = " " not in slug and slug.lower() == slug
        recipe = None
        if looks_like_slug:
            try:
                recipe = await self._request(hass, "GET", f"/api/recipes/{quote(slug)}")
            except HomeAssistantError:
                recipe = None

        if recipe is None:
            payload = await self._request(
                hass,
                "GET",
                "/api/recipes",
                params={"search": slug, "page": 1, "perPage": 5},
            )
            recipes = payload.get("items", payload if isinstance(payload, list) else [])
            recipe = next(
                (
                    item
                    for item in recipes
                    if _clean_text(item.get("name")).lower() == slug.lower()
                    or _clean_text(item.get("slug")).lower() == slug.lower()
                ),
                recipes[0] if recipes else None,
            )
            if not recipe:
                raise HomeAssistantError(f"No Mealie recipe matched {slug}")
            recipe = await self._request(
                hass, "GET", f"/api/recipes/{quote(recipe['slug'])}"
            )

        return {
            "success": True,
            "recipe": _recipe_details(recipe),
        }


class MealieAPI(llm.API):
    """Home Assistant LLM API backed by Mealie."""

    def __init__(
        self,
        hass: HomeAssistant,
        url: str,
        token: str,
        result_count: int,
        timeout: int,
    ) -> None:
        """Initialize the API."""
        super().__init__(hass=hass, id="mealie_recipes", name="Mealie Recipes")
        self._tools = [
            ImportRecipeUrlTool(url, token, timeout),
            FindRecipesTool(url, token, timeout, result_count),
            GetRecipeTool(url, token, timeout),
        ]

    async def async_get_api_instance(
        self, llm_context: llm.LLMContext
    ) -> llm.APIInstance:
        """Return the Mealie API instance."""
        return llm.APIInstance(
            api=self,
            api_prompt=(
                "Use Mealie as the source of truth for saved recipes. When a "
                "user asks to save a recipe, only import a specific URL after "
                "they have chosen it. When asked to read ingredients or method, "
                "prefer get_saved_recipe over repeating web-search text."
            ),
            llm_context=llm_context,
            tools=self._tools,
        )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the Mealie LLM API."""
    settings = config[DOMAIN]
    hass.data[DOMAIN] = llm.async_register_api(
        hass,
        MealieAPI(
            hass,
            settings[CONF_URL],
            settings[CONF_TOKEN],
            settings[CONF_RESULT_COUNT],
            settings[CONF_TIMEOUT],
        ),
    )
    return True
