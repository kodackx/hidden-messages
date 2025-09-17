from typing import Dict, Optional, List
from uuid import UUID
from dataclasses import dataclass, field

@dataclass
class SessionState:
    """In-memory state for active sessions"""
    session_id: UUID
    topic: str
    secret_word: str
    participants: List[dict] = field(default_factory=list)  # [{id, role, provider, order}]
    conversation_history: list = field(default_factory=list)
    turn_number: int = 1
    tries_remaining: Dict[str, int] = field(default_factory=dict)  # keyed by receiver id
    game_over: bool = False
    game_status: Optional[str] = None  # 'win' or 'loss'

# In-memory store for active sessions
# In production, this should be Redis or similar
active_sessions: Dict[UUID, SessionState] = {}