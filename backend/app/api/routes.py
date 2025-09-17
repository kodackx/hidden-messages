from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from typing import Dict, Optional
import os
from sqlalchemy import select

from ..models import get_db, SessionModel, MessageModel, GuessModel
from ..agents import HiddenMessageAgent
from .schemas import (
    StartSessionRequest,
    StartSessionResponse,
    NextTurnRequest,
    NextTurnResponse,
    MessageResponse,
    GuessResult
)
from .session_state import SessionState, active_sessions
from ..core.logging import get_logger

router = APIRouter()

# Global agent manager
agent_manager = HiddenMessageAgent()
logger = get_logger("api.routes")

@router.post("/start-session", response_model=StartSessionResponse)
async def start_session(
    request: StartSessionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Initialize a new conversation session with agents"""
    try:
        # Initialize agents and get secret word (use provided or randomize)
        # Build participants mapping and receiver tries
        from uuid import uuid4 as _uuid4
        participants = []
        from itertools import cycle
        default_names = [
            "Participant Alpha", "Participant Beta", "Participant Gamma", "Participant Delta",
            "Participant Epsilon", "Participant Zeta", "Participant Eta", "Participant Theta",
            "Participant Iota", "Participant Kappa"
        ]
        names_iter = cycle(default_names)
        for p in request.participants:
            pid = str(p.id or _uuid4())
            name = p.name or next(names_iter)
            participants.append({"id": pid, "provider": p.provider, "role": p.role, "order": p.order, "name": name})
        agents_map = {p["id"]: {"provider": p["provider"], "role": p["role"]} for p in participants}

        secret_word = await agent_manager.initialize_agents(
            request.secret_word,
            agents=agents_map
        )

        # Create session in database
        session_id = uuid4()
        session = SessionModel(
            id=session_id,
            topic=request.topic,
            secret_word=secret_word,
            participants={p["id"]: {"provider": p["provider"], "role": p["role"], "name": p.get("name")} for p in participants}
        )
        db.add(session)
        await db.commit()

        # Store session state in memory
        # Set initial tries for receivers only
        initial_tries = {p["id"]: 3 for p in participants if p["role"] == "receiver"}

        active_sessions[session_id] = SessionState(
            session_id=session_id,
            topic=request.topic,
            secret_word=secret_word,
            participants=participants,
            tries_remaining=initial_tries
        )

        return StartSessionResponse(
            session_id=session_id,
            status="agents_initialized_and_session_created"
        )

    except Exception as e:
        logger.exception("start_session failed")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@router.post("/next-turn", response_model=NextTurnResponse)
async def next_turn(
    request: NextTurnRequest,
    db: AsyncSession = Depends(get_db)
):
    """Execute the next conversation turn"""
    # Check if session exists
    if request.session_id not in active_sessions:
        # Attempt to hydrate in-memory state from DB
        try:
            session_row = (await db.execute(select(SessionModel).where(SessionModel.id == request.session_id))).scalar_one_or_none()
            if not session_row:
                raise HTTPException(status_code=404, detail="Session not found")

            # Participants mapping is stored on the session row
            participants_map: Dict[str, Dict[str, str]] = session_row.participants
            participants_list = [
                {"id": pid, "provider": meta.get("provider"), "role": meta.get("role"), "order": None}
                for pid, meta in participants_map.items()
            ]
            agents_map = {pid: {"provider": meta.get("provider"), "role": meta.get("role")} for pid, meta in participants_map.items()}

            # Build conversation history and determine next turn number
            result_msgs = await db.execute(
                select(MessageModel).where(MessageModel.session_id == request.session_id).order_by(MessageModel.turn.asc())
            )
            msgs = list(result_msgs.scalars())
            conversation_history = [{"participant_id": m.participant_id, "comms": m.comms} for m in msgs]
            next_turn = (max((m.turn for m in msgs), default=0) + 1) or 1

            # Compute tries remaining for receivers
            receivers = {pid for pid, meta in participants_map.items() if meta.get("role") == "receiver"}
            tries_remaining: Dict[str, int] = {pid: 3 for pid in receivers}
            result_guesses = await db.execute(
                select(GuessModel).where(GuessModel.session_id == request.session_id).order_by(GuessModel.turn.desc())
            )
            for g in result_guesses.scalars():
                if g.agent in receivers and g.tries_remaining is not None:
                    # first occurrence per agent is latest due to desc order
                    if tries_remaining.get(g.agent, None) == 3:
                        tries_remaining[g.agent] = g.tries_remaining

            active_sessions[request.session_id] = SessionState(
                session_id=request.session_id,
                topic=session_row.topic,
                secret_word=session_row.secret_word,
                participants=participants_list,
                conversation_history=conversation_history,
                turn_number=next_turn,
                tries_remaining=tries_remaining,
            )
            # Recreate in-memory agents so get_agent_response can resolve ids
            await agent_manager.initialize_agents(session_row.secret_word, agents=agents_map)
            logger.debug(f"Hydrated session {request.session_id} from DB: turn={next_turn}, receivers={list(receivers)}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to hydrate session {request.session_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to load session state")

    session_state = active_sessions[request.session_id]

    # Check if game is over
    if session_state.game_over:
        raise HTTPException(status_code=400, detail="Game is already over")

    try:
        # Run conversation turn
        result = await agent_manager.run_conversation_turn(
            topic=session_state.topic,
            secret_word=session_state.secret_word,
            conversation_history=session_state.conversation_history,
            turn_number=session_state.turn_number,
            tries_remaining=session_state.tries_remaining,
            participants=session_state.participants
        )

        # Process messages and save to database
        response_messages = []
        guess_result = None

        for msg in result["messages"]:
            # Save message to database
            message = MessageModel(
                session_id=request.session_id,
                turn=session_state.turn_number,
                participant_id=msg["participant_id"],
                comms=msg["comms"],
                internal_thoughts=msg["internal_thoughts"]
            )
            db.add(message)

            # Add to response
            response_messages.append(MessageResponse(
                participant_id=msg["participant_id"],
                participant_name=next((p.get("name") for p in session_state.participants if p["id"] == msg["participant_id"]), None),
                internal_thoughts=msg["internal_thoughts"],
                comms=msg["comms"]
            ))

            # Process guess if present
            if msg["guess"] and any(p["id"] == msg["participant_id"] and p["role"] == "receiver" for p in session_state.participants):
                # Normalize and check guess
                guess_normalized = msg["guess"].lower().strip()
                secret_normalized = session_state.secret_word.lower().strip()
                is_correct = guess_normalized == secret_normalized

                # Update tries with safe default
                total_tries = int(os.getenv("TRIES_TOTAL", "3"))
                current_tries = session_state.tries_remaining.get(msg["participant_id"], total_tries)
                logger.debug(f"Updating tries for {msg['participant_id']}: {current_tries} -> {max(current_tries-1, 0)}")
                session_state.tries_remaining[msg["participant_id"]] = max(current_tries - 1, 0)

                # Save guess to database
                guess_record = GuessModel(
                    session_id=request.session_id,
                    turn=session_state.turn_number,
                    participant_id=msg["participant_id"],
                    guess=msg["guess"],
                    correct=is_correct,
                    tries_remaining=session_state.tries_remaining.get(msg["participant_id"], 0)
                )
                db.add(guess_record)

                guess_result = GuessResult(
                    agent=msg["participant_id"],
                    correct=is_correct,
                    tries_remaining=session_state.tries_remaining.get(msg["participant_id"], 0)
                )

                # Check win/loss conditions (collaborative): all win on correct guess
                if is_correct:
                    session_state.game_over = True
                    session_state.game_status = "win"
                elif session_state.tries_remaining[msg["participant_id"]] <= 0:
                    session_state.game_over = True
                    session_state.game_status = "loss"

        # Update session state
        session_state.conversation_history = result["conversation_history"]
        session_state.turn_number += 1

        # Commit database changes
        await db.commit()

        return NextTurnResponse(
            messages=response_messages,
            guess_result=guess_result,
            game_over=session_state.game_over,
            game_status=session_state.game_status
        )

    except Exception as e:
        await db.rollback()
        logger.exception("next_turn failed")
        raise HTTPException(status_code=500, detail=f"Failed to execute turn: {str(e)}")

@router.get("/session/{session_id}/status")
async def get_session_status(session_id: UUID):
    """Get current status of a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_state = active_sessions[session_id]

    return {
        "session_id": session_id,
        "turn_number": session_state.turn_number,
        "game_over": session_state.game_over,
        "game_status": session_state.game_status,
        "tries_remaining": session_state.tries_remaining
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}