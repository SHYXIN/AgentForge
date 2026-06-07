"""
测试：Service 层依赖注入集成

行为：Service 应该能够通过依赖注入获取 Repository。
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def test_langchain_agent_can_be_created():
    """LangChain Agent 应该能够被创建。"""
    from backend.services.langchain_agent import LangChainAgent

    agent = LangChainAgent()
    assert agent is not None


def test_langchain_agent_can_process_message():
    """LangChain Agent 应该能够处理消息。"""
    import asyncio
    from backend.services.langchain_agent import LangChainAgent

    async def test():
        # Mock the ChatOpenAI class to avoid API call
        with patch('backend.services.langchain_agent.ChatOpenAI') as mock_llm_class:
            mock_llm = AsyncMock()
            mock_response = MagicMock()
            mock_response.content = "Test response"
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm

            agent = LangChainAgent()
            result = await agent.process_message("你好")

            assert result is not None
            assert "response" in result
            assert "agent_thoughts" in result
            assert "conversation_id" in result

    asyncio.run(test())
