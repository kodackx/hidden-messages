from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base

class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    topic = Column(Text, nullable=False)
    secret_word = Column(Text, nullable=False)
    participants = Column(JSON, nullable=False)  # {participant_id: {provider, role}}

    def __repr__(self):
        return f"<Session {self.id}: {self.topic[:50]}>"