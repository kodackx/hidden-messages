from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError, ProgrammingError
import asyncio

from ..core.logging import get_logger
from ..models.llm_call_event import LLMCallEventModel
from ..models.database import SessionLocal


logger = get_logger("core.llm_event_logger")

_TABLE_READY = False
_TABLE_LOCK = asyncio.Lock()


async def _ensure_table_exists(session: AsyncSession) -> None:
    global _TABLE_READY
    if _TABLE_READY:
        return

    async with _TABLE_LOCK:
        if _TABLE_READY:
            return
        try:
            async with session.bind.begin() as conn:
                await conn.run_sync(LLMCallEventModel.__table__.create, checkfirst=True)
        except Exception:
            logger.exception("Failed to ensure llm_call_events table exists")
        else:
            _TABLE_READY = True


async def log_llm_event(
    *,
    session_id: Optional[UUID] = None,
    participant_id: Optional[str] = None,
    participant_role: Optional[str] = None,
    participant_name: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    turn_number: Optional[int] = None,
    latency_ms: Optional[int] = None,
    prompt_text: Optional[str] = None,
    request_payload: Optional[Any] = None,
    response_text: Optional[str] = None,
    response_payload: Optional[Any] = None,
    status: str = "unknown",
    status_detail: Optional[str] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
    context_snapshot: Optional[Any] = None,
    db_session: Optional[AsyncSession] = None,
) -> None:
    owns_session = db_session is None
    session: AsyncSession

    if owns_session:
        session = SessionLocal()
    else:
        session = db_session

    try:
        await _ensure_table_exists(session)

        event = LLMCallEventModel(
            session_id=session_id,
            participant_id=participant_id,
            participant_role=participant_role,
            participant_name=participant_name,
            provider=provider,
            model=model,
            turn_number=turn_number,
            latency_ms=latency_ms,
            prompt_text=prompt_text,
            request_payload=request_payload,
            response_text=response_text,
            response_payload=response_payload,
            status=status or "unknown",
            status_detail=status_detail,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            context_snapshot=context_snapshot,
        )

        session.add(event)

        if owns_session:
            await session.commit()
        else:
            await session.flush()

    except (OperationalError, ProgrammingError) as exc:
        if owns_session:
            await session.rollback()
        logger.warning("Skipping LLM call logging because table is unavailable: %s", exc)
    except Exception:
        if owns_session:
            await session.rollback()
        logger.exception("Failed to log LLM call event")
    finally:
        if owns_session:
            await session.close()
