"""
测试：Agent Repository

行为：Agent Repository 应该能正确创建、读取、更新、删除 Agent。
"""
import pytest
import asyncio
from datetime import datetime
from backend.models import Agent


@pytest.fixture
def agent_repo():
    """创建内存 Agent Repository。"""
    from backend.repositories.agent_memory import InMemoryAgentRepository
    return InMemoryAgentRepository()


@pytest.mark.asyncio
async def test_create_agent(agent_repo):
    """应该能创建 Agent。"""
    agent = Agent(
        name="coder",
        role="代码工程师",
        description="负责编写和优化代码",
        config='{"model": "gpt-4"}',
        is_active=1
    )
    
    created = await agent_repo.create(agent)
    
    assert created is not None
    assert created.id is not None
    assert created.name == "coder"
    assert created.role == "代码工程师"
    assert created.description == "负责编写和优化代码"
    assert created.config == '{"model": "gpt-4"}'
    assert created.is_active == 1
    assert created.created_at is not None


@pytest.mark.asyncio
async def test_get_agent_by_id(agent_repo):
    """应该能通过 ID 获取 Agent。"""
    agent = Agent(
        name="tester",
        role="测试工程师",
        is_active=1
    )
    created = await agent_repo.create(agent)
    
    fetched = await agent_repo.get_by_id(created.id)
    
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "tester"


@pytest.mark.asyncio
async def test_get_agent_by_name(agent_repo):
    """应该能通过名称获取 Agent。"""
    agent = Agent(
        name="researcher",
        role="研究员",
        is_active=1
    )
    await agent_repo.create(agent)
    
    fetched = await agent_repo.get_by_name("researcher")
    
    assert fetched is not None
    assert fetched.name == "researcher"
    assert fetched.role == "研究员"


@pytest.mark.asyncio
async def test_list_all_agents(agent_repo):
    """应该能获取所有 Agent。"""
    # 创建多个 Agent
    for i in range(3):
        await agent_repo.create(Agent(
            name=f"agent-{i}",
            role=f"角色 {i}",
            is_active=1
        ))
    
    agents = await agent_repo.list_all()
    
    assert len(agents) == 3


@pytest.mark.asyncio
async def test_list_active_agents(agent_repo):
    """应该能获取所有启用的 Agent。"""
    # 创建启用的 Agent
    await agent_repo.create(Agent(
        name="active-1",
        role="活跃 Agent 1",
        is_active=1
    ))
    await agent_repo.create(Agent(
        name="active-2",
        role="活跃 Agent 2",
        is_active=1
    ))
    
    # 创建禁用的 Agent
    await agent_repo.create(Agent(
        name="inactive-1",
        role="非活跃 Agent",
        is_active=0
    ))
    
    active_agents = await agent_repo.list_active()
    
    assert len(active_agents) == 2
    assert all(agent.is_active == 1 for agent in active_agents)


@pytest.mark.asyncio
async def test_update_agent(agent_repo):
    """应该能更新 Agent。"""
    agent = Agent(
        name="updater",
        role="更新测试",
        description="旧描述",
        is_active=1
    )
    created = await agent_repo.create(agent)
    
    created.description = "新描述"
    created.config = '{"model": "gpt-4-turbo"}'
    updated = await agent_repo.update(created)
    
    assert updated is not None
    assert updated.description == "新描述"
    assert updated.config == '{"model": "gpt-4-turbo"}'
    
    # 验证已更新
    fetched = await agent_repo.get_by_id(created.id)
    assert fetched.description == "新描述"


@pytest.mark.asyncio
async def test_delete_agent(agent_repo):
    """应该能删除 Agent。"""
    agent = Agent(
        name="deleter",
        role="删除测试",
        is_active=1
    )
    created = await agent_repo.create(agent)
    
    result = await agent_repo.delete(created.id)
    
    assert result is True
    
    # 验证已删除
    fetched = await agent_repo.get_by_id(created.id)
    assert fetched is None


@pytest.mark.asyncio
async def test_enable_agent(agent_repo):
    """应该能启用 Agent。"""
    agent = Agent(
        name="enabler",
        role="启用测试",
        is_active=0
    )
    created = await agent_repo.create(agent)
    
    result = await agent_repo.enable(created.id)
    
    assert result is True
    
    # 验证已启用
    fetched = await agent_repo.get_by_id(created.id)
    assert fetched.is_active == 1


@pytest.mark.asyncio
async def test_disable_agent(agent_repo):
    """应该能禁用 Agent。"""
    agent = Agent(
        name="disabler",
        role="禁用测试",
        is_active=1
    )
    created = await agent_repo.create(agent)
    
    result = await agent_repo.disable(created.id)
    
    assert result is True
    
    # 验证已禁用
    fetched = await agent_repo.get_by_id(created.id)
    assert fetched.is_active == 0


@pytest.mark.asyncio
async def test_agent_to_dict(agent_repo):
    """Agent 应该能序列化为字典。"""
    now = datetime.utcnow()
    agent = Agent(
        id="agent-123",
        name="coder",
        role="代码工程师",
        description="负责代码",
        config='{"key": "value"}',
        is_active=1,
        created_at=now,
        updated_at=now
    )
    
    result = agent.to_dict()
    
    assert result["id"] == "agent-123"
    assert result["name"] == "coder"
    assert result["role"] == "代码工程师"
    assert result["description"] == "负责代码"
    assert result["config"] == '{"key": "value"}'
    assert result["is_active"] is True
    assert "created_at" in result
    assert "updated_at" in result
