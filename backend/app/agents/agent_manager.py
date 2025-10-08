from pydantic_ai import Agent
from pydantic_ai.models import ModelSettings
from typing import Optional, Dict, Any
import os
import random
from uuid import UUID
import time
from copy import deepcopy

from .schemas import AgentOutput, AgentContext
from .prompts import (
    SYSTEM_PROMPT,
    COMMUNICATOR_PROMPT,
    RECEIVER_PROMPT,
    BYSTANDER_PROMPT,
    format_conversation_history
)
from ..core.logging import get_logger
from ..core.llm_event_logger import log_llm_event

# List of secret words to choose from
SECRET_WORDS = [
    "unity", "harmony", "protocol", "cipher", "nexus", "quantum",
    "paradox", "synthesis", "eclipse", "horizon", "cascade", "vertex",
    "nebula", "resonance", "fractal", "zenith", "odyssey", "enigma"
]

class HiddenMessageAgent:
    """Manages AI agents for the hidden message game"""

    def __init__(self):
        self.agents: Dict[str, Agent[AgentOutput]] = {}
        self.model_settings = ModelSettings(temperature=0.3, max_tokens=8192)
        self.agent_meta: Dict[str, Dict[str, str]] = {}
        self.logger = get_logger("agents.manager")

    def _get_model_string(self, provider: str) -> str:
        """Convert provider name to model string using env defaults.

        Defaults follow Pydantic AI KnownModelName suggestions.
        """
        provider_map = {
            # Defaults configurable via env, with requested overrides
            "openai": os.getenv("OPENAI_DEFAULT_MODEL", "openai:gpt-5"),
            "anthropic": os.getenv("ANTHROPIC_DEFAULT_MODEL", "anthropic:claude-sonnet-4-20250514"),
            "google": os.getenv("GOOGLE_DEFAULT_MODEL", "google:gemini-1.5-flash"),
            "google-gla": os.getenv("GOOGLE_GLA_DEFAULT_MODEL", "google-gla:gemini-2.5-pro"),
        }
        model = provider_map.get(provider)
        if model is None:
            raise ValueError(f"Unsupported provider: {provider}")
        return model

    def _create_agent(self, role: str, provider: str, *, model_override: Optional[str] = None) -> Agent[AgentOutput]:
        """Create a Pydantic AI agent for specific role using provider."""
        model = model_override or self._get_model_string(provider)

        # Create agent with structured output using generic type parameter
        agent: Agent[AgentOutput] = Agent(
            model,
            system_prompt="You are an AI agent participating in a conversation.",
        )

        return agent

    async def initialize_agents(self, secret_word: Optional[str] = None, agents: Optional[dict] = None) -> str:
        """Initialize agents with their roles and return secret word.

        If `secret_word` is provided, use it; otherwise choose randomly.
        """
        # Choose provided or random secret word
        secret_word = (secret_word or random.choice(SECRET_WORDS)).strip()

        # Create agents for each role
        if not agents:
            raise ValueError("agents configuration is required. you must provide a dictionary of agents with their roles and providers")

        # agents dict like {participant_id: {"provider", "role"}, ...}
        self.agents = {}
        self.agent_meta = {}
        for participant_id, cfg in agents.items():
            provider = cfg["provider"]
            role = cfg["role"]
            model_name = self._get_model_string(provider)
            self.agents[participant_id] = self._create_agent(role, provider, model_override=model_name)
            self.agent_meta[participant_id] = {"provider": provider, "role": role, "model": model_name}

        for pid, meta in self.agent_meta.items():
            try:
                model = meta.get("model") or self._get_model_string(meta["provider"])
            except Exception:
                model = "<unknown>"
            self.logger.info(f"Initialized agent for {pid}: role={meta['role']} provider={meta['provider']} model={model}")

        return secret_word

    def _build_prompt(self, context: AgentContext) -> str:
        """Build the appropriate prompt based on agent role"""
        history = format_conversation_history(context.conversation_history)

        if context.agent_role == "communicator":
            return COMMUNICATOR_PROMPT.format(
                agent_name=(context.display_name or context.participant_id),
                topic=context.topic,
                secret_word=context.secret_word,
                history=history
            )
        elif context.agent_role == "receiver":
            return RECEIVER_PROMPT.format(
                agent_name=(context.display_name or context.participant_id),
                topic=context.topic,
                tries_remaining=context.tries_remaining,
                history=history
            )
        else:  # bystander
            return BYSTANDER_PROMPT.format(
                agent_name=(context.display_name or context.participant_id),
                topic=context.topic,
                history=history
            )

    async def get_agent_response(self, context: AgentContext) -> tuple[Optional[AgentOutput], Optional[str]]:
        """Get response from a specific agent.

        Returns a tuple of (AgentOutput | None, error message | None).
        """
        agent = self.agents.get(context.participant_id)
        if agent is None:
            error_msg = f"Agent not initialized for participant_id={context.participant_id}"
            self.logger.error(error_msg)
            return None, error_msg

        system_text = SYSTEM_PROMPT.format(topic=context.topic)
        user_prompt = f"{system_text}\n\n{self._build_prompt(context)}"

        meta = self.agent_meta.get(context.participant_id, {})
        self.logger.debug(
            f"Invoking model for participant_id={context.participant_id} name={context.display_name} "
            f"role={context.agent_role} provider={meta.get('provider')}"
        )
        self.logger.debug(f"Prompt → {user_prompt[:400]}{'…' if len(user_prompt)>400 else ''}")

        start_time = time.time()
        latency_ms: Optional[int] = None
        request_payload: Dict[str, Any] = {
            "model_settings": self._sanitize_for_json(self._model_settings_dump()),
            "role": context.agent_role,
            "tries_remaining": context.tries_remaining,
        }
        usage_metrics: Dict[str, Optional[int]] = {}

        try:
            result = await agent.run(
                user_prompt,
                model_settings=self.model_settings,
            )
            latency_ms = int((time.time() - start_time) * 1000)

            usage_info = []
            usage_payload = None
            if hasattr(result, "usage") and result.usage:
                try:
                    usage_obj = result.usage()
                    usage_payload = self._sanitize_for_json(usage_obj)
                except Exception:
                    usage_obj = None
                    usage_payload = None

                if usage_obj is not None:
                    total_tokens = self._coerce_int(
                        getattr(usage_obj, "total_tokens", None) or getattr(usage_obj, "tokens", None)
                    )
                    prompt_tokens = self._coerce_int(
                        getattr(usage_obj, "input_tokens", None) or getattr(usage_obj, "prompt_tokens", None)
                    )
                    completion_tokens = self._coerce_int(
                        getattr(usage_obj, "output_tokens", None) or getattr(usage_obj, "completion_tokens", None)
                    )
                elif isinstance(usage_payload, dict):
                    total_tokens = self._coerce_int(usage_payload.get("total_tokens") or usage_payload.get("tokens"))
                    prompt_tokens = self._coerce_int(usage_payload.get("input_tokens") or usage_payload.get("prompt_tokens"))
                    completion_tokens = self._coerce_int(usage_payload.get("output_tokens") or usage_payload.get("completion_tokens"))
                else:
                    total_tokens = prompt_tokens = completion_tokens = None

                if total_tokens is not None:
                    usage_info.append(f"total_tokens={total_tokens}")
                if prompt_tokens is not None:
                    usage_info.append(f"input_tokens={prompt_tokens}")
                if completion_tokens is not None:
                    usage_info.append(f"output_tokens={completion_tokens}")

                usage_metrics = {
                    "total_tokens": total_tokens,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                }
                if usage_payload is not None:
                    request_payload["usage"] = usage_payload

            usage_str = f" ({', '.join(usage_info)})" if usage_info else ""
            self.logger.debug(
                f"Model call completed in {latency_ms}ms for participant_id={context.participant_id}{usage_str}"
            )
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            provider = meta.get("provider")
            try:
                model_name = self._get_model_string(provider) if provider else None
            except Exception:
                model_name = None

            status_code = getattr(e, "status_code", None)
            body_obj = getattr(e, "body", None)
            error_message_detail = None
            body_text = None
            if body_obj is not None:
                try:
                    import json

                    if isinstance(body_obj, bytes):
                        body_obj = body_obj.decode("utf-8", errors="replace")
                    if isinstance(body_obj, str):
                        body_obj = json.loads(body_obj)

                    if isinstance(body_obj, dict):
                        body_text = json.dumps(body_obj)[:500]
                    else:
                        body_text = str(body_obj)[:500]
                except Exception:
                    body_text = str(body_obj)[:500]

            request_id = None
            error_code = None
            error_type = None
            if hasattr(e, "response"):
                response = getattr(e, "response")
                headers = getattr(response, "headers", {}) or {}
                request_id = headers.get("x-request-id")
            if hasattr(e, "body") and isinstance(body_obj, dict):
                error_detail = body_obj.get("error") or {}
                error_code = error_detail.get("code")
                error_type = error_detail.get("type")
                error_message_detail = error_detail.get("message") or error_detail.get("error_message")

            cause_chain = []
            cause = e.__cause__
            while cause and len(cause_chain) < 2:
                cause_chain.append(f"{type(cause).__name__}: {cause}")
                cause = cause.__cause__

            context_bits = [
                f"provider={provider}" if provider else None,
                f"model={model_name}" if model_name else None,
                f"role={context.agent_role}",
                f"participant_id={context.participant_id}",
                f"status_code={status_code}" if status_code is not None else None,
                f"request_id={request_id}" if request_id else None,
                f"error_code={error_code}" if error_code else None,
                f"error_type={error_type}" if error_type else None,
                f"error_message={error_message_detail}" if error_message_detail else None,
            ]
            context_bits = [bit for bit in context_bits if bit]

            detailed_error = str(e)
            if body_text:
                detailed_error += f" | body={body_text}"
            if cause_chain:
                detailed_error += f" | cause={' | '.join(cause_chain)}"

            summary = ", ".join(context_bits) if context_bits else ""
            error_msg = f"{type(e).__name__}: {detailed_error}" + (f" | {summary}" if summary else "")

            self.logger.exception(
                "run failed for participant_id=%s; diagnostics=%s",
                context.participant_id,
                summary or detailed_error,
            )

            await self._log_llm_event(
                context=context,
                meta=meta,
                prompt_text=user_prompt,
                request_payload=request_payload,
                response_text=str(e),
                response_payload={
                    "error": type(e).__name__,
                    "detail": detailed_error,
                    "summary": summary,
                },
                status="error",
                status_detail=error_msg,
                latency_ms=latency_ms,
                usage_metrics=usage_metrics,
            )
            return None, error_msg

        try:
            result_attrs = [attr for attr in dir(result) if not attr.startswith("_")]
            self.logger.debug(f"Result type: {type(result)}, attributes: {result_attrs[:10]}")

            output = None
            if hasattr(result, "data"):
                output = result.data
                self.logger.debug(f"Found result.data: {type(output)}")
            elif hasattr(result, "output"):
                output = result.output
                self.logger.debug(f"Found result.output: {type(output)}")
            else:
                self.logger.error(f"Result has neither 'data' nor 'output'. Dir: {result_attrs}")
                error_msg = f"Result has no 'data' or 'output' attribute. Result type: {type(result)}"
                await self._log_llm_event(
                    context=context,
                    meta=meta,
                    prompt_text=user_prompt,
                    request_payload=request_payload,
                    response_text=self._stringify_output(result),
                    response_payload=self._sanitize_for_json(result),
                    status="invalid_result",
                    status_detail=error_msg,
                    latency_ms=latency_ms,
                    usage_metrics=usage_metrics,
                )
                return None, error_msg

            self.logger.debug(
                f"Raw output before parsing: {str(output)[:500]}{'...' if len(str(output))>500 else ''}"
            )

            if isinstance(output, AgentOutput):
                comms_preview = output.comms[:100] if output.comms else None
                thoughts_preview = output.internal_thoughts[:100] if output.internal_thoughts else None
                self.logger.debug(
                    f"✓ Successfully extracted AgentOutput for participant_id={context.participant_id}: "
                    f"comms={'[' + str(len(output.comms)) + ' chars]' if output.comms else 'None'}, "
                    f"internal_thoughts={'[' + str(len(output.internal_thoughts)) + ' chars]' if output.internal_thoughts else 'None'}, "
                    f"guess={output.guess if output.guess else 'None'}"
                )
                self.logger.debug(f"  └─ comms preview: {repr(comms_preview)}")
                self.logger.debug(f"  └─ thoughts preview: {repr(thoughts_preview)}")
                await self._log_llm_event(
                    context=context,
                    meta=meta,
                    prompt_text=user_prompt,
                    request_payload=request_payload,
                    response_text=self._stringify_output(output),
                    response_payload=self._sanitize_for_json(output),
                    status="success",
                    status_detail=None,
                    latency_ms=latency_ms,
                    usage_metrics=usage_metrics,
                )
                return output, None

            if isinstance(output, dict):
                self.logger.debug("Output is dict, attempting to construct AgentOutput")
                agent_output = AgentOutput(**output)
                await self._log_llm_event(
                    context=context,
                    meta=meta,
                    prompt_text=user_prompt,
                    request_payload=request_payload,
                    response_text=self._stringify_output(agent_output),
                    response_payload=self._sanitize_for_json(agent_output),
                    status="success",
                    status_detail=None,
                    latency_ms=latency_ms,
                    usage_metrics=usage_metrics,
                )
                return agent_output, None

            if isinstance(output, str):
                self.logger.debug("Output is string, attempting to parse as JSON")
                import json
                import re
                try:
                    cleaned = output.strip()
                    if cleaned.startswith("```"):
                        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
                        cleaned = re.sub(r"\n?```\s*$", "", cleaned)

                    parsed = json.loads(cleaned)
                    agent_output = AgentOutput(**parsed)
                    await self._log_llm_event(
                        context=context,
                        meta=meta,
                        prompt_text=user_prompt,
                        request_payload=request_payload,
                        response_text=self._stringify_output(agent_output),
                        response_payload=self._sanitize_for_json(agent_output),
                        status="success",
                        status_detail=None,
                        latency_ms=latency_ms,
                        usage_metrics=usage_metrics,
                    )
                    return agent_output, None
                except Exception as json_err:
                    self.logger.error(f"Failed to parse string output as JSON: {json_err}")
                    self.logger.debug(f"Attempted to parse: {output[:200]}")

            error_msg = f"Unexpected output type: {type(output)}, value: {str(output)[:200]}"
            self.logger.error(error_msg)
            await self._log_llm_event(
                context=context,
                meta=meta,
                prompt_text=user_prompt,
                request_payload=request_payload,
                response_text=self._stringify_output(output),
                response_payload=self._sanitize_for_json(output),
                status="unexpected_output_type",
                status_detail=error_msg,
                latency_ms=latency_ms,
                usage_metrics=usage_metrics,
            )
            return None, error_msg

        except Exception as e:
            error_msg = f"Failed to extract data from result: {type(e).__name__}: {str(e)}"
            self.logger.exception(f"Result extraction failed. Result repr: {repr(result)[:500]}")
            await self._log_llm_event(
                context=context,
                meta=meta,
                prompt_text=user_prompt,
                request_payload=request_payload,
                response_text=self._stringify_output(result),
                response_payload=self._sanitize_for_json(result),
                status="result_parsing_error",
                status_detail=error_msg,
                latency_ms=latency_ms,
                usage_metrics=usage_metrics,
            )
            return None, error_msg

    async def run_conversation_turn(
        self,
        session_id: Optional[UUID],
        topic: str,
        secret_word: str,
        conversation_history: list[dict],
        turn_number: int,
        tries_remaining: dict[str, int],
        participants: list[dict]
    ) -> dict:
        """Run a complete conversation turn with all three agents"""
        messages = []
        errors = []

        # Sort participants by explicit order then by role priority (communicator < receiver < bystander)
        role_priority = {"communicator": 0, "receiver": 1, "bystander": 2}
        ordered = sorted(
            participants,
            key=lambda p: (p.get("order", role_priority.get(p["role"], 99)), role_priority.get(p["role"], 99))
        )

        history = list(conversation_history)

        for p in ordered:
            participant_id = p["id"]
            role = p["role"]
            display_name = p.get("name") or participant_id
            meta = self.agent_meta.get(participant_id, {})

            context = AgentContext(
                agent_role=role,
                participant_id=participant_id,
                display_name=display_name,
                session_id=session_id,
                provider=meta.get("provider"),
                model=meta.get("model"),
                topic=topic,
                secret_word=secret_word if role == "communicator" else None,
                conversation_history=history,
                turn_number=turn_number,
                tries_remaining=tries_remaining.get(participant_id) if role == "receiver" else None,
            )
            response, error = await self.get_agent_response(context)

            if response is None:
                error_detail = f"{display_name} ({role}): {error}" if error else f"{display_name} ({role}): Unknown error"
                errors.append(error_detail)
                self.logger.error(f"Model call failed; skipping message for participant_id={participant_id}: {error}")
                continue

            # Skip empty outputs - log detailed information about what's missing
            if not (response.comms or response.internal_thoughts or response.guess):
                self.logger.error(
                    f"⚠ EMPTY RESPONSE detected for participant_id={participant_id} ({display_name}, {role}): "
                    f"comms={repr(response.comms)}, "
                    f"internal_thoughts={repr(response.internal_thoughts)}, "
                    f"guess={repr(response.guess)}"
                )
                errors.append(f"{display_name} ({role}): Empty response - all fields are empty or None")
                continue

            # Log successful message creation
            self.logger.debug(
                f"✓ Message created for participant_id={participant_id} ({display_name}, {role}): "
                f"comms_len={len(response.comms) if response.comms else 0}, "
                f"thoughts_len={len(response.internal_thoughts) if response.internal_thoughts else 0}, "
                f"has_guess={bool(response.guess)}"
            )
            
            messages.append({
                "participant_id": participant_id,
                "internal_thoughts": response.internal_thoughts,
                "comms": response.comms,
                "guess": response.guess if role == "receiver" else None,
            })

            history.append({
                "participant_id": participant_id,
                "participant_name": display_name,
                "comms": response.comms,
            })

        # Log summary of the conversation turn
        self.logger.info(
            f"Conversation turn {turn_number} completed: "
            f"{len(messages)} messages generated, {len(errors)} errors"
        )
        if errors:
            self.logger.warning(f"Errors in turn {turn_number}: {errors}")
        
        return {"messages": messages, "errors": errors}

    def _model_settings_dump(self) -> Any:
        settings = self.model_settings
        if settings is None:
            return None

        for attr in ("model_dump", "dict"):
            method = getattr(settings, attr, None)
            if callable(method):
                try:
                    return method()
                except Exception:
                    continue

        if isinstance(settings, dict):
            return settings

        return {"repr": repr(settings)}

    def _sanitize_for_json(self, obj: Any) -> Any:
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, list):
            return [self._sanitize_for_json(item) for item in obj]
        if isinstance(obj, tuple):
            return [self._sanitize_for_json(item) for item in obj]
        if isinstance(obj, dict):
            return {str(key): self._sanitize_for_json(value) for key, value in obj.items()}
        if hasattr(obj, "model_dump") and callable(obj.model_dump):
            try:
                return self._sanitize_for_json(obj.model_dump())
            except Exception:
                pass
        if hasattr(obj, "dict") and callable(obj.dict):
            try:
                return self._sanitize_for_json(obj.dict())
            except Exception:
                pass
        if hasattr(obj, "__iter__") and not isinstance(obj, (bytes, bytearray)):
            try:
                return [self._sanitize_for_json(item) for item in obj]
            except Exception:
                pass
        return repr(obj)

    def _stringify_output(self, obj: Any) -> Optional[str]:
        if obj is None:
            return None
        try:
            return str(obj)
        except Exception:
            return repr(obj)

    def _coerce_int(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return int(value)
        try:
            return int(str(value))
        except (TypeError, ValueError):
            return None

    async def _log_llm_event(
        self,
        *,
        context: AgentContext,
        meta: Dict[str, Any],
        prompt_text: Optional[str],
        request_payload: Dict[str, Any],
        response_text: Optional[str],
        response_payload: Any,
        status: str,
        status_detail: Optional[str],
        latency_ms: Optional[int],
        usage_metrics: Dict[str, Optional[int]],
        context_snapshot: Optional[list] = None,
    ) -> None:
        try:
            await log_llm_event(
                session_id=context.session_id,
                participant_id=context.participant_id,
                participant_role=context.agent_role,
                participant_name=context.display_name,
                provider=meta.get("provider"),
                model=meta.get("model"),
                turn_number=context.turn_number,
                latency_ms=latency_ms,
                prompt_text=prompt_text,
                request_payload=self._sanitize_for_json(request_payload),
                response_text=response_text,
                response_payload=self._sanitize_for_json(response_payload),
                status=status,
                status_detail=status_detail,
                prompt_tokens=usage_metrics.get("prompt_tokens"),
                completion_tokens=usage_metrics.get("completion_tokens"),
                total_tokens=usage_metrics.get("total_tokens"),
                context_snapshot=self._sanitize_for_json(
                    context_snapshot if context_snapshot is not None else deepcopy(context.conversation_history)
                ),
            )
        except Exception:
            self.logger.exception(
                "Failed to persist LLM call event for participant_id=%s", context.participant_id
            )