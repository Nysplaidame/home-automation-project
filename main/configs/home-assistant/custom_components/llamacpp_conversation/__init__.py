"""Expose a local llama.cpp OpenAI-compatible server as a conversation agent."""

from __future__ import annotations

import json
import logging
import re
import time
from difflib import SequenceMatcher
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
ASSISTANT_STATE_RETENTION_SECONDS = 48 * 60 * 60
MAX_COMPACT_TRACE_ITEMS = 30
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
AFFIRMATIVE_RE = re.compile(
    r"^\s*(yes|yeah|yep|please|do that|go ahead|ok|okay|sure)\s*[.!?]?\s*$",
    re.IGNORECASE,
)
RAW_TOOL_CALL_RE = re.compile(
    r"(</tool_call>|\btool_call\b|^\s*\{\s*\"name\"\s*:\s*\"[^\"]+\")",
    re.IGNORECASE | re.DOTALL,
)
RECIPE_RE = re.compile(
    r"\b(recipe|recipes|ingredient|ingredients|step|steps|method|cook|cooking|"
    r"mealie|mealy|melee|lentil|soup|serving|servings)\b",
    re.IGNORECASE,
)
RECIPE_INGREDIENTS_RE = re.compile(
    r"\b(ingredient|ingredients|shopping|need|how much|how many|quantity|amount)\b",
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
ACTIVE_RECIPE_REF_RE = re.compile(
    r"\b(this|that|the|current|saved|active)\s+recipe\b|\bit\b",
    re.IGNORECASE,
)
QUANTITY_STOPWORDS = {
    "how",
    "much",
    "many",
    "do",
    "i",
    "we",
    "you",
    "need",
    "for",
    "the",
    "this",
    "that",
    "recipe",
    "chicken",
    "and",
    "of",
    "a",
    "an",
    "is",
}
RECIPE_IMPORT_RE = re.compile(
    r"(?:\b(send|save|add|import)\b.*\b(recipe|mealie|mealy|melee|merely)\b|"
    r"\brecipe\b.*\b(mealie|mealy|melee|merely)\b)",
    re.IGNORECASE,
)
ORDINAL_RE = re.compile(
    r"\b(?P<ordinal>first|second|third|1st|2nd|3rd|one|two|three)\b",
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
        self._assistant_state: dict[str, Any] = {
            "created_at": time.time(),
            "updated_at": time.time(),
            "trace": [],
        }
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
            chat_log,
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
        self._prune_assistant_state()

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
            self._remember_trace("direct_recipe_history", user_text)
            return

        direct_import_done = await self._async_maybe_direct_recipe_import(
            agent_id,
            user_text,
            chat_log,
        )
        if direct_import_done:
            return

        direct_web_answer = _maybe_direct_web_recipe_followup_answer(
            user_text,
            chat_log,
        )
        if direct_web_answer:
            chat_log.async_add_assistant_content_without_tools(
                conversation.AssistantContent(
                    agent_id=agent_id,
                    content=_normalize_assistant_text(direct_web_answer),
                    native={"source": "web_search_history_direct"},
                )
            )
            self._remember_trace("direct_web_history", user_text)
            return

        session = async_get_clientsession(self.hass)
        for _ in range(MAX_TOOL_ITERATIONS):
            messages = _trim_messages(
                [_content_to_openai_message(content) for content in chat_log.content],
                self._settings[CONF_MAX_HISTORY],
                self._assistant_state,
            )
            tools = _format_tools(chat_log.llm_api)
            response = await self._async_chat_completion(
                session,
                messages,
                tools,
                _max_tokens_for_turn(user_text, tools, self._settings[CONF_MAX_TOKENS]),
            )
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
                    tool_error = _tool_error_response(_tool_result)
                    if tool_error:
                        chat_log.async_add_assistant_content_without_tools(
                            conversation.AssistantContent(
                                agent_id=agent_id,
                                content=tool_error,
                                native={
                                    "source": "tool_error_direct",
                                    "tool_name": getattr(_tool_result, "tool_name", None),
                                },
                            )
                        )
                        return

                    web_answer = _maybe_direct_web_search_answer(_tool_result)
                    if web_answer:
                        self._remember_web_search(_tool_result)
                        chat_log.async_add_assistant_content_without_tools(
                            conversation.AssistantContent(
                                agent_id=agent_id,
                                content=_normalize_assistant_text(web_answer),
                                native={
                                    "source": "web_search_tool_direct",
                                    "tool_name": getattr(_tool_result, "tool_name", None),
                                },
                            )
                        )
                        return

                    direct_answer = _maybe_direct_recipe_answer(user_text, _tool_result)
                    if direct_answer:
                        self._remember_recipe_tool_result(_tool_result)
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

                    action_answer = _maybe_direct_action_done(_tool_result)
                    if action_answer:
                        chat_log.async_add_assistant_content_without_tools(
                            conversation.AssistantContent(
                                agent_id=agent_id,
                                content=_normalize_assistant_text(action_answer),
                                native={
                                    "source": "action_tool_direct",
                                    "tool_name": getattr(_tool_result, "tool_name", None),
                                },
                            )
                        )
                        self._remember_trace("direct_action_done", user_text)
                        return
                continue

            if isinstance(content, str) and content.strip():
                if _looks_like_raw_tool_call(content):
                    _LOGGER.warning(
                        "llama.cpp returned a raw tool call as assistant text; "
                        "suppressing it from speech"
                    )
                    chat_log.async_add_assistant_content_without_tools(
                        conversation.AssistantContent(
                            agent_id=agent_id,
                            content=(
                                "I tried to use a tool that was not available for "
                                "that turn. Please repeat the action you want me to take."
                            ),
                            native={"source": "raw_tool_call_suppressed", **message},
                        )
                    )
                    return

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
                self._remember_trace("llm_response", user_text)
                return

            raise HomeAssistantError("llama.cpp returned no response content")

        raise HomeAssistantError("llama.cpp exceeded the Home Assistant tool loop limit")

    async def _async_chat_completion(
        self,
        session: aiohttp.ClientSession,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_tokens: int,
    ) -> dict[str, Any]:
        """Call the local OpenAI-compatible llama.cpp chat completion endpoint."""
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "temperature": self._settings[CONF_TEMPERATURE],
            "max_tokens": max_tokens,
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

    async def _async_maybe_direct_recipe_import(
        self,
        agent_id: str,
        user_text: str,
        chat_log: conversation.ChatLog,
    ) -> bool:
        """Import a selected web recipe and optionally read details immediately."""
        if not RECIPE_IMPORT_RE.search(user_text):
            return False

        result = _select_web_recipe_result(user_text, chat_log)
        if result is None:
            return False

        url = result.get("url")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            return False

        title = str(result.get("title") or "that recipe").strip() or "that recipe"
        tool_input = llm.ToolInput(
            tool_name="import_recipe_url",
            tool_args={
                "url": url,
                "include_tags": True,
                "include_categories": True,
            },
        )
        assistant_content = conversation.AssistantContent(
            agent_id=agent_id,
            content=None,
            tool_calls=[tool_input],
            native={"source": "web_result_direct_import", "title": title, "url": url},
        )

        async for tool_result_content in chat_log.async_add_assistant_content(
            assistant_content
        ):
            tool_result = getattr(tool_result_content, "tool_result", None)
            if isinstance(tool_result, dict) and tool_result.get("success"):
                recipe = tool_result.get("recipe")
                imported_name = title
                slug = None
                if isinstance(recipe, dict):
                    imported_name = str(recipe.get("name") or title)
                    slug = recipe.get("slug")
                    self._remember_recipe_summary(recipe, source="import_recipe_url")

                detail_answer = await self._async_maybe_read_imported_recipe(
                    agent_id,
                    user_text,
                    chat_log,
                    slug,
                )
                if detail_answer:
                    chat_log.async_add_assistant_content_without_tools(
                        conversation.AssistantContent(
                            agent_id=agent_id,
                            content=_normalize_assistant_text(
                                f"Saved {imported_name} to Mealie. {detail_answer}"
                            ),
                            native={
                                "source": "web_result_direct_import_then_read",
                                "tool_name": getattr(tool_result_content, "tool_name", None),
                            },
                        )
                    )
                    self._remember_trace("direct_import_then_read", user_text)
                    return True

                chat_log.async_add_assistant_content_without_tools(
                    conversation.AssistantContent(
                        agent_id=agent_id,
                        content=f"Saved {imported_name} to Mealie.",
                        native={
                            "source": "web_result_direct_import",
                            "tool_name": getattr(tool_result_content, "tool_name", None),
                        },
                    )
                )
                self._remember_trace("direct_import", user_text)
                return True

            chat_log.async_add_assistant_content_without_tools(
                conversation.AssistantContent(
                    agent_id=agent_id,
                    content=(
                        f"I tried to save {title} to Mealie, but the import failed. "
                        "Mealie could not import that page automatically."
                    ),
                    native={
                        "source": "web_result_direct_import_failed",
                        "tool_name": getattr(tool_result_content, "tool_name", None),
                    },
                )
            )
            self._remember_trace("direct_import_failed", user_text)
            return True

        return False

    async def _async_maybe_read_imported_recipe(
        self,
        agent_id: str,
        user_text: str,
        chat_log: conversation.ChatLog,
        slug: Any,
    ) -> str | None:
        """Fetch the imported recipe when the same utterance asks to read it."""
        if not isinstance(slug, str) or not slug:
            return None
        if not (RECIPE_INGREDIENTS_RE.search(user_text) or RECIPE_STEPS_RE.search(user_text)):
            return None

        tool_input = llm.ToolInput(
            tool_name="get_saved_recipe",
            tool_args={"slug": slug},
        )
        assistant_content = conversation.AssistantContent(
            agent_id=agent_id,
            content=None,
            tool_calls=[tool_input],
            native={"source": "imported_recipe_direct_read", "slug": slug},
        )
        async for tool_result_content in chat_log.async_add_assistant_content(
            assistant_content
        ):
            self._remember_recipe_tool_result(tool_result_content)
            return _maybe_direct_recipe_answer(user_text, tool_result_content)
        return None

    def _remember_web_search(self, tool_result_content: Any) -> None:
        """Remember compact web results for short-lived follow-up routing."""
        tool_result = getattr(tool_result_content, "tool_result", None)
        if not isinstance(tool_result, dict):
            return
        results = tool_result.get("results")
        if not isinstance(results, list):
            return
        self._assistant_state["last_web_results"] = [
            _compact_web_result(result)
            for result in results
            if isinstance(result, dict)
        ][:5]
        self._touch_assistant_state()

    def _remember_recipe_tool_result(self, tool_result_content: Any) -> None:
        """Remember the latest full recipe returned by Mealie."""
        tool_result = getattr(tool_result_content, "tool_result", None)
        if not isinstance(tool_result, dict):
            return
        recipe = tool_result.get("recipe")
        if isinstance(recipe, dict):
            self._remember_recipe_summary(recipe, source="get_saved_recipe")
            self._assistant_state["active_recipe_details"] = _compact_recipe_details(recipe)
            self._touch_assistant_state()

    def _remember_recipe_summary(self, recipe: dict[str, Any], source: str) -> None:
        """Remember the active recipe identity without storing large blobs."""
        self._assistant_state["active_recipe"] = {
            "name": str(recipe.get("name") or "").strip(),
            "slug": str(recipe.get("slug") or "").strip(),
            "source": source,
            "updated_at": time.time(),
        }
        self._touch_assistant_state()

    def _remember_trace(self, event: str, user_text: str) -> None:
        """Keep a compact 48-hour trace for routing and debugging."""
        trace = self._assistant_state.setdefault("trace", [])
        if not isinstance(trace, list):
            trace = []
            self._assistant_state["trace"] = trace
        trace.append(
            {
                "ts": time.time(),
                "event": event,
                "user": str(user_text or "")[:220],
            }
        )
        self._assistant_state["trace"] = trace[-MAX_COMPACT_TRACE_ITEMS:]
        self._touch_assistant_state()

    def _touch_assistant_state(self) -> None:
        """Update assistant state timestamp."""
        self._assistant_state["updated_at"] = time.time()

    def _prune_assistant_state(self) -> None:
        """Expire retained state after the configured 48-hour window."""
        now = time.time()
        updated_at = float(self._assistant_state.get("updated_at") or 0)
        if now - updated_at > ASSISTANT_STATE_RETENTION_SECONDS:
            self._assistant_state = {
                "created_at": now,
                "updated_at": now,
                "trace": [],
            }
            return

        trace = self._assistant_state.get("trace")
        if isinstance(trace, list):
            self._assistant_state["trace"] = [
                item
                for item in trace
                if isinstance(item, dict)
                and now - float(item.get("ts") or 0) <= ASSISTANT_STATE_RETENTION_SECONDS
            ][-MAX_COMPACT_TRACE_ITEMS:]


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
            "content": _json_dumps(
                _compact_tool_result_for_prompt(content.tool_name, content.tool_result)
            ),
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
    assistant_state: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Keep the system prompt and the most recent chat history."""
    messages = _inject_assistant_state_context(messages, assistant_state)
    if len(messages) <= max_history + 1:
        return messages

    if messages and messages[0].get("role") == "system":
        if len(messages) > 1 and messages[1].get("role") == "system":
            return [messages[0], messages[1], *messages[-max_history:]]
        return [messages[0], *messages[-max_history:]]

    return messages[-max_history:]


def _inject_assistant_state_context(
    messages: list[dict[str, Any]],
    assistant_state: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Add a compact structured state hint without consuming large context."""
    if not assistant_state:
        return messages

    context = _assistant_state_prompt(assistant_state)
    if not context:
        return messages

    state_message = {
        "role": "system",
        "content": context,
    }
    if messages and messages[0].get("role") == "system":
        return [messages[0], state_message, *messages[1:]]
    return [state_message, *messages]


def _assistant_state_prompt(assistant_state: dict[str, Any]) -> str:
    """Return a short state summary for the model."""
    lines = [
        "Short-lived assistant state is available for resolving follow-ups. "
        "Use it only when relevant; do not mention it."
    ]
    active_recipe = assistant_state.get("active_recipe")
    if isinstance(active_recipe, dict):
        name = str(active_recipe.get("name") or "").strip()
        slug = str(active_recipe.get("slug") or "").strip()
        if name or slug:
            lines.append(f"Active recipe: {name or slug}.")
            if slug:
                lines.append(f"Active recipe slug: {slug}.")

    details = assistant_state.get("active_recipe_details")
    if isinstance(details, dict):
        ingredients = details.get("ingredients")
        if isinstance(ingredients, list) and ingredients:
            lines.append(
                "Active recipe ingredients: "
                + "; ".join(str(item) for item in ingredients[:12])
                + "."
            )
        steps = details.get("steps")
        if isinstance(steps, list) and steps:
            lines.append(f"Active recipe has {len(steps)} steps.")

    web_results = assistant_state.get("last_web_results")
    if isinstance(web_results, list) and web_results:
        result_lines = []
        for index, result in enumerate(web_results[:3], start=1):
            if not isinstance(result, dict):
                continue
            title = str(result.get("title") or "").strip()
            url = str(result.get("url") or "").strip()
            if title or url:
                result_lines.append(f"{index}. {title or url}")
        if result_lines:
            lines.append("Recent web results: " + " | ".join(result_lines) + ".")

    return "\n".join(lines)


def _compact_tool_result_for_prompt(tool_name: Any, tool_result: Any) -> Any:
    """Keep LLM prompt tool history small while preserving useful semantics."""
    if not isinstance(tool_result, dict):
        return tool_result

    name = str(tool_name or "")
    if "web_search" in name:
        compact = {
            "success": tool_result.get("success"),
            "query": tool_result.get("query"),
        }
        results = tool_result.get("results")
        if isinstance(results, list):
            compact["results"] = [
                _compact_web_result(result)
                for result in results
                if isinstance(result, dict)
            ][:3]
        return compact

    if "get_saved_recipe" in name:
        compact = {"success": tool_result.get("success")}
        recipe = tool_result.get("recipe")
        if isinstance(recipe, dict):
            compact["recipe"] = _compact_recipe_details(recipe)
        return compact

    if "import_recipe_url" in name:
        compact = {"success": tool_result.get("success")}
        recipe = tool_result.get("recipe")
        if isinstance(recipe, dict):
            compact["recipe"] = {
                "name": recipe.get("name"),
                "slug": recipe.get("slug"),
            }
        return compact

    if "grocy" in name or "shopping" in name.lower():
        return _compact_shopping_result(tool_result)

    response_type = tool_result.get("response_type")
    if response_type == "action_done":
        return {
            "success": True,
            "response_type": response_type,
            "speech": _extract_tool_speech(tool_result),
        }

    return tool_result


def _select_llm_hass_api(
    text: str,
    configured_apis: str | list[str] | None,
    chat_log: conversation.ChatLog | None = None,
) -> str | list[str] | None:
    """Select the smallest useful tool set for the user's utterance."""
    configured = _configured_api_set(configured_apis)
    if not configured:
        return None

    if _is_web_search_affirmation(text, chat_log):
        return _selected_apis(configured, ["searxng_search"])

    wants_recipe = bool(RECIPE_RE.search(text))
    wants_web = bool(WEB_RE.search(text))

    if wants_recipe and wants_web:
        return _selected_apis(configured, ["searxng_search", "mealie_recipes"])

    if wants_recipe:
        return _selected_apis(configured, ["mealie_recipes"])

    if wants_web:
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


def _is_web_search_affirmation(
    text: str,
    chat_log: conversation.ChatLog | None,
) -> bool:
    """Return true when the user accepts the assistant's web-search offer."""
    if chat_log is None or not AFFIRMATIVE_RE.match(text):
        return False

    for item in reversed(chat_log.content):
        if getattr(item, "role", None) != "assistant":
            continue
        content = getattr(item, "content", None)
        if not isinstance(content, str):
            return False
        return bool(re.search(r"\bsearch (?:the )?web\b", content, re.IGNORECASE))

    return False


def _looks_like_raw_tool_call(content: str) -> bool:
    """Return true when a model emitted tool-call markup as plain speech."""
    return bool(RAW_TOOL_CALL_RE.search(content))


def _tool_error_response(tool_result_content: Any) -> str | None:
    """Return a spoken-safe response for tool failures."""
    if getattr(tool_result_content, "role", None) != "tool_result":
        return None

    tool_result = getattr(tool_result_content, "tool_result", None)
    if not isinstance(tool_result, dict) or not tool_result.get("error"):
        return None

    tool_name = str(getattr(tool_result_content, "tool_name", "") or "")
    error_text = str(tool_result.get("error_text") or tool_result.get("error") or "")
    is_timeout = "TimeoutError" in error_text or "timed out" in error_text.lower()

    if "find_saved_recipes" in tool_name:
        if is_timeout:
            return (
                "Mealie timed out while searching saved recipes. "
                "I can search the web instead."
            )
        return "Mealie could not search saved recipes right now."

    if "web_search" in tool_name:
        if is_timeout:
            return "Web search timed out. Please try again in a moment."
        return "Web search failed before I could use the results."

    if is_timeout:
        return "That tool timed out before I could finish."

    return None


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


def _maybe_direct_action_done(tool_result_content: Any) -> str | None:
    """Return fast spoken responses for simple successful actions."""
    if getattr(tool_result_content, "role", None) != "tool_result":
        return None

    tool_name = str(getattr(tool_result_content, "tool_name", "") or "")
    tool_result = getattr(tool_result_content, "tool_result", None)
    if not isinstance(tool_result, dict) or not tool_result.get("success"):
        if isinstance(tool_result, dict) and tool_result.get("response_type") == "action_done":
            speech = _extract_tool_speech(tool_result)
            return speech or "Done."
        return None

    if "add_grocy_shopping_item" in tool_name:
        item = str(tool_result.get("item") or "that item").strip()
        amount = tool_result.get("amount")
        if amount in (None, "", 1, 1.0):
            return f"Done, added {item} to the shopping list."
        return f"Done, added {_format_amount(amount)} {item} to the shopping list."

    if "list_grocy_shopping_list" in tool_name:
        items = tool_result.get("items")
        if not isinstance(items, list) or not items:
            return "The shopping list is empty."
        names = []
        for item in items[:12]:
            if isinstance(item, dict):
                name = str(item.get("item") or "").strip()
                if name:
                    names.append(name)
        if names:
            return "The shopping list has: " + ", ".join(names) + "."

    if tool_result.get("response_type") == "action_done":
        speech = _extract_tool_speech(tool_result)
        if speech:
            return speech

        data = tool_result.get("data")
        if isinstance(data, dict):
            failed = _extract_entity_names(data.get("failed"))
            if failed:
                return f"I tried, but {', '.join(failed)} failed."

            successful = _extract_entity_names(data.get("success"))
            if successful:
                return f"Done. {', '.join(successful)} succeeded."

        return "Done."

    return None


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
    ingredient_answer = _maybe_direct_ingredient_quantity_answer(user_text, recipe)
    if ingredient_answer:
        return ingredient_answer

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
    ingredient_answer = _maybe_direct_ingredient_quantity_answer(user_text, recipe)
    if ingredient_answer:
        return ingredient_answer

    if RECIPE_INGREDIENTS_RE.search(user_text):
        ingredients = _extract_recipe_ingredients(recipe)
        if ingredients:
            return f"The ingredients for {recipe_name} are:\n" + "\n".join(
                f"- {ingredient}" for ingredient in ingredients
            )

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


def _maybe_direct_ingredient_quantity_answer(
    user_text: str,
    recipe: dict[str, Any],
) -> str | None:
    """Answer quantity follow-ups from active recipe ingredients."""
    if not RECIPE_INGREDIENTS_RE.search(user_text):
        return None

    ingredients = _extract_recipe_ingredients(recipe)
    if not ingredients:
        return None

    if re.search(r"\b(all|list|read|what(?:'s| is)? in)\b", user_text, re.IGNORECASE):
        return None

    requested = _ingredient_query_terms(user_text)
    if not requested:
        return None

    match = _best_ingredient_match(requested, ingredients)
    if match is None:
        return None

    recipe_name = str(recipe.get("name") or "the recipe").strip() or "the recipe"
    return f"For {recipe_name}, {match}."


def _ingredient_query_terms(user_text: str) -> list[str]:
    """Extract likely ingredient words from a quantity question."""
    words = re.findall(r"[a-zA-Z][a-zA-Z'-]+", user_text.lower())
    return [
        word.strip("'-")
        for word in words
        if word not in QUANTITY_STOPWORDS and len(word.strip("'-")) >= 3
    ]


def _best_ingredient_match(
    requested_terms: list[str],
    ingredients: list[str],
) -> str | None:
    """Fuzzily match STT-noisy ingredient terms to recipe ingredient text."""
    best_score = 0.0
    best_ingredient = None
    for ingredient in ingredients:
        ingredient_words = [
            word
            for word in re.findall(r"[a-zA-Z][a-zA-Z'-]+", ingredient.lower())
            if len(word) >= 3
        ]
        if not ingredient_words:
            continue
        score = 0.0
        for requested in requested_terms:
            for candidate in ingredient_words:
                if requested == candidate:
                    score = max(score, 1.0)
                elif requested in candidate or candidate in requested:
                    score = max(score, 0.88)
                else:
                    score = max(score, SequenceMatcher(None, requested, candidate).ratio())
        if score > best_score:
            best_score = score
            best_ingredient = ingredient

    if best_score >= 0.72:
        return best_ingredient
    return None


def _maybe_direct_web_search_answer(tool_result_content: Any) -> str | None:
    """Format web-search results directly for fast voice playback."""
    if getattr(tool_result_content, "role", None) != "tool_result":
        return None

    tool_name = getattr(tool_result_content, "tool_name", None)
    if not isinstance(tool_name, str) or "web_search" not in tool_name:
        return None

    tool_result = getattr(tool_result_content, "tool_result", None)
    if not isinstance(tool_result, dict) or not tool_result.get("success"):
        return None

    results = tool_result.get("results")
    if not isinstance(results, list) or not results:
        return None

    lines = ["I found these options:"]
    for index, result in enumerate(results[:3], start=1):
        if not isinstance(result, dict):
            continue
        title = _clean_spoken_title(result.get("title"))
        snippet = _clean_spoken_snippet(result.get("snippet"))
        if title and snippet:
            lines.append(f"{index}. {title}. {snippet}")
        elif title:
            lines.append(f"{index}. {title}.")

    if len(lines) == 1:
        return None

    lines.append("Say which one you want to save or inspect.")
    return "\n".join(lines)


def _maybe_direct_web_recipe_followup_answer(
    user_text: str,
    chat_log: conversation.ChatLog,
) -> str | None:
    """Answer web-result detail follow-ups without drifting into saved recipes."""
    if not (RECIPE_INGREDIENTS_RE.search(user_text) or RECIPE_STEPS_RE.search(user_text)):
        return None

    result = _select_web_recipe_result(user_text, chat_log)
    if result is None:
        return None

    title = _clean_spoken_title(result.get("title")) or "that web recipe"
    snippet = _clean_spoken_snippet(result.get("snippet"))
    if RECIPE_INGREDIENTS_RE.search(user_text):
        return (
            f"I only have the web-search summary for {title}, not the full "
            "ingredient list. Save it to Mealie first, or ask me to open the "
            f"recipe page. The summary says: {snippet}"
        )

    return (
        f"I only have the web-search summary for {title}, not the full method. "
        "Save it to Mealie first, or ask me to open the recipe page."
    )


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


def _select_web_recipe_result(
    user_text: str,
    chat_log: conversation.ChatLog,
) -> dict[str, Any] | None:
    """Select a recipe from the latest web search results."""
    results = _latest_web_search_results(chat_log)
    if not results:
        return None

    ordinal_index = _requested_ordinal_index(user_text)
    if ordinal_index is not None and ordinal_index < len(results):
        return results[ordinal_index]

    lowered = user_text.lower()
    if "bbc" in lowered:
        return _first_result_matching(results, "bbc")
    if "modern" in lowered:
        return _first_result_matching(results, "modern")
    if "pardon" in lowered or "french" in lowered:
        return _first_result_matching(results, "pardon", "french")

    if "this recipe" in lowered or "that recipe" in lowered:
        return results[0]

    return None


def _latest_web_search_results(chat_log: conversation.ChatLog) -> list[dict[str, Any]]:
    """Find the latest successful web-search result list in chat history."""
    for item in reversed(chat_log.content):
        if getattr(item, "role", None) != "tool_result":
            continue
        tool_name = getattr(item, "tool_name", None)
        if not isinstance(tool_name, str) or "web_search" not in tool_name:
            continue
        tool_result = getattr(item, "tool_result", None)
        if not isinstance(tool_result, dict) or not tool_result.get("success"):
            continue
        results = tool_result.get("results")
        if isinstance(results, list):
            return [result for result in results if isinstance(result, dict)]
    return []


def _requested_ordinal_index(user_text: str) -> int | None:
    """Return requested zero-based ordinal index, if present."""
    match = ORDINAL_RE.search(user_text)
    if match is None:
        return None

    value = match.group("ordinal").lower()
    ordinals = {
        "first": 0,
        "1st": 0,
        "one": 0,
        "second": 1,
        "2nd": 1,
        "two": 1,
        "third": 2,
        "3rd": 2,
        "three": 2,
    }
    return ordinals[value]


def _first_result_matching(
    results: list[dict[str, Any]],
    *needles: str,
) -> dict[str, Any] | None:
    """Return the first result whose title or URL contains any needle."""
    for result in results:
        haystack = f"{result.get('title', '')} {result.get('url', '')}".lower()
        if any(needle in haystack for needle in needles):
            return result
    return None


def _clean_spoken_title(value: Any) -> str:
    """Return a concise title for spoken search results."""
    title = str(value or "").strip()
    title = re.sub(r"\s+", " ", title)
    return title[:120]


def _clean_spoken_snippet(value: Any) -> str:
    """Return the first useful sentence from a web-search snippet."""
    snippet = str(value or "").strip()
    snippet = re.sub(r"\s+", " ", snippet)
    snippet = re.sub(r"\s*\d+(?:\.\d+)?\s*[\u200b ]*\([^)]+\).*$", "", snippet)
    for separator in (". ", "! ", "? "):
        if separator in snippet:
            snippet = snippet.split(separator, 1)[0] + separator.strip()
            break
    return snippet[:220]


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


def _max_tokens_for_turn(
    user_text: str,
    tools: list[dict[str, Any]],
    configured_max_tokens: int,
) -> int:
    """Use smaller voice budgets unless the turn clearly needs more text."""
    if RECIPE_REPEAT_STEPS_RE.search(user_text):
        return min(configured_max_tokens, 256)
    if RECIPE_STEPS_RE.search(user_text) or RECIPE_INGREDIENTS_RE.search(user_text):
        return min(configured_max_tokens, 192)
    if tools:
        return min(configured_max_tokens, 128)
    if ASSIST_RE.search(user_text):
        return min(configured_max_tokens, 96)
    return min(configured_max_tokens, 160)


def _compact_web_result(result: dict[str, Any]) -> dict[str, Any]:
    """Return compact web result state safe for short-lived retention."""
    return {
        "title": _clean_spoken_title(result.get("title")),
        "url": str(result.get("url") or "")[:500],
        "snippet": _clean_spoken_snippet(result.get("snippet")),
    }


def _compact_recipe_details(recipe: dict[str, Any]) -> dict[str, Any]:
    """Return compact active recipe details for state and prompt context."""
    return {
        "name": str(recipe.get("name") or "").strip(),
        "slug": str(recipe.get("slug") or "").strip(),
        "ingredients": _extract_recipe_ingredients(recipe)[:40],
        "steps": _extract_recipe_steps(recipe)[:30],
    }


def _compact_shopping_result(tool_result: dict[str, Any]) -> dict[str, Any]:
    """Return compact shopping-list tool result for prompt history."""
    compact = {"success": tool_result.get("success")}
    if "item" in tool_result:
        compact["item"] = tool_result.get("item")
    if "amount" in tool_result:
        compact["amount"] = tool_result.get("amount")
    items = tool_result.get("items")
    if isinstance(items, list):
        compact["items"] = [
            item
            for item in items[:12]
            if isinstance(item, dict)
        ]
    return compact


def _format_amount(value: Any) -> str:
    """Return a compact spoken amount."""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


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
