"""Expose a local llama.cpp OpenAI-compatible server as a conversation agent."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Literal

import aiohttp
import voluptuous as vol
from voluptuous_openapi import convert

from homeassistant.components import conversation
from homeassistant.components.conversation.agent_manager import get_agent_manager
from homeassistant.components.conversation.const import DATA_COMPONENT
from homeassistant.const import (
    CONF_LLM_HASS_API,
    CONF_MODEL,
    CONF_NAME,
    CONF_PROMPT,
    CONF_TIMEOUT,
    CONF_URL,
    MATCH_ALL,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv, llm
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "llamacpp_conversation"

CONF_MAX_HISTORY = "max_history"
CONF_MAX_TOKENS = "max_tokens"
CONF_TEMPERATURE = "temperature"

DEFAULT_NAME = "Llama.cpp Conversation"
DEFAULT_TIMEOUT = 120
DEFAULT_MAX_HISTORY = 20
DEFAULT_MAX_TOKENS = 512
DEFAULT_TEMPERATURE = 0.2
MAX_TOOL_ITERATIONS = 10
RAW_TOOL_EXPLANATION_RE = re.compile(
    r"\b(json object|speech field|response_type|action_done|data field)\b",
    re.IGNORECASE,
)
DIRECT_RESPONSE_RE = re.compile(
    r"^\s*(reply|respond|say|repeat|read|tell me|answer)\s+"
    r"(exactly|verbatim|with|the following|this)?\b",
    re.IGNORECASE,
)
BULLET_RE = re.compile(r"^(\s*(?:[-*•]|\d+[.)])\s+)(\S.*?)(\s*)$")
TERMINAL_PUNCTUATION_RE = re.compile(r"[.!?][\"')\]]*$")

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_URL): cv.url,
                vol.Required(CONF_MODEL): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Optional(CONF_LLM_HASS_API): vol.Any(
                    cv.string, vol.All(cv.ensure_list, [cv.string])
                ),
                vol.Optional(CONF_PROMPT): cv.string,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.All(
                    vol.Coerce(int), vol.Range(min=10, max=300)
                ),
                vol.Optional(CONF_MAX_HISTORY, default=DEFAULT_MAX_HISTORY): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=100)
                ),
                vol.Optional(CONF_MAX_TOKENS, default=DEFAULT_MAX_TOKENS): vol.All(
                    vol.Coerce(int), vol.Range(min=64, max=4096)
                ),
                vol.Optional(CONF_TEMPERATURE, default=DEFAULT_TEMPERATURE): vol.All(
                    vol.Coerce(float), vol.Range(min=0.0, max=2.0)
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the llama.cpp conversation entity."""
    settings = config[DOMAIN]
    entity = LlamaCppConversationEntity(settings)
    hass.data[DOMAIN] = entity
    get_agent_manager(hass).async_set_agent(DOMAIN, entity)
    await hass.data[DATA_COMPONENT].async_add_entities([entity])
    return True


