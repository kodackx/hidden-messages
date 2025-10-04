"""Pytest fixtures and configuration for the test suite"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from uuid import uuid4

from app.models.database import Base
from app.agents.schemas import AgentOutput


@pytest_asyncio.fixture
async def db_engine():
    """Create an in-memory SQLite engine for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    
    async with engine.begin() as conn:
        # Enable foreign key constraints in SQLite
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing"""
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_agent_output():
    """Factory for creating mock AgentOutput responses"""
    def _create(
        comms: str = "This is a test message about the topic.",
        internal_thoughts: str = "I am thinking strategically.",
        guess: str | None = None
    ) -> AgentOutput:
        return AgentOutput(
            comms=comms,
            internal_thoughts=internal_thoughts,
            guess=guess
        )
    return _create


@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {
        "topic": "space exploration",
        "secret_word": "horizon",
        "participants": [
            {
                "id": str(uuid4()),
                "provider": "openai",
                "role": "communicator",
                "order": 0,
                "name": "Alice"
            },
            {
                "id": str(uuid4()),
                "provider": "anthropic",
                "role": "receiver",
                "order": 1,
                "name": "Bob"
            },
            {
                "id": str(uuid4()),
                "provider": "google-gla",
                "role": "bystander",
                "order": 2,
                "name": "Charlie"
            }
        ]
    }


@pytest.fixture
def mock_conversation_history():
    """Sample conversation history for testing"""
    return [
        {
            "participant_id": "alice",
            "participant_name": "Alice",
            "comms": "I think we should explore the distant horizon of Mars."
        },
        {
            "participant_id": "bob",
            "participant_name": "Bob",
            "comms": "That's an interesting perspective on space missions."
        },
        {
            "participant_id": "charlie",
            "participant_name": "Charlie",
            "comms": "I agree, reaching new frontiers is exciting."
        }
    ]
