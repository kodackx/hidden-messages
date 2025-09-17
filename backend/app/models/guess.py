from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .database import Base

class GuessModel(Base):
    __tablename__ = "guesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    turn = Column(Integer, nullable=False)
    participant_id = Column(String(64), nullable=False)
    guess = Column(Text, nullable=False)
    correct = Column(Boolean, nullable=False)
    tries_remaining = Column(Integer, nullable=False)

    __table_args__ = (
        Index("ix_guesses_session_turn", "session_id", "turn"),
    )

    session = relationship("SessionModel", backref="guesses")

    def __repr__(self):
        return f"<Guess {self.session_id} T{self.turn} Participant{self.participant_id}: {self.guess}>"