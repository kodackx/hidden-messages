"""Tests for edge cases and error handling"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
import json
from uuid import uuid4

from app.agents.agent_manager import HiddenMessageAgent
from app.agents.schemas import AgentOutput, AgentContext


@pytest.mark.unit
class TestJSONParsingEdgeCases:
    """Test edge cases in JSON parsing"""

    @pytest.mark.asyncio
    async def test_parse_json_with_extra_whitespace(self):
        """Test parsing JSON with extra whitespace"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = '''
        
        {
            "comms"  :  "Test"  ,
            "internal_thoughts": "Thoughts"  ,
            "guess": null
        }
        
        '''
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
        assert response.comms == "Test"

    @pytest.mark.asyncio
    async def test_parse_json_with_escaped_quotes(self):
        """Test parsing JSON with escaped quotes in content"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = {
            "comms": 'He said "hello" to everyone.',
            "internal_thoughts": "Using quotes",
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
        assert '"hello"' in response.comms

    @pytest.mark.asyncio
    async def test_parse_json_with_newlines_in_content(self):
        """Test parsing JSON with newlines in content"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = AgentOutput(
            comms="First line\nSecond line\nThird line",
            internal_thoughts="Multi\nline\nthoughts",
            guess=None
        )
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
        assert "\n" in response.comms

    @pytest.mark.asyncio
    async def test_parse_json_with_unicode(self):
        """Test parsing JSON with unicode characters"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = AgentOutput(
            comms="Testing 你好 émojis 🚀",
            internal_thoughts="Unicode test",
            guess=None
        )
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
        assert "你好" in response.comms
        assert "🚀" in response.comms


@pytest.mark.unit
class TestEmptyAndNullValues:
    """Test handling of empty and null values"""

    @pytest.mark.asyncio
    async def test_empty_comms_field(self):
        """Test handling empty comms field"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = AgentOutput(
            comms="",
            internal_thoughts="Some thoughts",
            guess=None
        )
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
        
        # Should return response but may be filtered out later
        assert error is None
        assert response.comms == ""

    @pytest.mark.asyncio
    async def test_guess_empty_string_vs_none(self):
        """Test difference between empty string guess and None"""
        manager = HiddenMessageAgent()
        
        # Test with None
        mock_agent_none = Mock()
        mock_result_none = Mock()
        mock_result_none.data = AgentOutput(
            comms="No guess",
            internal_thoughts="Not guessing",
            guess=None
        )
        mock_agent_none.run = AsyncMock(return_value=mock_result_none)
        
        context = AgentContext(
            agent_role="receiver",
            participant_id="test-1",
            topic="test",
            conversation_history=[],
            tries_remaining=3
        )
        
        manager.agents = {"test-1": mock_agent_none}
        manager.agent_meta = {"test-1": {"provider": "openai", "role": "receiver"}}
        
        response, error = await manager.get_agent_response(context)
        assert response.guess is None


@pytest.mark.unit
class TestLargeInputs:
    """Test handling of large inputs"""

    @pytest.mark.asyncio
    async def test_very_long_conversation_history(self):
        """Test handling very long conversation history"""
        manager = HiddenMessageAgent()
        
        # Create a long history
        long_history = [
            {
                "participant_id": f"agent-{i}",
                "participant_name": f"Agent {i}",
                "comms": f"Message {i} " * 100  # Long messages
            }
            for i in range(100)  # Many messages
        ]
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-id",
            topic="test",
            conversation_history=long_history
        )
        
        # Should not raise error when building prompt
        prompt = manager._build_prompt(context)
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    @pytest.mark.asyncio
    async def test_very_long_comms_message(self):
        """Test handling very long comms message"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_result = Mock()
        # 10,000 character message
        long_message = "This is a very long message. " * 333
        mock_result.data = AgentOutput(
            comms=long_message,
            internal_thoughts="Regular thoughts",
            guess=None
        )
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
        assert len(response.comms) > 9000


@pytest.mark.unit
class TestSpecialCharactersInInput:
    """Test handling special characters"""

    @pytest.mark.asyncio
    async def test_secret_word_with_special_chars(self):
        """Test secret word with special characters"""
        manager = HiddenMessageAgent()
        
        agents_config = {
            "agent-1": {"provider": "openai", "role": "communicator"}
        }
        
        secret = await manager.initialize_agents(
            secret_word="test-word_123",
            agents=agents_config
        )
        
        assert secret == "test-word_123"

    @pytest.mark.asyncio
    async def test_topic_with_special_chars(self):
        """Test topic with special characters"""
        manager = HiddenMessageAgent()
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-id",
            topic="AI & ML: The Future (2024-2025)",
            conversation_history=[]
        )
        
        prompt = manager._build_prompt(context)
        assert "AI & ML" in prompt


@pytest.mark.unit
class TestCaseInsensitiveGuesses:
    """Test case handling in guesses"""

    def test_guess_normalization_lowercase(self):
        """Test that guesses should be normalized for comparison"""
        secret = "Horizon"
        guess = "horizon"
        
        # Simulating the normalization in the API
        assert secret.lower().strip() == guess.lower().strip()

    def test_guess_normalization_uppercase(self):
        """Test uppercase guess matching"""
        secret = "horizon"
        guess = "HORIZON"
        
        assert secret.lower().strip() == guess.lower().strip()

    def test_guess_normalization_mixed_case(self):
        """Test mixed case guess matching"""
        secret = "HoRiZoN"
        guess = "horizon"
        
        assert secret.lower().strip() == guess.lower().strip()

    def test_guess_with_whitespace(self):
        """Test guess with surrounding whitespace"""
        secret = "horizon"
        guess = "  horizon  "
        
        assert secret.lower().strip() == guess.lower().strip()


@pytest.mark.unit
class TestErrorRecovery:
    """Test error recovery and graceful degradation"""

    @pytest.mark.asyncio
    async def test_partial_agent_failures(self, mock_agent_output):
        """Test that some agents can succeed even if others fail"""
        manager = HiddenMessageAgent()
        
        participants = [
            {"id": "success-1", "role": "communicator", "name": "Alice", "order": 0},
            {"id": "fail-1", "role": "receiver", "name": "Bob", "order": 1},
            {"id": "success-2", "role": "bystander", "name": "Charlie", "order": 2}
        ]
        
        # First agent succeeds
        mock_agent_1 = Mock()
        mock_result_1 = Mock()
        mock_result_1.data = mock_agent_output(comms="Success 1", internal_thoughts="OK")
        mock_agent_1.run = AsyncMock(return_value=mock_result_1)
        
        # Second agent fails
        mock_agent_2 = Mock()
        mock_agent_2.run = AsyncMock(side_effect=Exception("Network error"))
        
        # Third agent succeeds
        mock_agent_3 = Mock()
        mock_result_3 = Mock()
        mock_result_3.data = mock_agent_output(comms="Success 2", internal_thoughts="OK")
        mock_agent_3.run = AsyncMock(return_value=mock_result_3)
        
        manager.agents = {
            "success-1": mock_agent_1,
            "fail-1": mock_agent_2,
            "success-2": mock_agent_3
        }
        manager.agent_meta = {
            "success-1": {"provider": "openai", "role": "communicator"},
            "fail-1": {"provider": "anthropic", "role": "receiver"},
            "success-2": {"provider": "google-gla", "role": "bystander"}
        }
        
        result = await manager.run_conversation_turn(
            session_id=uuid4(),
            topic="test",
            secret_word="test",
            conversation_history=[],
            turn_number=1,
            tries_remaining={"fail-1": 3},
            participants=participants
        )
        
        # Should have 2 successful messages and 1 error
        assert len(result["messages"]) == 2
        assert len(result["errors"]) == 1
        assert "Bob" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of timeout errors"""
        manager = HiddenMessageAgent()
        
        mock_agent = Mock()
        mock_agent.run = AsyncMock(side_effect=TimeoutError("Request timeout"))
        
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
        assert "timeout" in error.lower()


@pytest.mark.unit
class TestPromptEdgeCases:
    """Test edge cases in prompt generation"""

    def test_prompt_with_empty_history(self):
        """Test prompt generation with empty history"""
        manager = HiddenMessageAgent()
        
        context = AgentContext(
            agent_role="communicator",
            participant_id="test-id",
            display_name="Alice",
            topic="test topic",
            secret_word="test",
            conversation_history=[],
            turn_number=1
        )
        
        prompt = manager._build_prompt(context)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "test topic" in prompt

    def test_prompt_without_display_name(self):
        """Test prompt when display name is None"""
        manager = HiddenMessageAgent()
        
        context = AgentContext(
            agent_role="bystander",
            participant_id="test-id-123",
            display_name=None,
            topic="test",
            conversation_history=[]
        )
        
        prompt = manager._build_prompt(context)
        # Should fall back to participant_id
        assert "test-id-123" in prompt

    def test_receiver_prompt_with_zero_tries(self):
        """Test receiver prompt when no tries remaining"""
        manager = HiddenMessageAgent()
        
        context = AgentContext(
            agent_role="receiver",
            participant_id="test-id",
            topic="test",
            conversation_history=[],
            tries_remaining=0
        )
        
        prompt = manager._build_prompt(context)
        assert "0" in prompt or "no" in prompt.lower()
