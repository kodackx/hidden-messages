"""Tests for agent manager and LLM response handling"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from app.agents.agent_manager import HiddenMessageAgent, SECRET_WORDS
from app.agents.schemas import AgentOutput, AgentContext


@pytest.mark.unit
class TestHiddenMessageAgent:
    """Test HiddenMessageAgent class"""

    def test_initialization(self):
        """Test agent manager initializes correctly"""
        manager = HiddenMessageAgent()
        assert manager.agents == {}
        assert manager.agent_meta == {}
        # model_settings might be dict or ModelSettings object depending on pydantic-ai version
        assert manager.model_settings is not None
        if isinstance(manager.model_settings, dict):
            assert manager.model_settings.get('temperature') == 0.3
        else:
            assert manager.model_settings.temperature == 0.3

    @pytest.mark.asyncio
    async def test_initialize_agents_with_secret_word(self):
        """Test initializing agents with provided secret word"""
        manager = HiddenMessageAgent()
        agents_config = {
            "agent-1": {"provider": "openai", "role": "communicator"},
            "agent-2": {"provider": "anthropic", "role": "receiver"},
            "agent-3": {"provider": "google-gla", "role": "bystander"}
        }
        
        secret = await manager.initialize_agents(
            secret_word="horizon",
            agents=agents_config
        )
        
        assert secret == "horizon"
        assert len(manager.agents) == 3
        assert len(manager.agent_meta) == 3

    @pytest.mark.asyncio
    async def test_initialize_agents_random_secret(self):
        """Test initializing agents with random secret word"""
        manager = HiddenMessageAgent()
        agents_config = {
            "agent-1": {"provider": "openai", "role": "communicator"}
        }
        
        secret = await manager.initialize_agents(agents=agents_config)
        
        assert secret in SECRET_WORDS
        assert len(manager.agents) == 1

    @pytest.mark.asyncio
    async def test_initialize_agents_no_config_raises(self):
        """Test that missing agents config raises error"""
        manager = HiddenMessageAgent()
        
        with pytest.raises(ValueError, match="agents configuration is required"):
            await manager.initialize_agents(agents=None)

    def test_get_model_string_openai(self):
        """Test model string generation for OpenAI"""
        manager = HiddenMessageAgent()
        model = manager._get_model_string("openai")
        assert model.startswith("openai:")

    def test_get_model_string_anthropic(self):
        """Test model string generation for Anthropic"""
        manager = HiddenMessageAgent()
        model = manager._get_model_string("anthropic")
        assert model.startswith("anthropic:")

    def test_get_model_string_google(self):
        """Test model string generation for Google"""
        manager = HiddenMessageAgent()
        model = manager._get_model_string("google")
        assert model.startswith("google:")

    def test_get_model_string_google_gla(self):
        """Test model string generation for Google GLA"""
        manager = HiddenMessageAgent()
        model = manager._get_model_string("google-gla")
        assert model.startswith("google-gla:")

    def test_get_model_string_invalid_provider(self):
        """Test that invalid provider raises error"""
        manager = HiddenMessageAgent()
        with pytest.raises(ValueError, match="Unsupported provider"):
            manager._get_model_string("invalid-provider")


@pytest.mark.unit
class TestPromptBuilding:
    """Test prompt building for different roles"""

    def test_build_communicator_prompt(self):
        """Test building prompt for communicator"""
        manager = HiddenMessageAgent()
        context = AgentContext(
            agent_role="communicator",
            participant_id="test-id",
            display_name="Alice",
            topic="space exploration",
            secret_word="horizon",
            conversation_history=[],
            turn_number=1
        )
        
        prompt = manager._build_prompt(context)
        
        assert "communicator" in prompt.lower() or "embed" in prompt.lower()
        assert "horizon" in prompt
        assert "space exploration" in prompt
        assert "Alice" in prompt

    def test_build_receiver_prompt(self):
        """Test building prompt for receiver"""
        manager = HiddenMessageAgent()
        context = AgentContext(
            agent_role="receiver",
            participant_id="test-id",
            display_name="Bob",
            topic="technology",
            conversation_history=[],
            turn_number=1,
            tries_remaining=3
        )
        
        prompt = manager._build_prompt(context)
        
        assert "receiver" in prompt.lower() or "detect" in prompt.lower() or "guess" in prompt.lower()
        assert "technology" in prompt
        assert "Bob" in prompt
        assert "3" in prompt or "tries" in prompt.lower()

    def test_build_bystander_prompt(self):
        """Test building prompt for bystander"""
        manager = HiddenMessageAgent()
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-id",
            display_name="Charlie",
            topic="artificial intelligence",
            conversation_history=[],
            turn_number=1
        )
        
        prompt = manager._build_prompt(context)
        
        assert "bystander" in prompt.lower() or "natural" in prompt.lower()
        assert "artificial intelligence" in prompt
        assert "Charlie" in prompt


@pytest.mark.unit
class TestAgentResponseParsing:
    """Test agent response parsing and error handling"""

    @pytest.mark.asyncio
    async def test_get_agent_response_success(self, mock_agent_output):
        """Test successful agent response parsing"""
        manager = HiddenMessageAgent()
        
        # Create a mock agent
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = mock_agent_output(
            comms="Test message",
            internal_thoughts="Test thoughts"
        )
        mock_agent.run = AsyncMock(return_value=mock_result)
        
        # Initialize with mock
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-id",
            topic="test topic",
            conversation_history=[]
        )
        
        manager.agents = {"test-id": mock_agent}
        manager.agent_meta = {"test-id": {"provider": "openai", "role": "bystander"}}
        
        response, error = await manager.get_agent_response(context)
        
        assert error is None
        assert response is not None
        assert response.comms == "Test message"
        assert response.internal_thoughts == "Test thoughts"

    @pytest.mark.asyncio
    async def test_get_agent_response_with_guess(self, mock_agent_output):
        """Test parsing response with a guess"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = mock_agent_output(
            comms="I think I know",
            internal_thoughts="Confident about this",
            guess="horizon"
        )
        mock_agent.run = AsyncMock(return_value=mock_result)
        
        context = AgentContext(
            agent_role="receiver",
            participant_id="test-id",
            topic="test",
            conversation_history=[],
            tries_remaining=3
        )
        
        manager.agents = {"test-id": mock_agent}
        manager.agent_meta = {"test-id": {"provider": "anthropic", "role": "receiver"}}
        
        response, error = await manager.get_agent_response(context)
        
        assert error is None
        assert response.guess == "horizon"

    @pytest.mark.asyncio
    async def test_get_agent_response_dict_output(self):
        """Test parsing dict output from agent"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = {
            "comms": "Test from dict",
            "internal_thoughts": "Dict thoughts",
            "guess": None
        }
        mock_agent.run = AsyncMock(return_value=mock_result)
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-id",
            topic="test",
            conversation_history=[]
        )
        
        manager.agents = {"test-id": mock_agent}
        manager.agent_meta = {"test-id": {"provider": "openai", "role": "bystander"}}
        
        response, error = await manager.get_agent_response(context)
        
        assert error is None
        assert response.comms == "Test from dict"

    @pytest.mark.asyncio
    async def test_get_agent_response_json_string(self):
        """Test parsing JSON string output from agent"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = '{"comms": "JSON test", "internal_thoughts": "JSON thoughts", "guess": null}'
        mock_agent.run = AsyncMock(return_value=mock_result)
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-id",
            topic="test",
            conversation_history=[]
        )
        
        manager.agents = {"test-id": mock_agent}
        manager.agent_meta = {"test-id": {"provider": "openai", "role": "bystander"}}
        
        response, error = await manager.get_agent_response(context)
        
        assert error is None
        assert response.comms == "JSON test"

    @pytest.mark.asyncio
    async def test_get_agent_response_json_with_markdown(self):
        """Test parsing JSON wrapped in markdown code blocks"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = '''```json
{
    "comms": "Markdown wrapped",
    "internal_thoughts": "Code block",
    "guess": null
}
```'''
        mock_agent.run = AsyncMock(return_value=mock_result)
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-id",
            topic="test",
            conversation_history=[]
        )
        
        manager.agents = {"test-id": mock_agent}
        manager.agent_meta = {"test-id": {"provider": "anthropic", "role": "bystander"}}
        
        response, error = await manager.get_agent_response(context)
        
        assert error is None
        assert response.comms == "Markdown wrapped"

    @pytest.mark.asyncio
    async def test_get_agent_response_api_error(self):
        """Test handling API errors"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_agent.run = AsyncMock(side_effect=Exception("API Error"))
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-id",
            topic="test",
            conversation_history=[]
        )
        
        manager.agents = {"test-id": mock_agent}
        manager.agent_meta = {"test-id": {"provider": "openai", "role": "bystander"}}
        
        response, error = await manager.get_agent_response(context)
        
        assert response is None
        assert error is not None
        assert "API Error" in error

    @pytest.mark.asyncio
    async def test_get_agent_response_invalid_output_type(self):
        """Test handling invalid output type"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = 12345  # Invalid: not AgentOutput, dict, or string
        mock_agent.run = AsyncMock(return_value=mock_result)
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-id",
            topic="test",
            conversation_history=[]
        )
        
        manager.agents = {"test-id": mock_agent}
        manager.agent_meta = {"test-id": {"provider": "openai", "role": "bystander"}}
        
        response, error = await manager.get_agent_response(context)
        
        assert response is None
        assert error is not None


@pytest.mark.unit
class TestConversationTurn:
    """Test running a complete conversation turn"""

    @pytest.mark.asyncio
    async def test_run_conversation_turn_success(self, mock_agent_output):
        """Test successful conversation turn with all agents"""
        manager = HiddenMessageAgent()
        
        # Mock agents
        participants = [
            {"id": "comm-1", "role": "communicator", "name": "Alice", "order": 0},
            {"id": "recv-1", "role": "receiver", "name": "Bob", "order": 1},
            {"id": "byst-1", "role": "bystander", "name": "Charlie", "order": 2}
        ]
        
        for p in participants:
            mock_agent = Mock()
            mock_result = Mock()
            mock_result.data = mock_agent_output(
                comms=f"Message from {p['name']}",
                internal_thoughts=f"Thoughts from {p['name']}"
            )
            mock_agent.run = AsyncMock(return_value=mock_result)
            manager.agents[p["id"]] = mock_agent
            manager.agent_meta[p["id"]] = {"provider": "openai", "role": p["role"]}
        
        result = await manager.run_conversation_turn(
            topic="test topic",
            secret_word="horizon",
            conversation_history=[],
            turn_number=1,
            tries_remaining={"recv-1": 3},
            participants=participants
        )
        
        assert len(result["messages"]) == 3
        assert len(result["errors"]) == 0
        assert all("comms" in msg for msg in result["messages"])

    @pytest.mark.asyncio
    async def test_run_conversation_turn_with_guess(self, mock_agent_output):
        """Test conversation turn where receiver makes a guess"""
        manager = HiddenMessageAgent()
        
        participants = [
            {"id": "comm-1", "role": "communicator", "name": "Alice", "order": 0},
            {"id": "recv-1", "role": "receiver", "name": "Bob", "order": 1}
        ]
        
        # Communicator response
        mock_agent_comm = Mock()
        mock_result_comm = Mock()
        mock_result_comm.data = mock_agent_output(comms="Normal message", internal_thoughts="Thoughts")
        mock_agent_comm.run = AsyncMock(return_value=mock_result_comm)
        
        # Receiver response with guess
        mock_agent_recv = Mock()
        mock_result_recv = Mock()
        mock_result_recv.data = mock_agent_output(
            comms="I have an idea",
            internal_thoughts="I think it's horizon",
            guess="horizon"
        )
        mock_agent_recv.run = AsyncMock(return_value=mock_result_recv)
        
        manager.agents = {
            "comm-1": mock_agent_comm,
            "recv-1": mock_agent_recv
        }
        manager.agent_meta = {
            "comm-1": {"provider": "openai", "role": "communicator"},
            "recv-1": {"provider": "anthropic", "role": "receiver"}
        }
        
        result = await manager.run_conversation_turn(
            topic="test topic",
            secret_word="horizon",
            conversation_history=[],
            turn_number=1,
            tries_remaining={"recv-1": 3},
            participants=participants
        )
        
        assert len(result["messages"]) == 2
        assert result["messages"][1]["guess"] == "horizon"

    @pytest.mark.asyncio
    async def test_run_conversation_turn_agent_failure(self, mock_agent_output):
        """Test turn continues when one agent fails"""
        manager = HiddenMessageAgent()
        
        participants = [
            {"id": "comm-1", "role": "communicator", "name": "Alice", "order": 0},
            {"id": "recv-1", "role": "receiver", "name": "Bob", "order": 1}
        ]
        
        # First agent succeeds
        mock_agent_1 = Mock()
        mock_result_1 = Mock()
        mock_result_1.data = mock_agent_output(comms="Success", internal_thoughts="OK")
        mock_agent_1.run = AsyncMock(return_value=mock_result_1)
        
        # Second agent fails
        mock_agent_2 = Mock()
        mock_agent_2.run = AsyncMock(side_effect=Exception("API timeout"))
        
        manager.agents = {
            "comm-1": mock_agent_1,
            "recv-1": mock_agent_2
        }
        manager.agent_meta = {
            "comm-1": {"provider": "openai", "role": "communicator"},
            "recv-1": {"provider": "anthropic", "role": "receiver"}
        }
        
        result = await manager.run_conversation_turn(
            topic="test topic",
            secret_word="horizon",
            conversation_history=[],
            turn_number=1,
            tries_remaining={"recv-1": 3},
            participants=participants
        )
        
        assert len(result["messages"]) == 1  # Only successful agent
        assert len(result["errors"]) == 1  # One error recorded
        assert "Bob" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_run_conversation_turn_respects_order(self, mock_agent_output):
        """Test that agents speak in correct order"""
        manager = HiddenMessageAgent()
        
        participants = [
            {"id": "third", "role": "bystander", "name": "C", "order": 2},
            {"id": "first", "role": "communicator", "name": "A", "order": 0},
            {"id": "second", "role": "receiver", "name": "B", "order": 1}
        ]
        
        call_order = []
        
        for p in participants:
            mock_agent = Mock()
            mock_result = Mock()
            mock_result.data = mock_agent_output(comms=f"From {p['name']}", internal_thoughts="OK")
            
            async def make_call(name):
                async def _call(*args, **kwargs):
                    call_order.append(name)
                    return mock_result
                return _call
            
            mock_agent.run = await make_call(p['name'])
            manager.agents[p["id"]] = mock_agent
            manager.agent_meta[p["id"]] = {"provider": "openai", "role": p["role"]}
        
        result = await manager.run_conversation_turn(
            topic="test",
            secret_word="test",
            conversation_history=[],
            turn_number=1,
            tries_remaining={"second": 3},
            participants=participants
        )
        
        # Should be called in order: A, B, C
        assert result["messages"][0]["participant_id"] == "first"
        assert result["messages"][1]["participant_id"] == "second"
        assert result["messages"][2]["participant_id"] == "third"
