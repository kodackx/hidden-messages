import pytest
from uuid import uuid4
from sqlalchemy import select

from app.core.llm_event_logger import log_llm_event
from app.models import SessionModel
from app.models.llm_call_event import LLMCallEventModel


@pytest.mark.asyncio
async def test_log_llm_event_persists_success(db_session):
    session_id = uuid4()

    session_row = SessionModel(
        id=session_id,
        topic="test topic",
        secret_word="secret",
        participants={},
    )
    db_session.add(session_row)
    await db_session.commit()

    await log_llm_event(
        session_id=session_id,
        participant_id="agent-1",
        participant_role="communicator",
        participant_name="Agent One",
        provider="openai",
        model="openai:gpt-test",
        turn_number=1,
        latency_ms=120,
        prompt_text="prompt",
        response_text="response",
        status="success",
        prompt_tokens=5,
        completion_tokens=7,
        total_tokens=12,
        context_snapshot=[{"participant_id": "system", "comms": "hello"}],
        db_session=db_session,
    )

    result = await db_session.execute(select(LLMCallEventModel))
    event = result.scalar_one()

    assert event.session_id == session_id
    assert event.status == "success"
    assert event.prompt_tokens == 5
    assert event.total_tokens == 12
    assert event.prompt_text == "prompt"


@pytest.mark.asyncio
async def test_log_llm_event_error_records_detail(db_session):
    await log_llm_event(
        participant_id="agent-2",
        participant_role="receiver",
        status="error",
        status_detail="boom",
        response_text="failure",
        response_payload={"error": "Boom"},
        db_session=db_session,
    )

    result = await db_session.execute(select(LLMCallEventModel).order_by(LLMCallEventModel.created_at))
    events = result.scalars().all()

    assert len(events) == 1
    assert events[0].status == "error"
    assert events[0].status_detail == "boom"
