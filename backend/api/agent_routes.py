"""
Agent API 路由模块

提供 Agent 的 CRUD 操作。
注意：仅管理员可管理 Agent。
"""
import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.models import Agent
from backend.container import container


router = APIRouter(prefix="/api/agents", tags=["agents"])


# ============ Pydantic 模型 ============

class CreateAgentRequest(BaseModel):
    name: str
    role: str
    description: str = ""
    config: str = "{}"
    is_active: int = 1


class UpdateAgentRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    config: Optional[str] = None
    is_active: Optional[int] = None


class AgentResponse(BaseModel):
    id: str
    name: str
    role: str
    description: str
    config: str
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]


# ============ 依赖注入 ============

def get_agent_repository():
    """获取 Agent Repository。"""
    return container.agent_repository()


# ============ API 端点 ============

@router.post("", status_code=201)
async def create_agent(
    request: CreateAgentRequest,
    agent_repo = Depends(get_agent_repository)
):
    """创建新 Agent（仅管理员）。"""
    # 检查名称是否已存在
    existing = await agent_repo.get_by_name(request.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Agent 名称 '{request.name}' 已存在"
        )
    
    now = datetime.utcnow()
    agent = Agent(
        id=str(uuid.uuid4()),
        name=request.name,
        role=request.role,
        description=request.description,
        config=request.config,
        is_active=request.is_active,
        created_at=now,
        updated_at=now
    )
    
    created = await agent_repo.create(agent)
    
    return {
        "id": created.id,
        "name": created.name,
        "role": created.role,
        "description": created.description,
        "config": created.config,
        "is_active": bool(created.is_active),
        "created_at": created.created_at.isoformat() if created.created_at else None,
        "updated_at": created.updated_at.isoformat() if created.updated_at else None
    }


@router.get("")
async def list_agents(
    active_only: bool = False,
    agent_repo = Depends(get_agent_repository)
):
    """获取 Agent 列表。"""
    if active_only:
        agents = await agent_repo.list_active()
    else:
        agents = await agent_repo.list_all()
    
    result = []
    for agent in agents:
        result.append({
            "id": agent.id,
            "name": agent.name,
            "role": agent.role,
            "description": agent.description,
            "config": agent.config,
            "is_active": bool(agent.is_active),
            "created_at": agent.created_at.isoformat() if agent.created_at else None,
            "updated_at": agent.updated_at.isoformat() if agent.updated_at else None
        })
    
    return result


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    agent_repo = Depends(get_agent_repository)
):
    """获取单个 Agent。"""
    agent = await agent_repo.get_by_id(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent 不存在")
    
    return {
        "id": agent.id,
        "name": agent.name,
        "role": agent.role,
        "description": agent.description,
        "config": agent.config,
        "is_active": bool(agent.is_active),
        "created_at": agent.created_at.isoformat() if agent.created_at else None,
        "updated_at": agent.updated_at.isoformat() if agent.updated_at else None
    }


@router.put("/{agent_id}")
async def update_agent(
    agent_id: str,
    request: UpdateAgentRequest,
    agent_repo = Depends(get_agent_repository)
):
    """更新 Agent（仅管理员）。"""
    agent = await agent_repo.get_by_id(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent 不存在")
    
    # 如果要修改名称，检查新名称是否已存在
    if request.name is not None and request.name != agent.name:
        existing = await agent_repo.get_by_name(request.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Agent 名称 '{request.name}' 已存在"
            )
        agent.name = request.name
    
    if request.role is not None:
        agent.role = request.role
    if request.description is not None:
        agent.description = request.description
    if request.config is not None:
        agent.config = request.config
    if request.is_active is not None:
        agent.is_active = request.is_active
    
    updated = await agent_repo.update(agent)
    
    return {
        "id": updated.id,
        "name": updated.name,
        "role": updated.role,
        "description": updated.description,
        "config": updated.config,
        "is_active": bool(updated.is_active),
        "created_at": updated.created_at.isoformat() if updated.created_at else None,
        "updated_at": updated.updated_at.isoformat() if updated.updated_at else None
    }


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str,
    agent_repo = Depends(get_agent_repository)
):
    """删除 Agent（仅管理员）。"""
    result = await agent_repo.delete(agent_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Agent 不存在")
    
    return None


@router.post("/{agent_id}/enable")
async def enable_agent(
    agent_id: str,
    agent_repo = Depends(get_agent_repository)
):
    """启用 Agent。"""
    result = await agent_repo.enable(agent_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Agent 不存在")
    
    return {"message": "Agent 已启用"}


@router.post("/{agent_id}/disable")
async def disable_agent(
    agent_id: str,
    agent_repo = Depends(get_agent_repository)
):
    """禁用 Agent。"""
    result = await agent_repo.disable(agent_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Agent 不存在")
    
    return {"message": "Agent 已禁用"}
