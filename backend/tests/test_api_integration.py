"""Integration tests for API endpoints"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID

from app.main import app
from app.models import SessionModel, MessageModel, GuessModel
from app.api.session_state import SessionState, active_sessions
from app.api.routes import agent_manager
from app.agents.schemas import AgentOutput


@pytest_asyncio.fixture
async def client(db_session):
    """Create test client with database override"""
    from app.models.database import get_db
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint"""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health endpoint returns healthy status"""
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.integration
class TestStartSessionEndpoint:
    """Test session creation endpoint"""

    @pytest.mark.asyncio
    async def test_start_session_minimal(self, client):
        """Test starting session with minimal data"""
        with patch('app.agents.agent_manager.HiddenMessageAgent.initialize_agents') as mock_init:
            mock_init.return_value = "horizon"
            
            response = await client.post(
                "/api/start-session",
                json={
                    "topic": "space exploration"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "session_id" in data
            assert data["status"] == "agents_initialized_and_session_created"
            
            # Validate UUID format
            session_id = UUID(data["session_id"])
            assert isinstance(session_id, UUID)

    @pytest.mark.asyncio
    async def test_start_session_with_secret_word(self, client):
        """Test starting session with custom secret word"""
        with patch('app.agents.agent_manager.HiddenMessageAgent.initialize_agents') as mock_init:
            mock_init.return_value = "custom"
            
            response = await client.post(
                "/api/start-session",
                json={
                    "topic": "technology",
                    "secret_word": "custom"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "session_id" in data

    @pytest.mark.asyncio
    async def test_start_session_with_custom_participants(self, client):
        """Test starting session with custom participants"""
        with patch('app.agents.agent_manager.HiddenMessageAgent.initialize_agents') as mock_init:
            mock_init.return_value = "test"
            
            response = await client.post(
                "/api/start-session",
                json={
                    "topic": "art",
                    "participants": [
                        {
                            "role": "communicator",
                            "provider": "openai",
                            "order": 0,
                            "name": "Artist"
                        },
                        {
                            "role": "receiver",
                            "provider": "anthropic",
                            "order": 1,
                            "name": "Critic"
                        },
                        {
                            "role": "bystander",
                            "provider": "google-gla",
                            "order": 2,
                            "name": "Observer"
                        }
                    ]
                }
            )
            
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_start_session_invalid_topic(self, client):
        """Test that empty topic is rejected"""
        response = await client.post(
            "/api/start-session",
            json={"topic": ""}
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_start_session_invalid_role(self, client):
        """Test that invalid role is rejected"""
        response = await client.post(
            "/api/start-session",
            json={
                "topic": "test",
                "participants": [
                    {
                        "role": "invalid_role",
                        "provider": "openai"
                    }
                ]
            }
        )
        
        assert response.status_code == 422


@pytest.mark.integration
class TestNextTurnEndpoint:
    """Test conversation turn execution"""

    @pytest.mark.asyncio
    async def test_next_turn_session_not_found(self, client):
        """Test next turn with non-existent session"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.post(
            "/api/next-turn",
            json={"session_id": fake_uuid}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_next_turn_rehydrates_missing_history(self, client, db_session, sample_session_data):
        """Ensure a resumed session repopulates history before invoking agents"""
        # Persist session and prior messages
        session = SessionModel(
            topic=sample_session_data["topic"],
            secret_word=sample_session_data["secret_word"],
            participants={
                p["id"]: {
                    "provider": p["provider"],
                    "role": p["role"],
                    "name": p["name"],
                }
                for p in sample_session_data["participants"]
            },
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        prior_messages = [
            MessageModel(
                session_id=session.id,
                turn=1,
                participant_id=sample_session_data["participants"][0]["id"],
                comms="First turn opener",
                internal_thoughts="thinking",
            ),
            MessageModel(
                session_id=session.id,
                turn=2,
                participant_id=sample_session_data["participants"][1]["id"],
                comms="Second turn follow-up",
                internal_thoughts="pondering",
            ),
        ]
        db_session.add_all(prior_messages)
        await db_session.commit()

        # Simulate in-memory state missing history
        active_sessions.pop(session.id, None)
        tries_remaining = {
            p["id"]: 3 for p in sample_session_data["participants"] if p["role"] == "receiver"
        }
        active_sessions[session.id] = SessionState(
            session_id=session.id,
            topic=session.topic,
            secret_word=session.secret_word,
            participants=sample_session_data["participants"],
            conversation_history=[],
            turn_number=3,
            tries_remaining=tries_remaining,
        )

        async_mock = AsyncMock(return_value={
            "messages": [
                {
                    "participant_id": sample_session_data["participants"][0]["id"],
                    "comms": "New contribution",
                    "internal_thoughts": "continuing",
                    "guess": None,
                }
            ],
            "errors": [],
        })

        try:
            with patch.object(agent_manager, "run_conversation_turn", async_mock):
                response = await client.post(
                    "/api/next-turn",
                    json={"session_id": str(session.id)}
                )

            assert response.status_code == 200
            history_passed = async_mock.await_args.kwargs["conversation_history"]
            assert history_passed, "Expected prior messages to be provided to the agent"
            assert history_passed[0]["comms"] == "First turn opener"
            assert history_passed[1]["comms"] == "Second turn follow-up"
        finally:
            active_sessions.pop(session.id, None)
            agent_manager.agents.clear()
            agent_manager.agent_meta.clear()

    @pytest.mark.asyncio
    async def test_next_turn_success(self, client, db_session, sample_session_data):
        """Test successful turn execution"""
        # Create a session in the database
        session = SessionModel(
            topic=sample_session_data["topic"],
            secret_word=sample_session_data["secret_word"],
            participants={
                p["id"]: {"provider": p["provider"], "role": p["role"], "name": p["name"]}
                for p in sample_session_data["participants"]
            }
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        # Mock the agent manager
        with patch('app.api.routes.agent_manager') as mock_manager:
            mock_manager.initialize_agents = AsyncMock(return_value=sample_session_data["secret_word"])
            mock_manager.run_conversation_turn = AsyncMock(return_value={
                "messages": [
                    {
                        "participant_id": sample_session_data["participants"][0]["id"],
                        "comms": "Let's explore the distant horizon.",
                        "internal_thoughts": "Embedding the word naturally.",
                        "guess": None
                    },
                    {
                        "participant_id": sample_session_data["participants"][1]["id"],
                        "comms": "That's an interesting perspective.",
                        "internal_thoughts": "Analyzing for hidden meaning.",
                        "guess": None
                    },
                    {
                        "participant_id": sample_session_data["participants"][2]["id"],
                        "comms": "I agree with both of you.",
                        "internal_thoughts": "Just participating naturally.",
                        "guess": None
                    }
                ],
                "errors": []
            })
            
            response = await client.post(
                "/api/next-turn",
                json={"session_id": str(session.id)}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["messages"]) == 3
            assert data["game_over"] is False
            assert data["guess_result"] is None

    @pytest.mark.asyncio
    async def test_next_turn_with_correct_guess(self, client, db_session, sample_session_data):
        """Test turn with correct guess ends game"""
        session = SessionModel(
            topic=sample_session_data["topic"],
            secret_word=sample_session_data["secret_word"],
            participants={
                p["id"]: {"provider": p["provider"], "role": p["role"], "name": p["name"]}
                for p in sample_session_data["participants"]
            }
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        receiver_id = sample_session_data["participants"][1]["id"]
        
        with patch('app.api.routes.agent_manager') as mock_manager:
            mock_manager.initialize_agents = AsyncMock(return_value=sample_session_data["secret_word"])
            mock_manager.run_conversation_turn = AsyncMock(return_value={
                "messages": [
                    {
                        "participant_id": receiver_id,
                        "comms": "I think I know the word.",
                        "internal_thoughts": "I'm confident it's horizon.",
                        "guess": "horizon"
                    }
                ],
                "errors": []
            })
            
            response = await client.post(
                "/api/next-turn",
                json={"session_id": str(session.id)}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["game_over"] is True
            assert data["game_status"] == "win"
            assert data["guess_result"]["correct"] is True

    @pytest.mark.asyncio
    async def test_next_turn_with_wrong_guess(self, client, db_session, sample_session_data):
        """Test turn with incorrect guess"""
        session = SessionModel(
            topic=sample_session_data["topic"],
            secret_word=sample_session_data["secret_word"],
            participants={
                p["id"]: {"provider": p["provider"], "role": p["role"], "name": p["name"]}
                for p in sample_session_data["participants"]
            }
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        receiver_id = sample_session_data["participants"][1]["id"]
        
        with patch('app.api.routes.agent_manager') as mock_manager:
            mock_manager.initialize_agents = AsyncMock(return_value=sample_session_data["secret_word"])
            mock_manager.run_conversation_turn = AsyncMock(return_value={
                "messages": [
                    {
                        "participant_id": receiver_id,
                        "comms": "Maybe it's destiny?",
                        "internal_thoughts": "Taking a guess.",
                        "guess": "destiny"
                    }
                ],
                "errors": []
            })
            
            response = await client.post(
                "/api/next-turn",
                json={"session_id": str(session.id)}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["game_over"] is False  # Still has tries
            assert data["guess_result"]["correct"] is False
            assert data["guess_result"]["tries_remaining"] == 2

    @pytest.mark.asyncio
    async def test_next_turn_exhaust_tries(self, client, db_session, sample_session_data):
        """Test that exhausting tries ends game"""
        session = SessionModel(
            topic=sample_session_data["topic"],
            secret_word=sample_session_data["secret_word"],
            participants={
                p["id"]: {"provider": p["provider"], "role": p["role"], "name": p["name"]}
                for p in sample_session_data["participants"]
            }
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        receiver_id = sample_session_data["participants"][1]["id"]
        
        # Make 3 wrong guesses
        with patch('app.api.routes.agent_manager') as mock_manager:
            mock_manager.initialize_agents = AsyncMock(return_value=sample_session_data["secret_word"])
            
            for i, wrong_guess in enumerate(["wrong1", "wrong2", "wrong3"], 1):
                mock_manager.run_conversation_turn = AsyncMock(return_value={
                    "messages": [
                        {
                            "participant_id": receiver_id,
                            "comms": f"Guess {i}",
                            "internal_thoughts": f"Try {i}",
                            "guess": wrong_guess
                        }
                    ],
                    "errors": []
                })
                
                response = await client.post(
                    "/api/next-turn",
                    json={"session_id": str(session.id)}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                if i < 3:
                    assert data["game_over"] is False
                else:
                    assert data["game_over"] is True
                    assert data["game_status"] == "loss"

    @pytest.mark.asyncio
    async def test_next_turn_all_agents_fail(self, client, db_session, sample_session_data):
        """Test handling when all agents fail to respond"""
        session = SessionModel(
            topic=sample_session_data["topic"],
            secret_word=sample_session_data["secret_word"],
            participants={
                p["id"]: {"provider": p["provider"], "role": p["role"], "name": p["name"]}
                for p in sample_session_data["participants"]
            }
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        with patch('app.api.routes.agent_manager') as mock_manager:
            mock_manager.initialize_agents = AsyncMock(return_value=sample_session_data["secret_word"])
            mock_manager.run_conversation_turn = AsyncMock(return_value={
                "messages": [],
                "errors": ["Agent 1 failed", "Agent 2 failed", "Agent 3 failed"]
            })
            
            response = await client.post(
                "/api/next-turn",
                json={"session_id": str(session.id)}
            )
            
            # The API raises HTTPException with 503, but it might be wrapped in 500 by FastAPI
            # Both are acceptable for this error condition
            assert response.status_code in [500, 503]
            assert "failed" in response.json()["detail"].lower()


@pytest.mark.integration
class TestSessionStatusEndpoint:
    """Test session status retrieval"""

    @pytest.mark.asyncio
    async def test_get_session_status_not_found(self, client):
        """Test getting status for non-existent session"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/session/{fake_uuid}/status")
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_session_status_success(self, client, db_session, sample_session_data):
        """Test getting session status"""
        from app.api.session_state import active_sessions, SessionState
        
        session = SessionModel(
            topic=sample_session_data["topic"],
            secret_word=sample_session_data["secret_word"],
            participants={
                p["id"]: {"provider": p["provider"], "role": p["role"], "name": p["name"]}
                for p in sample_session_data["participants"]
            }
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        # Add to active sessions
        receiver_id = sample_session_data["participants"][1]["id"]
        active_sessions[session.id] = SessionState(
            session_id=session.id,
            topic=sample_session_data["topic"],
            secret_word=sample_session_data["secret_word"],
            participants=sample_session_data["participants"],
            turn_number=1,
            tries_remaining={receiver_id: 3}
        )
        
        response = await client.get(f"/api/session/{session.id}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["turn_number"] == 1
        assert data["game_over"] is False
        assert receiver_id in data["tries_remaining"]


@pytest.mark.integration
class TestSessionHistoryEndpoint:
    """Test session history retrieval"""

    @pytest.mark.asyncio
    async def test_get_session_history_not_found(self, client):
        """Test getting history for non-existent session"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/session/{fake_uuid}/history")
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_session_history_empty(self, client, db_session, sample_session_data):
        """Test getting history for session with no messages"""
        session = SessionModel(
            topic=sample_session_data["topic"],
            secret_word=sample_session_data["secret_word"],
            participants={
                p["id"]: {"provider": p["provider"], "role": p["role"], "name": p["name"]}
                for p in sample_session_data["participants"]
            }
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        response = await client.get(f"/api/session/{session.id}/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == str(session.id)
        assert data["topic"] == sample_session_data["topic"]
        assert data["secret_word"] == sample_session_data["secret_word"]
        assert len(data["messages"]) == 0
        assert len(data["guesses"]) == 0

    @pytest.mark.asyncio
    async def test_get_session_history_with_messages(self, client, db_session, sample_session_data):
        """Test getting history with messages and guesses"""
        session = SessionModel(
            topic=sample_session_data["topic"],
            secret_word=sample_session_data["secret_word"],
            participants={
                p["id"]: {"provider": p["provider"], "role": p["role"], "name": p["name"]}
                for p in sample_session_data["participants"]
            }
        )
        db_session.add(session)
        await db_session.flush()
        
        # Add messages
        participant_ids = [p["id"] for p in sample_session_data["participants"]]
        message1 = MessageModel(
            session_id=session.id,
            turn=1,
            participant_id=participant_ids[0],
            comms="First message",
            internal_thoughts="First thoughts"
        )
        message2 = MessageModel(
            session_id=session.id,
            turn=1,
            participant_id=participant_ids[1],
            comms="Second message",
            internal_thoughts="Second thoughts"
        )
        db_session.add_all([message1, message2])
        
        # Add guess
        guess = GuessModel(
            session_id=session.id,
            turn=1,
            participant_id=participant_ids[1],
            guess="horizon",
            correct=True,
            tries_remaining=2
        )
        db_session.add(guess)
        
        await db_session.commit()
        await db_session.refresh(session)
        
        response = await client.get(f"/api/session/{session.id}/history")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 2
        assert len(data["guesses"]) == 1
        assert data["guesses"][0]["correct"] is True
        assert data["guesses"][0]["guess"] == "horizon"
