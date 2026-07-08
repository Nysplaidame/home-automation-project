"""Expose Grocy household actions as Home Assistant LLM tools."""

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

DOMAIN = "grocy_llm"
CONF_API_KEY = "api_key"
CONF_DEFAULT_LOCATION_ID = "default_location_id"
CONF_DEFAULT_QUANTITY_UNIT_ID = "default_quantity_unit_id"
CONF_DEFAULT_PRODUCT_GROUP_ID = "default_product_group_id"
CONF_DEFAULT_SHOPPING_LIST_ID = "default_shopping_list_id"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_URL): cv.url,
                vol.Required(CONF_API_KEY): cv.string,
                vol.Optional(CONF_DEFAULT_LOCATION_ID, default=3): vol.All(
                    vol.Coerce(int), vol.Range(min=1)
                ),
                vol.Optional(CONF_DEFAULT_QUANTITY_UNIT_ID, default=4): vol.All(
                    vol.Coerce(int), vol.Range(min=1)
                ),
                vol.Optional(CONF_DEFAULT_PRODUCT_GROUP_ID, default=5): vol.All(
                    vol.Coerce(int), vol.Range(min=1)
                ),
                vol.Optional(CONF_DEFAULT_SHOPPING_LIST_ID, default=1): vol.All(
                    vol.Coerce(int), vol.Range(min=1)
                ),
                vol.Optional(CONF_TIMEOUT, default=30): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=120)
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def _clean_text(value: Any, limit: int = 200) -> str:
    """Return a bounded plain string."""
    return str(value or "").strip()[:limit]


class GrocyTool(llm.Tool):
    """Base class for Grocy tools."""

    def __init__(
        self,
        url: str,
        api_key: str,
        timeout: int,
        default_location_id: int,
        default_quantity_unit_id: int,
        default_product_group_id: int,
        default_shopping_list_id: int,
    ) -> None:
        """Initialize the Grocy API client bits."""
        self._url = url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._default_location_id = default_location_id
        self._default_quantity_unit_id = default_quantity_unit_id
        self._default_product_group_id = default_product_group_id
        self._default_shopping_list_id = default_shopping_list_id

    async def _request(
        self,
        hass: HomeAssistant,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """Run an authenticated Grocy request."""
        session = async_get_clientsession(hass)
        headers = kwargs.pop("headers", {})
        headers["GROCY-API-KEY"] = self._api_key

        try:
            async with session.request(
                method,
                f"{self._url}{path}",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self._timeout),
                **kwargs,
            ) as response:
                response.raise_for_status()
                if response.status == 204:
                    return None
                return await response.json(content_type=None)
        except aiohttp.ClientResponseError as err:
            raise HomeAssistantError(
                f"Grocy request failed: HTTP {err.status} {err.message}"
            ) from err
        except (aiohttp.ClientError, TimeoutError) as err:
            raise HomeAssistantError(f"Grocy request failed: {err!r}") from err

    async def _get_or_create_product(
        self, hass: HomeAssistant, item_name: str
    ) -> dict[str, Any]:
        """Return an existing product or create a simple one."""
        products = await self._request(hass, "GET", "/api/objects/products")
        normalized = item_name.casefold()
        for product in products or []:
            if _clean_text(product.get("name")).casefold() == normalized:
                return product

        created = await self._request(
            hass,
            "POST",
            "/api/objects/products",
            json={
                "name": item_name,
                "location_id": self._default_location_id,
                "qu_id_purchase": self._default_quantity_unit_id,
                "qu_id_stock": self._default_quantity_unit_id,
                "product_group_id": self._default_product_group_id,
            },
        )
        product_id = int(created["created_object_id"])
        return await self._request(hass, "GET", f"/api/objects/products/{product_id}")


