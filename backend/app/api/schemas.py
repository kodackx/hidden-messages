from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from uuid import UUID

class AgentConfig(BaseModel):
    provider: Literal["openai", "anthropic", "google", "google-gla"]
    role: Literal["communicator", "receiver", "bystander"]

class ParticipantConfig(BaseModel):
    id: Optional[UUID] = None
    role: Literal["communicator", "receiver", "bystander"]
    provider: Literal["openai", "anthropic", "google", "google-gla"]
    order: Optional[int] = Field(None, description="Speaking order; lower goes earlier. Defaults by role.")
    name: Optional[str] = Field(None, description="Display name, e.g., 'Participant Alpha'")

def _default_participants() -> List[ParticipantConfig]:
    return [
        ParticipantConfig(name="Participant Alpha", provider="openai", role="communicator", order=0),
        ParticipantConfig(name="Participant Beta", provider="anthropic", role="receiver", order=1),
        ParticipantConfig(name="Participant Gamma", provider="google-gla", role="bystander", order=2),
    ]

class StartSessionRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    secret_word: Optional[str] = Field(None, min_length=1, max_length=100)
    participants: List[ParticipantConfig] = Field(default_factory=_default_participants)

class AgentInfo(BaseModel):
    id: str
    role: str
    provider: str

class StartSessionResponse(BaseModel):
    session_id: UUID
    status: str

class NextTurnRequest(BaseModel):
    session_id: UUID

class MessageResponse(BaseModel):
    participant_id: str
    participant_name: Optional[str] = None
    participant_role: Optional[str] = None
    internal_thoughts: str
    comms: str

class GuessResult(BaseModel):
    agent: str
    correct: bool
    tries_remaining: int

class NextTurnResponse(BaseModel):
    messages: List[MessageResponse]
    guess_result: Optional[GuessResult] = None
    game_over: bool = False
    game_status: Optional[str] = None