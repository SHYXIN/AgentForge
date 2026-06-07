"""
Agent 内存 Repository 实现模块

提供基于内存的 Agent Repository 实现，用于开发和测试。
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict

from backend.models import Agent
from backend.repositories.base import AgentRepository


class InMemoryAgentRepository(AgentRepository):
    """Agent 内存存储实现。"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}

    async def create(self, agent: Agent) -> Agent:
        """创建 Agent。"""
        if not agent.id:
            agent.id = str(uuid.uuid4())
        
        now = datetime.utcnow()
        agent.created_at = now
        agent.updated_at = now
        
        self.agents[agent.id] = agent
        return agent

    async def get_by_id(self, agent_id: str) -> Optional[Agent]:
        """通过 ID 获取 Agent。"""
        return self.agents.get(agent_id)

    async def get_by_name(self, name: str) -> Optional[Agent]:
        """通过名称获取 Agent。"""
        for agent in self.agents.values():
            if agent.name == name:
                return agent
        return None

    async def list_all(self) -> List[Agent]:
        """获取所有 Agent。"""
        return list(self.agents.values())

    async def list_active(self) -> List[Agent]:
        """获取所有启用的 Agent。"""
        return [
            agent for agent in self.agents.values()
            if agent.is_active == 1
        ]

    async def update(self, agent: Agent) -> Agent:
        """更新 Agent。"""
        if agent.id in self.agents:
            agent.updated_at = datetime.utcnow()
            self.agents[agent.id] = agent
            return agent
        return None

    async def delete(self, agent_id: str) -> bool:
        """删除 Agent。"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False

    async def enable(self, agent_id: str) -> bool:
        """启用 Agent。"""
        agent = self.agents.get(agent_id)
        if agent:
            agent.is_active = 1
            agent.updated_at = datetime.utcnow()
            return True
        return False

    async def disable(self, agent_id: str) -> bool:
        """禁用 Agent。"""
        agent = self.agents.get(agent_id)
        if agent:
            agent.is_active = 0
            agent.updated_at = datetime.utcnow()
            return True
        return False
