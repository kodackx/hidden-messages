from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from .database import Base


class LLMCallEventModel(Base):
    __tablename__ = "llm_call_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    participant_id = Column(String(64), nullable=True)
    participant_role = Column(String(32), nullable=True)
    participant_name = Column(String(128), nullable=True)

    provider = Column(String(32), nullable=True)
    model = Column(String(128), nullable=True)

    turn_number = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)

    prompt_text = Column(Text, nullable=True)
    request_payload = Column(JSON, nullable=True)

    response_text = Column(Text, nullable=True)
    response_payload = Column(JSON, nullable=True)

    status = Column(String(32), nullable=False, default="unknown")
    status_detail = Column(Text, nullable=True)

    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)

    context_snapshot = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        parts = [self.id and str(self.id) or "<pending>"]
        if self.participant_id:
            parts.append(self.participant_id)
        if self.status:
            parts.append(self.status)
        return f"<LLMCallEvent {' '.join(parts)}>"
