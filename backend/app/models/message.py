from sqlalchemy import Column, String, Text, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .database import Base

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    turn = Column(Integer, nullable=False)
    participant_id = Column(String(64), nullable=False)
    comms = Column(Text, nullable=False)
    internal_thoughts = Column(Text, nullable=False)

    __table_args__ = (
        Index("ix_messages_session_turn", "session_id", "turn"),
    )

    session = relationship("SessionModel", backref="messages")

    def __repr__(self):
        return f"<Message {self.session_id} T{self.turn} Participant{self.participant_id}>"