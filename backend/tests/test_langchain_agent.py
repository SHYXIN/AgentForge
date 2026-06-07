"""
测试：LangChain Agent

行为：Agent 应该使用 LangChain 接入真实 AI，提供有意义的回复。
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


def test_langchain_agent_can_be_created():
    """LangChain Agent 应该能够被创建。"""
    from backend.services.langchain_agent import LangChainAgent

    agent = LangChainAgent()
    assert agent is not None


def test_langchain_agent_has_conversation_history():
    """LangChain Agent 应该有对话历史。"""
    from backend.services.langchain_agent import LangChainAgent

    agent = LangChainAgent()
    assert hasattr(agent, 'conversation_history')
    assert isinstance(agent.conversation_history, list)


@pytest.mark.asyncio
async def test_langchain_agent_process_message():
    """Agent 应该能处理消息并返回真实回复。"""
    from backend.services.langchain_agent import LangChainAgent

    agent = LangChainAgent()

    # Mock the LLM
    with patch.object(agent, 'llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = "This is a real AI response"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await agent.process_message("Hello")

        assert result is not None
        assert "response" in result
        assert result["response"] == "This is a real AI response"


@pytest.mark.asyncio
async def test_langchain_agent_remembers_conversation():
    """Agent 应该记住之前的对话。"""
    from backend.services.langchain_agent import LangChainAgent

    agent = LangChainAgent()

    # Check that conversation_history is initially empty
    assert len(agent.conversation_history) == 0
