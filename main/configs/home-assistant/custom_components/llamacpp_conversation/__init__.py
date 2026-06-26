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
DEFAULT_MAX_HISTORY = 8
DEFAULT_MAX_TOKENS = 256
DEFAULT_TEMPERATURE = 0.1
MAX_TOOL_ITERATIONS = 10
RAW_TOOL_EXPLANATION_RE = re.compile(
    r"\b(json object|speech field|response_type|action_done|data field)\b",
    re.IGNORECASE,
)
EXACT_RESPONSE_RE = re.compile(
    r"^\s*(reply|respond|answer)\s+(exactly|verbatim)\b",
    re.IGNORECASE,
)
SAY_RESPONSE_RE = re.compile(
    r"^\s*(say|repeat|read)\b",
    re.IGNORECASE,
)
RECIPE_RE = re.compile(
    r"\b(recipe|recipes|ingredient|ingredients|step|steps|method|cook|cooking|"
    r"mealie|mealy|melee|lentil|soup|serving|servings)\b",
    re.IGNORECASE,
)
RECIPE_INGREDIENTS_RE = re.compile(
    r"\b(ingredient|ingredients|shopping|need)\b",
    re.IGNORECASE,
)
RECIPE_STEPS_RE = re.compile(
    r"\b(step|steps|method|instruction|instructions|make|cook|prepare)\b",
    re.IGNORECASE,
)
RECIPE_REPEAT_STEPS_RE = re.compile(
    r"\b(?:repeat|read|redo|re-?do|re-?dote)\b.*\b(?:all\s+)?steps?\b",
    re.IGNORECASE,
)
RECIPE_STEP_NUMBER_RE = re.compile(
    r"\bstep\s+(?P<number>one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b",
    re.IGNORECASE,
)
WEB_RE = re.compile(
    r"\b(search|web|internet|online|latest|news|current|look up|find me)\b",
    re.IGNORECASE,
)
ASSIST_RE = re.compile(
    r"\b(turn|switch|set|open|close|lock|unlock|start|stop|cancel|pause|resume|"
    r"increase|decrease|dim|brighten|fan|light|timer|scene|script|broadcast|"
    r"add .+ list|remove .+ list)\b",
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
        llm_hass_api = _select_llm_hass_api(
            user_input.text,
            self._settings.get(CONF_LLM_HASS_API),
        )
        _LOGGER.debug("Selected LLM API set for utterance: %s", llm_hass_api)

        try:
            await chat_log.async_provide_llm_data(
                user_input.as_llm_context(DOMAIN),
                llm_hass_api,
                self._settings.get(CONF_PROMPT),
                user_input.extra_system_prompt,
            )
        except conversation.ConverseError as err:
            return err.as_conversation_result()

        try:
            await self._async_handle_chat_log(
                user_input.agent_id,
                chat_log,
                user_input.text,
            )
        except HomeAssistantError as err:
            _LOGGER.warning("llama.cpp conversation failed: %s", err)
            chat_log.async_add_assistant_content_without_tools(
                conversation.AssistantContent(
                    agent_id=user_input.agent_id,
                    content=(
                        "I could not complete that request. The local assistant "
                        "hit an error before it could respond."
                    ),
                )
            )

        return conversation.async_get_result_from_chat_log(user_input, chat_log)

    async def _async_handle_chat_log(
        self,
        agent_id: str,
        chat_log: conversation.ChatLog,
        user_text: str,
    ) -> None:
        """Send the chat log to llama.cpp and execute requested HA tools."""
        direct_history_answer = _maybe_direct_recipe_history_answer(
            user_text,
            chat_log,
        )
        if direct_history_answer:
            chat_log.async_add_assistant_content_without_tools(
                conversation.AssistantContent(
                    agent_id=agent_id,
                    content=_normalize_assistant_text(direct_history_answer),
                    native={"source": "mealie_history_direct"},
                )
            )
            return

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
                    direct_answer = _maybe_direct_recipe_answer(user_text, _tool_result)
                    if direct_answer:
                        chat_log.async_add_assistant_content_without_tools(
                            conversation.AssistantContent(
                                agent_id=agent_id,
                                content=_normalize_assistant_text(direct_answer),
                                native={
                                    "source": "mealie_tool_direct",
                                    "tool_name": _tool_result.tool_name,
                                },
                            )
                        )
                        return
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


def _select_llm_hass_api(
    text: str,
    configured_apis: str | list[str] | None,
) -> str | list[str] | None:
    """Select the smallest useful tool set for the user's utterance."""
    configured = _configured_api_set(configured_apis)
    if not configured:
        return None

    if RECIPE_RE.search(text):
        return _selected_apis(configured, ["mealie_recipes"])

    if WEB_RE.search(text):
        return _selected_apis(configured, ["searxng_search"])

    if ASSIST_RE.search(text):
        return _selected_apis(configured, ["assist"])

    if _is_direct_response_request(text):
        return None

    return None


def _configured_api_set(configured_apis: str | list[str] | None) -> set[str]:
    """Return configured API ids as a set."""
    if configured_apis is None:
        return set()
    if isinstance(configured_apis, str):
        return {configured_apis}
    return set(configured_apis)


def _selected_apis(configured: set[str], candidates: list[str]) -> str | list[str] | None:
    """Return configured API ids from a candidate list."""
    selected = [api for api in candidates if api in configured]
    if not selected:
        return None
    if len(selected) == 1:
        return selected[0]
    return selected


def _is_direct_response_request(text: str) -> bool:
    """Return true when the user is asking for text, not tools."""
    return bool(EXACT_RESPONSE_RE.match(text) or SAY_RESPONSE_RE.match(text))


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


def _maybe_direct_recipe_answer(user_text: str, tool_result_content: Any) -> str | None:
    """Format Mealie recipe details directly instead of re-querying the LLM."""
    if getattr(tool_result_content, "role", None) != "tool_result":
        return None

    tool_name = getattr(tool_result_content, "tool_name", None)
    if not isinstance(tool_name, str) or "get_saved_recipe" not in tool_name:
        return None

    tool_result = getattr(tool_result_content, "tool_result", None)
    if not isinstance(tool_result, dict) or not tool_result.get("success"):
        return None

    recipe = tool_result.get("recipe")
    if not isinstance(recipe, dict):
        return None

    recipe_name = str(recipe.get("name") or "the recipe").strip() or "the recipe"
    if RECIPE_STEPS_RE.search(user_text):
        steps = _extract_recipe_steps(recipe)
        if steps:
            return f"The steps for {recipe_name} are:\n" + "\n".join(
                f"{index}. {step}" for index, step in enumerate(steps, start=1)
            )

    if RECIPE_INGREDIENTS_RE.search(user_text):
        ingredients = _extract_recipe_ingredients(recipe)
        if ingredients:
            return f"The ingredients for {recipe_name} are:\n" + "\n".join(
                f"- {ingredient}" for ingredient in ingredients
            )

    return None


def _maybe_direct_recipe_history_answer(
    user_text: str,
    chat_log: conversation.ChatLog,
) -> str | None:
    """Answer recipe follow-ups from the latest Mealie result in chat history."""
    recipe = _latest_recipe_from_history(chat_log)
    if recipe is None:
        return None

    recipe_name = str(recipe.get("name") or "the recipe").strip() or "the recipe"
    steps = _extract_recipe_steps(recipe)
    if not steps:
        return None

    step_number = _requested_step_number(user_text)
    if step_number is not None:
        if 1 <= step_number <= len(steps):
            return f"Step {step_number} for {recipe_name} is: {steps[step_number - 1]}"
        return f"{recipe_name} only has {len(steps)} steps."

    if RECIPE_REPEAT_STEPS_RE.search(user_text):
        return f"The steps for {recipe_name} are:\n" + "\n".join(
            f"{index}. {step}" for index, step in enumerate(steps, start=1)
        )

    return None


def _extract_recipe_steps(recipe: dict[str, Any]) -> list[str]:
    """Extract spoken recipe step text from a Mealie tool result."""
    steps = []
    for item in recipe.get("steps") or []:
        if isinstance(item, dict):
            candidate = item.get("text") or item.get("summary") or item.get("title")
        else:
            candidate = item
        text = str(candidate or "").strip()
        if text:
            steps.append(text)
    return steps


def _extract_recipe_ingredients(recipe: dict[str, Any]) -> list[str]:
    """Extract spoken ingredient text from a Mealie tool result."""
    ingredients = []
    for item in recipe.get("ingredients") or []:
        text = str(item or "").strip()
        if text:
            ingredients.append(text)
    return ingredients


def _latest_recipe_from_history(
    chat_log: conversation.ChatLog,
) -> dict[str, Any] | None:
    """Find the latest successful Mealie recipe result in the chat log."""
    for item in reversed(chat_log.content):
        if getattr(item, "role", None) != "tool_result":
            continue
        tool_name = getattr(item, "tool_name", None)
        if not isinstance(tool_name, str) or "get_saved_recipe" not in tool_name:
            continue
        tool_result = getattr(item, "tool_result", None)
        if not isinstance(tool_result, dict) or not tool_result.get("success"):
            continue
        recipe = tool_result.get("recipe")
        if isinstance(recipe, dict):
            return recipe
    return None


def _requested_step_number(user_text: str) -> int | None:
    """Return requested recipe step number, if present."""
    match = RECIPE_STEP_NUMBER_RE.search(user_text)
    if match is None:
        return None

    value = match.group("number").lower()
    words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }
    if value in words:
        return words[value]
    return int(value)


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
    content = _strip_wrapping_quotes(content.strip())
    lines = content.splitlines()
    normalized = []
    for line in lines:
        normalized.append(_normalize_bullet_line(line))
    return "\n".join(normalized).strip()


def _strip_wrapping_quotes(content: str) -> str:
    """Remove one pair of whole-response wrapping quotes."""
    if len(content) < 2:
        return content
    if content[0] == content[-1] and content[0] in {'"', "'"}:
        return content[1:-1].strip()
    return content


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
