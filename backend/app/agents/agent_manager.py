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
        self.agents: Dict[str, Agent[AgentOutput]] = {}
        self.model_settings = ModelSettings(temperature=0.3, max_tokens=2000)
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

    def _create_agent(self, role: str, provider: str) -> Agent[AgentOutput]:
        """Create a Pydantic AI agent for specific role using provider."""
        model = self._get_model_string(provider)

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

    async def get_agent_response(self, context: AgentContext) -> tuple[Optional[AgentOutput], Optional[str]]:
        """Get response from a specific agent
        
        Returns:
            tuple: (AgentOutput or None, error_message or None)
        """
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
            # Use run() to get the final result directly
            # The Agent[AgentOutput] generic type tells Pydantic AI what to return
            result = await agent.run(
                user_prompt,
                model_settings=self.model_settings,
            )
        except Exception as e:
            # Attempt to extract more detailed error information from the exception
            detailed_error = str(e)
            if hasattr(e, 'body'):
                try:
                    import json
                    body = e.body
                    if isinstance(body, bytes):
                        body = body.decode('utf-8')
                    if isinstance(body, str):
                         body = json.loads(body)
                    
                    error_details = body.get("error", {})
                    if "message" in error_details:
                        detailed_error += f" | Details: {error_details['message']}"
                    else:
                        detailed_error += f" | Body: {str(body)[:200]}"

                except Exception as parse_err:
                    self.logger.warning(f"Could not parse exception body: {parse_err}")
                    detailed_error += f" | Raw Body: {str(getattr(e, 'body', ''))[:200]}"
            
            error_msg = f"{type(e).__name__}: {detailed_error}"
            self.logger.exception(f"run failed for participant_id={context.participant_id}")
            self.logger.error(f"Failed with provider={meta.get('provider')}, role={context.agent_role}, Details: {detailed_error}")
            return None, error_msg

        # Extract the structured data from the result
        try:
            # Log result attributes to understand its structure
            result_attrs = [attr for attr in dir(result) if not attr.startswith('_')]
            self.logger.debug(f"Result type: {type(result)}, attributes: {result_attrs[:10]}")
            
            # Try different possible attribute names for the output
            output = None
            if hasattr(result, 'data'):
                output = result.data
                self.logger.debug(f"Found result.data: {type(output)}")
            elif hasattr(result, 'output'):
                output = result.output
                self.logger.debug(f"Found result.output: {type(output)}")
            else:
                # Log the full result to understand its structure
                self.logger.error(f"Result has neither 'data' nor 'output'. Dir: {result_attrs}")
                error_msg = f"Result has no 'data' or 'output' attribute. Result type: {type(result)}"
                return None, error_msg
            
            # Check if output is an AgentOutput instance
            if isinstance(output, AgentOutput):
                self.logger.debug(f"Successfully extracted AgentOutput: comms={output.comms[:50] if output.comms else 'None'}...")
                return output, None
            
            # Try to construct AgentOutput from dict
            if isinstance(output, dict):
                self.logger.debug(f"Output is dict, attempting to construct AgentOutput")
                return AgentOutput(**output), None
            
            # Try to parse as string if it's JSON
            if isinstance(output, str):
                self.logger.debug(f"Output is string, attempting to parse as JSON")
                import json
                import re
                try:
                    # Strip markdown code blocks if present
                    cleaned = output.strip()
                    if cleaned.startswith('```'):
                        # Remove ```json or ``` at start and ``` at end
                        cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned)
                        cleaned = re.sub(r'\n?```\s*$', '', cleaned)
                    
                    parsed = json.loads(cleaned)
                    return AgentOutput(**parsed), None
                except Exception as json_err:
                    self.logger.error(f"Failed to parse string output as JSON: {json_err}")
                    self.logger.debug(f"Attempted to parse: {output[:200]}")
            
            error_msg = f"Unexpected output type: {type(output)}, value: {str(output)[:200]}"
            self.logger.error(error_msg)
            return None, error_msg
            
        except Exception as e:
            error_msg = f"Failed to extract data from result: {type(e).__name__}: {str(e)}"
            self.logger.exception(f"Result extraction failed. Result repr: {repr(result)[:500]}")
            return None, error_msg

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
        errors = []

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
            response, error = await self.get_agent_response(context)

            if response is None:
                error_detail = f"{display_name} ({role}): {error}" if error else f"{display_name} ({role}): Unknown error"
                errors.append(error_detail)
                self.logger.error(f"Model call failed; skipping message for participant_id={participant_id}: {error}")
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

        return {"messages": messages, "errors": errors}