class LlamaCppConversationEntity(conversation.ConversationEntity):
    """Conversation agent backed by a local llama.cpp server endpoint."""

    _attr_supports_streaming = False

    def __init__(self, settings: dict[str, Any]) -> None:
        """Initialize the llama.cpp conversation entity."""
        self._settings = settings
        self._url = settings[CONF_URL].rstrip("/")
        self._model = settings[CONF_MODEL]
        self._attr_name = settings[CONF_NAME]
        self._attr_unique_id = DOMAIN
        if settings.get(CONF_LLM_HASS_API):
            self._attr_supported_features = (
                conversation.ConversationEntityFeature.CONTROL
            )

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return the languages this agent supports."""
        return MATCH_ALL

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        """Process a conversation turn through llama.cpp."""
        llm_hass_api = self._settings.get(CONF_LLM_HASS_API)
        if _is_direct_response_request(user_input.text):
            llm_hass_api = None

        try:
            await chat_log.async_provide_llm_data(
                user_input.as_llm_context(DOMAIN),
                llm_hass_api,
                self._settings.get(CONF_PROMPT),
                user_input.extra_system_prompt,
            )
        except conversation.ConverseError as err:
            return err.as_conversation_result()

        await self._async_handle_chat_log(user_input.agent_id, chat_log)
        return conversation.async_get_result_from_chat_log(user_input, chat_log)

    async def _async_handle_chat_log(
        self,
        agent_id: str,
        chat_log: conversation.ChatLog,
    ) -> None:
        """Send the chat log to llama.cpp and execute requested HA tools."""
        session = async_get_clientsession(self.hass)
        for _ in range(MAX_TOOL_ITERATIONS):
            messages = _trim_messages(
                [_content_to_openai_message(content) for content in chat_log.content],
                self._settings[CONF_MAX_HISTORY],
            )
            tools = _format_tools(chat_log.llm_api)
            response = await self._async_chat_completion(session, messages, tools)
            message = _extract_message(response)
            tool_inputs = _extract_tool_inputs(message)
            content = message.get("content")

            if tool_inputs:
                assistant_content = conversation.AssistantContent(
                    agent_id=agent_id,
                    content=content if isinstance(content, str) and content else None,
                    tool_calls=tool_inputs,
                    native=message,
                )
                async for _tool_result in chat_log.async_add_assistant_content(
                    assistant_content
                ):
                    pass
                continue

            if isinstance(content, str) and content.strip():
                response_text = _normalize_assistant_text(
                    _naturalize_tool_result_response(chat_log, content.strip())
                )
                chat_log.async_add_assistant_content_without_tools(
                    conversation.AssistantContent(
                        agent_id=agent_id,
                        content=response_text,
                        native=message,
                    )
                )
                return

            raise HomeAssistantError("llama.cpp returned no response content")

        raise HomeAssistantError("llama.cpp exceeded the Home Assistant tool loop limit")

    async def _async_chat_completion(
        self,
        session: aiohttp.ClientSession,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Call the local OpenAI-compatible llama.cpp chat completion endpoint."""
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "temperature": self._settings[CONF_TEMPERATURE],
            "max_tokens": self._settings[CONF_MAX_TOKENS],
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            async with session.post(
                f"{self._url}/chat/completions",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self._settings[CONF_TIMEOUT]),
            ) as response:
                response.raise_for_status()
                return await response.json(content_type=None)
        except aiohttp.ClientResponseError as err:
            raise HomeAssistantError(
                f"llama.cpp request failed: HTTP {err.status} {err.message}"
            ) from err
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise HomeAssistantError(f"llama.cpp request failed: {err!r}") from err


def _content_to_openai_message(
    content: conversation.Content,
) -> dict[str, Any]:
    """Convert Home Assistant chat content to OpenAI-compatible chat messages."""
    if content.role == "system":
        return {"role": "system", "content": content.content}

    if content.role == "user":
        if content.attachments:
            raise HomeAssistantError("llama.cpp conversation does not support attachments")
        return {"role": "user", "content": content.content}

    if content.role == "assistant":
        message: dict[str, Any] = {
            "role": "assistant",
            "content": content.content,
        }
        if content.tool_calls:
            message["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.tool_name,
                        "arguments": _json_dumps(tool_call.tool_args),
                    },
                }
                for tool_call in content.tool_calls
            ]
        return message

    if content.role == "tool_result":
        return {
            "role": "tool",
            "tool_call_id": content.tool_call_id,
            "name": content.tool_name,
            "content": _json_dumps(content.tool_result),
        }

    raise HomeAssistantError(f"Unsupported chat content role: {content.role}")


def _format_tools(
    llm_api: llm.APIInstance | None,
) -> list[dict[str, Any]]:
    """Convert Home Assistant LLM tools to OpenAI-compatible function tools."""
    if llm_api is None:
        return []

    tools = []
    for tool in llm_api.tools:
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": convert(
                        tool.parameters,
                        custom_serializer=llm_api.custom_serializer,
                    ),
                },
            }
        )
    return tools


def _extract_message(response: dict[str, Any]) -> dict[str, Any]:
    """Extract the first assistant message from a chat completion response."""
    try:
        message = response["choices"][0]["message"]
    except (KeyError, IndexError, TypeError) as err:
        raise HomeAssistantError("llama.cpp returned an invalid chat response") from err

    if not isinstance(message, dict):
        raise HomeAssistantError("llama.cpp returned an invalid assistant message")

    return message


