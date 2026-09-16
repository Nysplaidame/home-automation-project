"""Expose GardenKeeper's deterministic voice contract as an LLM tool."""

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

DOMAIN = "gardenkeeper_llm"
CONF_SECRET = "secret"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_URL): cv.url,
                vol.Required(CONF_SECRET): cv.string,
                vol.Optional(CONF_TIMEOUT, default=30): vol.All(
                    vol.Coerce(int), vol.Range(min=3, max=60)
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


class GardenTaskTool(llm.Tool):
    """Query or update canonical GardenKeeper task state."""

    name = "garden_tasks"
    description = (
        "Use for operational garden questions and actions: tasks due, adding "
        "garden reminders, and completing garden tasks. Do not use for general "
        "gardening advice. Pass a confirmation_token only after the user chooses "
        "one of GardenKeeper's confirmation options."
    )
    parameters = vol.Schema(
        {
            vol.Required("transcript"): vol.All(
                cv.string, vol.Length(min=2, max=1000)
            ),
            vol.Optional("confirmation_token"): vol.All(
                cv.string, vol.Length(min=10, max=2000)
            ),
        }
    )

    def __init__(self, url: str, secret: str, timeout: int) -> None:
        self._url = url.rstrip("/")
        self._secret = secret
        self._timeout = timeout

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> JsonObjectType:
        args = self.parameters(tool_input.tool_args)
        body: dict[str, Any] = {
            "transcript": args["transcript"],
            "source": "home-assistant-llm",
            "actor": "home-assistant",
        }
        if args.get("confirmation_token"):
            body["confirmation_token"] = args["confirmation_token"]

        session = async_get_clientsession(hass)
        try:
            async with session.post(
                f"{self._url}/api/assistant/voice-command",
                headers={"X-GardenKeeper-Secret": self._secret},
                json=body,
                timeout=aiohttp.ClientTimeout(total=self._timeout),
            ) as response:
                response.raise_for_status()
                payload: dict[str, Any] = await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise HomeAssistantError(f"GardenKeeper request failed: {err}") from err

        return payload


class GardenKeeperAPI(llm.API):
    def __init__(self, hass: HomeAssistant, url: str, secret: str, timeout: int) -> None:
        super().__init__(hass=hass, id="gardenkeeper_ops", name="GardenKeeper")
        self._tool = GardenTaskTool(url, secret, timeout)

    async def async_get_api_instance(
        self, llm_context: llm.LLMContext
    ) -> llm.APIInstance:
        return llm.APIInstance(
            api=self,
            api_prompt=(
                "GardenKeeper is authoritative for plants and garden task state. "
                "Use garden_tasks for operational garden requests. Repeat its "
                "spoken_response naturally. When requires_confirmation is true, "
                "ask the user to choose an option and retain its confirmation_token."
            ),
            llm_context=llm_context,
            tools=[self._tool],
        )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    settings = config[DOMAIN]
    hass.data[DOMAIN] = llm.async_register_api(
        hass,
        GardenKeeperAPI(
            hass,
            settings[CONF_URL],
            settings[CONF_SECRET],
            settings[CONF_TIMEOUT],
        ),
    )
    return True
