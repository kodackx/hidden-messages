"""Simplified end-to-end tests with real LLM API calls

This is a simplified approach to e2e testing that avoids over-engineering:
1. Quick provider smoke tests - verify each LLM provider responds
2. Session creation - create a game session
3. Single turn test - run one complete turn with real LLMs

These tests:
- Make real API calls (slow, uses tokens)
- Require valid API keys in environment
- Are skipped if keys are missing

Run with: pytest -m e2e -v -s
"""
import pytest
import os
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.agents.agent_manager import HiddenMessageAgent
from app.agents.schemas import AgentContext

pytestmark = pytest.mark.e2e


def check_provider_available(provider: str) -> bool:
    """Check if provider API key is available"""
    key_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "google-gla": "GOOGLE_API_KEY"
    }
    return bool(os.getenv(key_map.get(provider, "")))


@pytest.fixture
def available_providers():
    """Get list of available LLM providers based on API keys"""
    providers = []
    if check_provider_available("openai"):
        providers.append("openai")
    if check_provider_available("anthropic"):
        providers.append("anthropic")
    if check_provider_available("google-gla"):
        providers.append("google-gla")
    
    if not providers:
        pytest.skip("No LLM API keys found. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY")
    
    return providers


@pytest.fixture
async def client(db_session):
    """Test client with database override"""
    from app.models.database import get_db
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


class TestProviderSmokeTests:
    """Quick sanity check that each provider can respond"""

    @pytest.mark.asyncio
    async def test_openai_smoke(self, available_providers):
        """Quick test that OpenAI provider responds"""
        if "openai" not in available_providers:
            pytest.skip("OpenAI not available")
        
        manager = HiddenMessageAgent()
        agents_config = {"test": {"provider": "openai", "role": "bystander"}}
        await manager.initialize_agents(secret_word="test", agents=agents_config)
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test",
            display_name="TestAgent",
            topic="testing",
            conversation_history=[],
            turn_number=1
        )
        
        print("\n[OpenAI] Making API call...")
        response, error = await manager.get_agent_response(context)
        
        assert error is None, f"OpenAI call failed: {error}"
        assert response is not None
        assert response.comms
        print(f"[OpenAI] ✓ Response received: {response.comms[:50]}...")

    @pytest.mark.asyncio
    async def test_anthropic_smoke(self, available_providers):
        """Quick test that Anthropic provider responds"""
        if "anthropic" not in available_providers:
            pytest.skip("Anthropic not available")
        
        manager = HiddenMessageAgent()
        agents_config = {"test": {"provider": "anthropic", "role": "bystander"}}
        await manager.initialize_agents(secret_word="test", agents=agents_config)
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test",
            display_name="TestAgent",
            topic="testing",
            conversation_history=[],
            turn_number=1
        )
        
        print("\n[Anthropic] Making API call...")
        response, error = await manager.get_agent_response(context)
        
        assert error is None, f"Anthropic call failed: {error}"
        assert response is not None
        assert response.comms
        print(f"[Anthropic] ✓ Response received: {response.comms[:50]}...")

    @pytest.mark.asyncio
    async def test_google_smoke(self, available_providers):
        """Quick test that Google/Gemini provider responds"""
        if "google-gla" not in available_providers:
            pytest.skip("Google not available")
        
        manager = HiddenMessageAgent()
        agents_config = {"test": {"provider": "google-gla", "role": "bystander"}}
        await manager.initialize_agents(secret_word="test", agents=agents_config)
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test",
            display_name="TestAgent",
            topic="testing",
            conversation_history=[],
            turn_number=1
        )
        
        print("\n[Google] Making API call...")
        response, error = await manager.get_agent_response(context)
        
        assert error is None, f"Google call failed: {error}"
        assert response is not None
        assert response.comms
        print(f"[Google] ✓ Response received: {response.comms[:50]}...")


class TestSessionCreation:
    """Test that we can create a game session"""

    @pytest.mark.asyncio
    async def test_create_session(self, client, available_providers, db_session):
        """Create a basic game session"""
        provider = available_providers[0]  # Use first available provider
        
        response = await client.post(
            "/api/start-session",
            json={
                "topic": "space exploration",
                "secret_word": "horizon",
                "participants": [
                    {"name": "Alice", "provider": provider, "role": "communicator", "order": 0},
                    {"name": "Bob", "provider": provider, "role": "receiver", "order": 1},
                    {"name": "Charlie", "provider": provider, "role": "bystander", "order": 2}
                ]
            }
        )
        
        assert response.status_code == 200, f"Failed to create session: {response.json()}"
        
        data = response.json()
        assert "session_id" in data
        assert data["topic"] == "space exploration"
        assert len(data["participants"]) == 3
        
        print(f"\n✓ Session created: {data['session_id']}")
        print(f"  Provider: {provider}")
        print(f"  Topic: {data['topic']}")