def _extract_tool_inputs(message: dict[str, Any]) -> list[llm.ToolInput]:
    """Extract Home Assistant tool inputs from an OpenAI-compatible message."""
    tool_inputs = []
    for tool_call in message.get("tool_calls") or []:
        function = tool_call.get("function") or {}
        name = function.get("name")
        if not isinstance(name, str) or not name:
            continue

        arguments = function.get("arguments") or "{}"
        if isinstance(arguments, str):
            try:
                tool_args = json.loads(arguments)
            except json.JSONDecodeError as err:
                raise HomeAssistantError(
                    f"llama.cpp returned invalid tool arguments for {name}"
                ) from err
        elif isinstance(arguments, dict):
            tool_args = arguments
        else:
            raise HomeAssistantError(
                f"llama.cpp returned unsupported tool arguments for {name}"
            )

        call_id = tool_call.get("id")
        tool_input_kwargs: dict[str, Any] = {
            "tool_name": name,
            "tool_args": tool_args,
        }
        if isinstance(call_id, str) and call_id:
            tool_input_kwargs["id"] = call_id
        tool_inputs.append(llm.ToolInput(**tool_input_kwargs))

    return tool_inputs


def _trim_messages(
    messages: list[dict[str, Any]],
    max_history: int,
) -> list[dict[str, Any]]:
    """Keep the system prompt and the most recent chat history."""
    if len(messages) <= max_history + 1:
        return messages

    if messages and messages[0].get("role") == "system":
        return [messages[0], *messages[-max_history:]]

    return messages[-max_history:]


def _is_direct_response_request(text: str) -> bool:
    """Return true when the user is asking for speech/text, not HA control."""
    return bool(DIRECT_RESPONSE_RE.match(text))


def _naturalize_tool_result_response(
    chat_log: conversation.ChatLog,
    content: str,
) -> str:
    """Replace raw tool-result explanations with a spoken action summary."""
    if not RAW_TOOL_EXPLANATION_RE.search(content):
        return content

    tool_result = next(
        (
            item.tool_result
            for item in reversed(chat_log.content)
            if item.role == "tool_result"
        ),
        None,
    )
    if not isinstance(tool_result, dict):
        return content

    speech = _extract_tool_speech(tool_result)
    if speech:
        return speech

    if tool_result.get("response_type") == "action_done":
        data = tool_result.get("data")
        if isinstance(data, dict):
            failed = _extract_entity_names(data.get("failed"))
            if failed:
                return f"I tried, but {', '.join(failed)} failed."

            successful = _extract_entity_names(data.get("success"))
            if successful:
                return f"Done. {', '.join(successful)} succeeded."

        return "Done."

    return content


def _extract_tool_speech(tool_result: dict[str, Any]) -> str | None:
    """Extract a normal speech string from a Home Assistant tool result."""
    speech = tool_result.get("speech")
    if isinstance(speech, str) and speech.strip():
        return speech.strip()

    if not isinstance(speech, dict):
        return None

    plain = speech.get("plain")
    if isinstance(plain, dict):
        plain_speech = plain.get("speech")
        if isinstance(plain_speech, str) and plain_speech.strip():
            return plain_speech.strip()

    return None


def _extract_entity_names(value: Any) -> list[str]:
    """Extract friendly entity names from HA action result data."""
    if value is None:
        return []

    items = value if isinstance(value, list) else [value]
    names = []
    for item in items:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict):
            candidate = (
                item.get("name")
                or item.get("friendly_name")
                or item.get("entity_name")
                or item.get("entity_id")
            )
            if candidate:
                names.append(str(candidate))

    return names


def _normalize_assistant_text(content: str) -> str:
    """Normalize response text for speech readability."""
    lines = content.splitlines()
    normalized = []
    for line in lines:
        normalized.append(_normalize_bullet_line(line))
    return "\n".join(normalized).strip()


def _normalize_bullet_line(line: str) -> str:
    """Ensure bullet list items end with a full stop for TTS pause cues."""
    match = BULLET_RE.match(line)
    if match is None:
        return line

    prefix, body, suffix = match.groups()
    body = body.rstrip()
    if TERMINAL_PUNCTUATION_RE.search(body):
        return f"{prefix}{body}{suffix}"

    body = body.rstrip(",;:")
    return f"{prefix}{body}.{suffix}"


def _json_dumps(value: Any) -> str:
    """Serialize compact JSON for OpenAI-compatible tool arguments/results."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
