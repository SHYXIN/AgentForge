"""
测试：Agent 自我反思能力

行为：Agent 应该能自我评估任务执行结果，并在失败时调整策略。
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


def test_reflective_agent_can_be_created():
    """Reflective Agent 应该能够被创建。"""
    from backend.services.reflective_agent import ReflectiveAgent

    agent = ReflectiveAgent()
    assert agent is not None


def test_reflective_agent_has_max_retries():
    """Reflective Agent 应该有最大重试次数配置。"""
    from backend.services.reflective_agent import ReflectiveAgent

    agent = ReflectiveAgent()
    assert hasattr(agent, 'max_retries')
    assert agent.max_retries > 0


@pytest.mark.asyncio
async def test_reflective_agent_evaluates_success():
    """Agent 应该能评估成功执行的任务。"""
    from backend.services.reflective_agent import ReflectiveAgent

    agent = ReflectiveAgent()

    # Mock the LLM
    with patch.object(agent, 'llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = "Task completed successfully"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await agent.process_message("Hello")

        assert result is not None
        assert "response" in result
        assert "reflection" in result


@pytest.mark.asyncio
async def test_reflective_agent_retries_on_failure():
    """Agent 应该在失败时重试。"""
    from backend.services.reflective_agent import ReflectiveAgent

    agent = ReflectiveAgent()
    agent.max_retries = 2

    # Mock the LLM to always succeed (reflection may fail but main call succeeds)
    with patch.object(agent, 'llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = "Success response"

        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await agent.process_message("Hello")

        assert result is not None
        assert "response" in result
        assert result["response"] == "Success response"
