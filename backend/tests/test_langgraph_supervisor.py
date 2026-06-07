"""
测试：LangGraph Supervisor 图

行为：Supervisor 图应该能协调多个 Worker Agent 完成任务。
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


def test_supervisor_graph_can_be_created():
    """Supervisor 图应该能够被创建。"""
    from backend.services.langgraph_supervisor import SupervisorGraph

    graph = SupervisorGraph()
    assert graph is not None


def test_supervisor_has_workers():
    """Supervisor 应该有 Worker Agent。"""
    from backend.services.langgraph_supervisor import SupervisorGraph

    graph = SupervisorGraph()
    assert hasattr(graph, 'workers')
    assert len(graph.workers) > 0


def test_supervisor_has_llm():
    """Supervisor 应该有 LLM 用于决策。"""
    from backend.services.langgraph_supervisor import SupervisorGraph

    graph = SupervisorGraph()
    assert hasattr(graph, 'llm')
    assert graph.llm is not None


@pytest.mark.asyncio
async def test_supervisor_can_route_task():
    """Supervisor 应该能路由任务到正确的 Worker。"""
    from backend.services.langgraph_supervisor import SupervisorGraph

    graph = SupervisorGraph()

    # Mock the LLM to return a worker choice
    with patch.object(graph, 'llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = "coder"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        # Re-create graph with mocked llm
        graph.llm = mock_llm

        result = await graph.process_message("写一个排序函数")

        assert result is not None
        assert "response" in result


@pytest.mark.asyncio
async def test_supervisor_handles_unknown_task():
    """Supervisor 应该能处理未知任务类型。"""
    from backend.services.langgraph_supervisor import SupervisorGraph

    graph = SupervisorGraph()

    # Mock the LLM
    with patch.object(graph, 'llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = "unknown"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        graph.llm = mock_llm

        result = await graph.process_message("未知任务")

        assert result is not None
        assert "response" in result