class TestSingleTurn:
    """Test running a single turn with real LLMs"""

    @pytest.mark.asyncio
    async def test_single_turn_flow(self, client, available_providers, db_session):
        """Complete flow: create session + run one turn with real LLMs"""
        provider = available_providers[0]
        
        # 1. Create session
        print(f"\n[Turn Test] Creating session with {provider}...")
        create_response = await client.post(
            "/api/start-session",
            json={
                "topic": "artificial intelligence",
                "secret_word": "neural",
                "participants": [
                    {"name": "Alice", "provider": provider, "role": "communicator", "order": 0},
                    {"name": "Bob", "provider": provider, "role": "receiver", "order": 1},
                    {"name": "Charlie", "provider": provider, "role": "bystander", "order": 2}
                ]
            }
        )
        
        assert create_response.status_code == 200
        session_id = create_response.json()["session_id"]
        print(f"[Turn Test] ✓ Session created: {session_id}")
        
        # 2. Run one turn (makes real LLM calls to all 3 agents)
        print(f"[Turn Test] Running turn 1 (3 real LLM calls)...")
        turn_response = await client.post(
            "/api/next-turn",
            json={"session_id": session_id}
        )
        
        assert turn_response.status_code == 200, f"Turn failed: {turn_response.json()}"
        
        turn_data = turn_response.json()
        
        # 3. Verify turn results
        assert "messages" in turn_data
        assert len(turn_data["messages"]) == 3, "Should have 3 agent responses"
        
        print(f"[Turn Test] ✓ Turn completed successfully\n")
        
        # Display messages
        for msg in turn_data["messages"]:
            print(f"  {msg['participant_name']} ({msg['participant_role']}):")
            print(f"    {msg['comms'][:80]}...")
        
        # Check if receiver made a guess
        if turn_data.get("guess_result"):
            guess = turn_data["guess_result"]
            print(f"\n  Guess: '{guess.get('guess')}' - {'✓ Correct!' if guess['correct'] else '✗ Incorrect'}")
        
        # Verify each agent responded appropriately
        roles_found = {msg["participant_role"] for msg in turn_data["messages"]}
        assert "communicator" in roles_found
        assert "receiver" in roles_found
        assert "bystander" in roles_found


class TestCrossProviderCommunication:
    """Test communication between different LLM providers"""

    @pytest.mark.asyncio
    async def test_mixed_providers_if_available(self, client, available_providers, db_session):
        """Test cross-provider communication if multiple providers available"""
        if len(available_providers) < 2:
            pytest.skip("Need at least 2 providers for cross-provider test")
        
        # Use different providers for each role
        providers = {
            "communicator": available_providers[0],
            "receiver": available_providers[1],
            "bystander": available_providers[0]  # Reuse first if only 2 available
        }
        
        print(f"\n[Cross-Provider] Testing communication:")
        print(f"  Communicator: {providers['communicator']}")
        print(f"  Receiver: {providers['receiver']}")
        print(f"  Bystander: {providers['bystander']}")
        
        # Create session with mixed providers
        create_response = await client.post(
            "/api/start-session",
            json={
                "topic": "machine learning",
                "secret_word": "training",
                "participants": [
                    {"name": "Alice", "provider": providers["communicator"], "role": "communicator", "order": 0},
                    {"name": "Bob", "provider": providers["receiver"], "role": "receiver", "order": 1},
                    {"name": "Charlie", "provider": providers["bystander"], "role": "bystander", "order": 2}
                ]
            }
        )
        
        assert create_response.status_code == 200
        session_id = create_response.json()["session_id"]
        
        # Run one turn with mixed providers
        print(f"[Cross-Provider] Running turn with mixed providers...")
        turn_response = await client.post(
            "/api/next-turn",
            json={"session_id": session_id}
        )
        
        assert turn_response.status_code == 200
        turn_data = turn_response.json()
        assert len(turn_data["messages"]) == 3
        
        print(f"[Cross-Provider] ✓ Cross-provider communication successful!")
