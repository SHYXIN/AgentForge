"""
多 Agent 协作 API 路由模块

提供多 Agent 协作的 REST API 端点。
"""
from fastapi import HTTPException
from typing import Dict, Any

from backend.models import MultiAgentChatRequest, MultiAgentChatResponse, TaskStatusResponse
from backend.services.multi_agent import multi_agent_service


async def multi_agent_chat(request: MultiAgentChatRequest) -> MultiAgentChatResponse:
    """
    多 Agent 聊天端点处理函数。

    Args:
        request: 聊天请求

    Returns:
        聊天响应
    """
    try:
        # 调用多 Agent 服务处理消息
        result = await multi_agent_service.chat(request.message)

        return MultiAgentChatResponse(
            task_id=result["task_id"],
            response=result["response"],
            result=result.get("result"),
            error=result.get("error")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多 Agent 处理失败: {str(e)}")


async def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    查询任务状态端点处理函数。

    Args:
        task_id: 任务 ID

    Returns:
        任务状态响应
    """
    try:
        # 获取任务状态
        status = await multi_agent_service.get_task_status(task_id)

        if status is None:
            raise HTTPException(status_code=404, detail="任务不存在")

        return TaskStatusResponse(
            task_id=task_id,
            status=status["status"],
            message=status.get("message"),
            result=status.get("result"),
            error=status.get("error")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")