class AddShoppingItemTool(GrocyTool):
    """Add an item to Grocy's shopping list."""

    name = "add_grocy_shopping_item"
    description = (
        "Add a non-sensitive household item to the Grocy shopping list. "
        "Use this for requests like 'add milk to the shopping list'. "
        "Do not use this for stock consumption/removal or destructive changes."
    )
    parameters = vol.Schema(
        {
            vol.Required("item", description="Shopping item name"): vol.All(
                cv.string, vol.Length(min=1, max=120)
            ),
            vol.Optional(
                "amount",
                default=1,
                description="Quantity to add, using the product's stock unit",
            ): vol.All(vol.Coerce(float), vol.Range(min=0.01, max=1000)),
            vol.Optional("note", default="", description="Optional short note"): vol.All(
                cv.string, vol.Length(max=200)
            ),
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> JsonObjectType:
        """Add an item to Grocy's default shopping list."""
        args = self.parameters(tool_input.tool_args)
        item_name = _clean_text(args["item"], 120)
        product = await self._get_or_create_product(hass, item_name)
        product_id = int(product["id"])

        await self._request(
            hass,
            "POST",
            "/api/stock/shoppinglist/add-product",
            json={
                "product_id": product_id,
                "list_id": self._default_shopping_list_id,
                "product_amount": args["amount"],
                "note": _clean_text(args["note"], 200),
            },
        )

        return {
            "success": True,
            "item": _clean_text(product.get("name"), 120),
            "amount": args["amount"],
            "shopping_list_id": self._default_shopping_list_id,
        }


class ListShoppingItemsTool(GrocyTool):
    """List current Grocy shopping-list items."""

    name = "list_grocy_shopping_list"
    description = "List current unchecked items on the Grocy shopping list."
    parameters = vol.Schema({})

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> JsonObjectType:
        """Return current shopping-list items."""
        items = await self._request(hass, "GET", "/api/objects/shopping_list")
        products = await self._request(hass, "GET", "/api/objects/products")
        product_names = {
            int(product["id"]): _clean_text(product.get("name"), 120)
            for product in products or []
        }

        active_items = []
        for item in items or []:
            if int(item.get("done") or 0) == 1:
                continue
            product_id = int(item["product_id"])
            active_items.append(
                {
                    "item": product_names.get(product_id, f"Product {product_id}"),
                    "amount": item.get("amount"),
                    "note": _clean_text(item.get("note"), 200),
                }
            )

        return {
            "success": True,
            "items": active_items,
        }


class GrocyAPI(llm.API):
    """Home Assistant LLM API backed by Grocy."""

    def __init__(
        self,
        hass: HomeAssistant,
        url: str,
        api_key: str,
        timeout: int,
        default_location_id: int,
        default_quantity_unit_id: int,
        default_product_group_id: int,
        default_shopping_list_id: int,
    ) -> None:
        """Initialize the API."""
        super().__init__(hass=hass, id="grocy_household", name="Grocy Household")
        args = (
            url,
            api_key,
            timeout,
            default_location_id,
            default_quantity_unit_id,
            default_product_group_id,
            default_shopping_list_id,
        )
        self._tools = [
            AddShoppingItemTool(*args),
            ListShoppingItemsTool(*args),
        ]

    async def async_get_api_instance(
        self, llm_context: llm.LLMContext
    ) -> llm.APIInstance:
        """Return the Grocy API instance."""
        return llm.APIInstance(
            api=self,
            api_prompt=(
                "Use Grocy for household inventory and shopping-list tasks. "
                "The available Grocy tools are intentionally limited to adding "
                "shopping-list items and reading the shopping list. Do not claim "
                "that stock was consumed, removed, purchased, or inventoried."
            ),
            llm_context=llm_context,
            tools=self._tools,
        )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the Grocy LLM API."""
    settings = config[DOMAIN]
    hass.data[DOMAIN] = llm.async_register_api(
        hass,
        GrocyAPI(
            hass,
            settings[CONF_URL],
            settings[CONF_API_KEY],
            settings[CONF_TIMEOUT],
            settings[CONF_DEFAULT_LOCATION_ID],
            settings[CONF_DEFAULT_QUANTITY_UNIT_ID],
            settings[CONF_DEFAULT_PRODUCT_GROUP_ID],
            settings[CONF_DEFAULT_SHOPPING_LIST_ID],
        ),
    )
    return True
