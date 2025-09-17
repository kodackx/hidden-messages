from pydantic_ai import Agent
from pydantic_ai.models import ModelSettings
from typing import Optional, Dict, Any
import os
import random
from .schemas import AgentOutput, AgentContext
from .prompts import (
    SYSTEM_PROMPT,
    COMMUNICATOR_PROMPT,
    RECEIVER_PROMPT,
    BYSTANDER_PROMPT,
    format_conversation_history
)
from ..core.logging import get_logger

# List of secret words to choose from
SECRET_WORDS = [
    "unity", "harmony", "protocol", "cipher", "nexus", "quantum",
    "paradox", "synthesis", "eclipse", "horizon", "cascade", "vertex",
    "nebula", "resonance", "fractal", "zenith", "odyssey", "enigma"
]

class HiddenMessageAgent:
    """Manages AI agents for the hidden message game"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.model_settings = ModelSettings(temperature=0.3, max_tokens=50000)
        self.agent_meta: Dict[str, Dict[str, str]] = {}
        self.logger = get_logger("agents.manager")

    def _get_model_string(self, provider: str) -> str:
        """Convert provider name to model string using env defaults.

        Defaults follow Pydantic AI KnownModelName suggestions.
        """
        provider_map = {
            # Defaults configurable via env, with requested overrides
            "openai": os.getenv("OPENAI_DEFAULT_MODEL", "openai:gpt-5-mini"),
            "anthropic": os.getenv("ANTHROPIC_DEFAULT_MODEL", "anthropic:claude-sonnet-4-20250514"),
            "google": os.getenv("GOOGLE_DEFAULT_MODEL", "google:gemini-1.5-flash"),
            "google-gla": os.getenv("GOOGLE_GLA_DEFAULT_MODEL", "google-gla:gemini-2.5-pro"),
        }
        model = provider_map.get(provider)
        if model is None:
            raise ValueError(f"Unsupported provider: {provider}")
        return model

    def _create_agent(self, role: str, provider: str) -> Agent:
        """Create a Pydantic AI agent for specific role using provider."""
        model = self._get_model_string(provider)

        # Create agent
        agent = Agent(
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
        self.agents = {participant_id: self._create_agent(cfg["role"], cfg["provider"]) for participant_id, cfg in agents.items()}
        self.agent_meta = {participant_id: {"provider": cfg["provider"], "role": cfg["role"]} for participant_id, cfg in agents.items()}

        for pid, meta in self.agent_meta.items():
            try:
                model = self._get_model_string(meta["provider"])
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

    async def get_agent_response(self, context: AgentContext) -> Optional[AgentOutput]:
        """Get response from a specific agent"""
        agent = self.agents[context.participant_id]

        # Build the full prompt (inline the system prompt to avoid unsupported kwargs)
        system_text = SYSTEM_PROMPT.format(topic=context.topic)
        user_prompt = f"{system_text}\n\n{self._build_prompt(context)}"

        meta = self.agent_meta.get(context.participant_id, {})
        self.logger.debug(
            f"Invoking model for participant_id={context.participant_id} name={context.display_name} "
            f"role={context.agent_role} provider={meta.get('provider')}"
        )
        self.logger.debug(f"Prompt → {user_prompt[:400]}{'…' if len(user_prompt)>400 else ''}")

        try:
            # Use async context manager for streaming; get() available inside the context
            async with agent.run_stream(
                user_prompt,
                model_settings=self.model_settings,
            ) as stream:
                result = await stream.get()
        except Exception:
            self.logger.exception(f"run_stream failed for participant_id={context.participant_id}")
            return None

        # Normalize various possible return shapes to AgentOutput
        try:
            data = getattr(result, "data", None)
            if isinstance(data, AgentOutput):
                return data
            if isinstance(data, dict):
                return AgentOutput(
                    comms=str(data.get("comms", "")),
                    internal_thoughts=str(data.get("internal_thoughts", "")),
                    guess=data.get("guess") if data.get("guess") else None,
                )
            # Fallbacks: many implementations expose .text or .content
            text = getattr(result, "text", None) or getattr(result, "content", None) or str(result)
            return AgentOutput(comms=str(text), internal_thoughts="", guess=None)
        except Exception:
            # Absolute fallback
            try:
                return AgentOutput(comms=str(result), internal_thoughts="", guess=None)
            except Exception:
                return None

    async def run_conversation_turn(
        self,
        topic: str,
        secret_word: str,
        conversation_history: list[dict],
        turn_number: int,
        tries_remaining: dict[str, int],
        participants: list[dict]
    ) -> dict:
        """Run a complete conversation turn with all three agents"""
        messages = []

        # Sort participants by explicit order then by role priority (communicator < receiver < bystander)
        role_priority = {"communicator": 0, "receiver": 1, "bystander": 2}
        ordered = sorted(
            participants,
            key=lambda p: (p.get("order", role_priority.get(p["role"], 99)), role_priority.get(p["role"], 99))
        )

        history = conversation_history

        for p in ordered:
            participant_id = p["id"]
            role = p["role"]
            display_name = p.get("name") or participant_id

            context = AgentContext(
                agent_role=role,
                participant_id=participant_id,
                display_name=display_name,
                topic=topic,
                secret_word=secret_word if role == "communicator" else None,
                conversation_history=history,
                turn_number=turn_number,
                tries_remaining=tries_remaining.get(participant_id) if role == "receiver" else None,
            )
            response = await self.get_agent_response(context)

            if response is None:
                self.logger.error(f"Model call failed; skipping message for participant_id={participant_id}")
                continue

            # Skip empty outputs
            if not (response.comms or response.internal_thoughts or response.guess):
                self.logger.warning(f"Empty output; skipping message for participant_id={participant_id}")
                continue

            messages.append({
                "participant_id": participant_id,
                "internal_thoughts": response.internal_thoughts,
                "comms": response.comms,
                "guess": response.guess if role == "receiver" else None,
            })

            # Update history after each message
            history = history + [{"participant_id": participant_id, "comms": response.comms, "participant_name": display_name}]

        return {"messages": messages, "conversation_history": history}