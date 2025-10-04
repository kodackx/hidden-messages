"""End-to-end tests with real LLM API calls

These tests make actual API calls to LLM providers and are:
- Slow (can take 10-30 seconds per test)
- Expensive (uses real API tokens)
- Require valid API keys in environment

Run these tests explicitly with:
    pytest -m e2e
    pytest tests/test_e2e_real_llm.py
    make test-e2e  (if added to Makefile)

Skip these tests by default:
    pytest  (will skip all e2e tests)
    pytest -m "not e2e"
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import os

from app.main import app
from app.models import SessionModel, MessageModel, GuessModel
from app.agents.agent_manager import HiddenMessageAgent
from app.agents.schemas import AgentContext


pytestmark = pytest.mark.e2e  # Mark all tests in this file as e2e


@pytest_asyncio.fixture
async def e2e_client(db_session):
    """Create test client for e2e tests"""
    from app.models.database import get_db
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def check_api_keys():
    """Check if API keys are available"""
    available_providers = []
    
    if os.getenv("OPENAI_API_KEY"):
        available_providers.append("openai")
    if os.getenv("ANTHROPIC_API_KEY"):
        available_providers.append("anthropic")
    if os.getenv("GOOGLE_API_KEY"):
        available_providers.append("google")
    
    if not available_providers:
        pytest.skip("No LLM API keys found in environment")
    
    return available_providers


class TestRealLLMCalls:
    """Test real LLM API calls to debug issues"""

    @pytest.mark.asyncio
    async def test_openai_direct_agent_call(self, check_api_keys):
        """Test direct OpenAI agent call to isolate issues"""
        if "openai" not in check_api_keys:
            pytest.skip("OPENAI_API_KEY not found")
        
        manager = HiddenMessageAgent()
        
        # Initialize with a simple OpenAI agent
        agents_config = {
            "test-agent": {"provider": "openai", "role": "bystander"}
        }
        
        secret_word = await manager.initialize_agents(
            secret_word="test",
            agents=agents_config
        )
        
        assert secret_word == "test"
        
        # Create a simple context
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-agent",
            display_name="Test Agent",
            topic="testing AI systems",
            conversation_history=[],
            turn_number=1
        )
        
        # Make the actual API call
        print("\n🔄 Making real OpenAI API call...")
        response, error = await manager.get_agent_response(context)
        
        # Debug output
        if error:
            print(f"❌ Error occurred: {error}")
            pytest.fail(f"OpenAI API call failed: {error}")
        else:
            print(f"✅ Success!")
            print(f"   Comms: {response.comms[:100]}...")
            print(f"   Thoughts: {response.internal_thoughts[:100]}...")
        
        assert response is not None, "Response should not be None"
        assert response.comms, "Comms should not be empty"
        assert response.internal_thoughts, "Internal thoughts should not be empty"
        assert response.guess is None, "Bystander should not make guesses"

    @pytest.mark.asyncio
    async def test_openai_communicator_role(self, check_api_keys):
        """Test OpenAI agent in communicator role with secret word"""
        if "openai" not in check_api_keys:
            pytest.skip("OPENAI_API_KEY not found")
        
        manager = HiddenMessageAgent()
        
        agents_config = {
            "communicator": {"provider": "openai", "role": "communicator"}
        }
        
        secret_word = await manager.initialize_agents(
            secret_word="horizon",
            agents=agents_config
        )
        
        context = AgentContext(
            agent_role="communicator",
            participant_id="communicator",
            display_name="Alice",
            topic="space exploration",
            secret_word="horizon",  # Secret word provided to communicator
            conversation_history=[],
            turn_number=1
        )
        
        print("\n🔄 Testing communicator role with secret word 'horizon'...")
        response, error = await manager.get_agent_response(context)
        
        if error:
            print(f"❌ Error: {error}")
            pytest.fail(f"Communicator call failed: {error}")
        
        print(f"✅ Success!")
        print(f"   Comms: {response.comms}")
        print(f"   Thoughts: {response.internal_thoughts[:100]}...")
        
        assert response is not None
        assert response.comms
        assert response.internal_thoughts

    @pytest.mark.asyncio
    async def test_openai_receiver_role(self, check_api_keys):
        """Test OpenAI agent in receiver role"""
        if "openai" not in check_api_keys:
            pytest.skip("OPENAI_API_KEY not found")
        
        manager = HiddenMessageAgent()
        
        agents_config = {
            "receiver": {"provider": "openai", "role": "receiver"}
        }
        
        await manager.initialize_agents(secret_word="test", agents=agents_config)
        
        # Give receiver some conversation history to analyze
        context = AgentContext(
            agent_role="receiver",
            participant_id="receiver",
            display_name="Bob",
            topic="space exploration",
            conversation_history=[
                {
                    "participant_id": "alice",
                    "participant_name": "Alice",
                    "comms": "I think we should focus on the distant horizon of Mars."
                }
            ],
            turn_number=2,
            tries_remaining=3
        )
        
        print("\n🔄 Testing receiver role with conversation history...")
        response, error = await manager.get_agent_response(context)
        
        if error:
            print(f"❌ Error: {error}")
            pytest.fail(f"Receiver call failed: {error}")
        
        print(f"✅ Success!")
        print(f"   Comms: {response.comms}")
        print(f"   Guess: {response.guess}")
        
        assert response is not None
        assert response.comms
        # Receiver might or might not make a guess
        if response.guess:
            print(f"   🎯 Receiver made a guess: {response.guess}")

    @pytest.mark.asyncio
    async def test_anthropic_agent_call(self, check_api_keys):
        """Test Anthropic API call"""
        if "anthropic" not in check_api_keys:
            pytest.skip("ANTHROPIC_API_KEY not found")
        
        manager = HiddenMessageAgent()
        
        agents_config = {
            "test-agent": {"provider": "anthropic", "role": "bystander"}
        }
        
        await manager.initialize_agents(secret_word="test", agents=agents_config)
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-agent",
            display_name="Claude",
            topic="artificial intelligence",
            conversation_history=[],
            turn_number=1
        )
        
        print("\n🔄 Making real Anthropic API call...")
        response, error = await manager.get_agent_response(context)
        
        if error:
            print(f"❌ Error: {error}")
            pytest.fail(f"Anthropic API call failed: {error}")
        
        print(f"✅ Success!")
        print(f"   Comms: {response.comms[:100]}...")
        
        assert response is not None
        assert response.comms

    @pytest.mark.asyncio
    async def test_google_agent_call(self, check_api_keys):
        """Test Google/Gemini API call"""
        if "google" not in check_api_keys:
            pytest.skip("GOOGLE_API_KEY not found")
        
        manager = HiddenMessageAgent()
        
        agents_config = {
            "test-agent": {"provider": "google-gla", "role": "bystander"}
        }
        
        await manager.initialize_agents(secret_word="test", agents=agents_config)
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-agent",
            display_name="Gemini",
            topic="machine learning",
            conversation_history=[],
            turn_number=1
        )
        
        print("\n🔄 Making real Google/Gemini API call...")
        response, error = await manager.get_agent_response(context)
        
        if error:
            print(f"❌ Error: {error}")
            pytest.fail(f"Google API call failed: {error}")
        
        print(f"✅ Success!")
        print(f"   Comms: {response.comms[:100]}...")
        
        assert response is not None
        assert response.comms


class TestFullE2ESession:
    """Test complete session flow with real LLM calls"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_complete_session_openai_only(self, e2e_client, check_api_keys, db_session):
        """Test a complete game session with OpenAI (all 3 agents)
        
        This is a full end-to-end test that will:
        1. Create a session
        2. Run multiple turns with real LLM calls
        3. Verify the game flows correctly
        
        WARNING: This test is SLOW and EXPENSIVE!
        """
        if "openai" not in check_api_keys:
            pytest.skip("OPENAI_API_KEY not found")
        
        print("\n" + "="*60)
        print("🎮 Starting FULL E2E session with real OpenAI calls")
        print("="*60)
        
        # Start session
        response = await e2e_client.post(
            "/api/start-session",
            json={
                "topic": "space exploration",
                "secret_word": "horizon",
                "participants": [
                    {
                        "name": "Alice",
                        "provider": "openai",
                        "role": "communicator",
                        "order": 0
                    },
                    {
                        "name": "Bob",
                        "provider": "openai",
                        "role": "receiver",
                        "order": 1
                    },
                    {
                        "name": "Charlie",
                        "provider": "openai",
                        "role": "bystander",
                        "order": 2
                    }
                ]
            }
        )
        
        assert response.status_code == 200
        session_data = response.json()
        session_id = session_data["session_id"]
        
        print(f"\n✅ Session created: {session_id}")
        print(f"   Topic: space exploration")
        print(f"   Secret: horizon")
        
        # Run turns until game ends or max turns reached
        max_turns = 5
        for turn in range(1, max_turns + 1):
            print(f"\n{'='*60}")
            print(f"🔄 Turn {turn}: Making real LLM calls to all 3 agents...")
            print(f"{'='*60}")
            
            response = await e2e_client.post(
                "/api/next-turn",
                json={"session_id": session_id}
            )
            
            if response.status_code != 200:
                print(f"\n❌ Turn {turn} failed!")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {response.json()}")
                pytest.fail(f"Turn {turn} failed with status {response.status_code}")
            
            turn_data = response.json()
            
            # Display messages
            for msg in turn_data["messages"]:
                print(f"\n👤 {msg['participant_name']} ({msg['participant_role']}):")
                print(f"   💬 {msg['comms']}")
                print(f"   🧠 {msg['internal_thoughts'][:80]}...")
            
            # Check for guess
            if turn_data.get("guess_result"):
                guess = turn_data["guess_result"]
                print(f"\n🎯 Guess made: '{guess.get('guess', 'N/A')}'")
                print(f"   Correct: {guess['correct']}")
                print(f"   Tries remaining: {guess['tries_remaining']}")
            
            # Check if game ended
            if turn_data["game_over"]:
                print(f"\n{'='*60}")
                print(f"🏁 Game Over! Status: {turn_data['game_status']}")
                print(f"{'='*60}")
                break
        
        # Verify session was created and turns were executed
        assert turn >= 1, "At least one turn should have been executed"
        print(f"\n✅ E2E test completed successfully after {turn} turns")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_mixed_providers_session(self, e2e_client, check_api_keys, db_session):
        """Test session with different providers for each agent
        
        This tests cross-model communication
        """
        available = check_api_keys
        
        if len(available) < 2:
            pytest.skip("Need at least 2 different LLM providers for this test")
        
        # Assign different providers to different roles
        provider_map = {
            "communicator": available[0] if len(available) > 0 else "openai",
            "receiver": available[1] if len(available) > 1 else available[0],
            "bystander": available[2] if len(available) > 2 else available[0]
        }
        
        print(f"\n🌐 Testing cross-model communication:")
        print(f"   Communicator: {provider_map['communicator']}")
        print(f"   Receiver: {provider_map['receiver']}")
        print(f"   Bystander: {provider_map['bystander']}")
        
        response = await e2e_client.post(
            "/api/start-session",
            json={
                "topic": "artificial intelligence",
                "secret_word": "neural",
                "participants": [
                    {
                        "name": "Comm",
                        "provider": provider_map["communicator"],
                        "role": "communicator",
                        "order": 0
                    },
                    {
                        "name": "Recv",
                        "provider": provider_map["receiver"],
                        "role": "receiver",
                        "order": 1
                    },
                    {
                        "name": "Byst",
                        "provider": provider_map["bystander"],
                        "role": "bystander",
                        "order": 2
                    }
                ]
            }
        )
        
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        
        # Run one turn to test cross-model interaction
        print("\n🔄 Running one turn with mixed providers...")
        response = await e2e_client.post(
            "/api/next-turn",
            json={"session_id": session_id}
        )
        
        if response.status_code != 200:
            pytest.fail(f"Turn failed: {response.json()}")
        
        turn_data = response.json()
        assert len(turn_data["messages"]) == 3, "All three agents should respond"
        
        print("✅ Cross-model communication successful!")
        for msg in turn_data["messages"]:
            print(f"   {msg['participant_name']}: {msg['comms'][:50]}...")



