from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class AgentOutput(BaseModel):
    """Structured output format that agents must return"""
    comms: str = Field(..., description="Natural, on-topic contribution visible to all")
    internal_thoughts: str = Field(..., description="Private notes about intent/strategy")
    guess: Optional[str] = Field(None, description="Optional guess at the hidden word (receiver only)")

class AgentContext(BaseModel):
    """Context passed to agents each turn"""
    agent_role: str  # "communicator", "receiver", "bystander"
    participant_id: str  # stable ID key used for lookup
    display_name: Optional[str] = None  # human-friendly name for prompts
    session_id: Optional[UUID] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    topic: str
    secret_word: Optional[str] = None  # Only provided to communicator
    conversation_history: list[dict] = Field(default_factory=list)
    turn_number: int = 1
    tries_remaining: Optional[int] = None  # Only provided to receiver