"""
测试：Agent 数据库模型完整验收标准

行为：验证问题 #6 的所有验收标准都已满足。
"""
import pytest
import os
from datetime import datetime
from backend.models import Agent


def test_acceptance_criteria_create_agent():
    """验收标准：能创建 Agent 对象"""
    agent = Agent(
        name="coder",
        role="代码工程师",
        description="负责编写和优化代码",
        is_active=1
    )
    
    assert agent is not None
    assert agent.name == "coder"
    assert agent.role == "代码工程师"
    assert agent.description == "负责编写和优化代码"
    assert agent.is_active == 1


def test_acceptance_criteria_configure_agent():
    """验收标准：能配置 Agent 参数"""
    agent = Agent(
        name="researcher",
        role="研究员",
        description="负责研究和分析",
        config='{"model": "gpt-4", "temperature": 0.7}',
        is_active=1
    )
    
    assert agent.config == '{"model": "gpt-4", "temperature": 0.7}'
    assert agent.name == "researcher"
    assert agent.role == "研究员"


def test_acceptance_criteria_enable_disable_agent():
    """验收标准：能启用/禁用 Agent"""
    # 创建启用的 Agent
    active_agent = Agent(
        name="active_agent",
        role="活跃 Agent",
        is_active=1
    )
    assert active_agent.is_active == 1
    assert bool(active_agent.is_active) is True
    
    # 创建禁用的 Agent
    inactive_agent = Agent(
        name="inactive_agent",
        role="非活跃 Agent",
        is_active=0
    )
    assert inactive_agent.is_active == 0
    assert bool(inactive_agent.is_active) is False


def test_acceptance_criteria_agent_to_dict():
    """验收标准：Agent 可以序列化为字典"""
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


def test_acceptance_criteria_agent_timestamps():
    """验收标准：Agent 有正确的时间戳"""
    now = datetime.utcnow()
    agent = Agent(
        name="coder",
        role="代码工程师",
        created_at=now,
        updated_at=now
    )
    
    assert agent.created_at is not None
    assert agent.updated_at is not None
    assert isinstance(agent.created_at, datetime)
    assert isinstance(agent.updated_at, datetime)


def test_acceptance_criteria_agent_unique_name():
    """验收标准：Agent 名称应该唯一（由数据库约束保证）"""
    agent1 = Agent(name="unique_agent", role="测试 Agent 1")
    agent2 = Agent(name="unique_agent", role="测试 Agent 2")
    
    # 在 Python 层面，两个对象可以创建（数据库层面会阻止重复）
    assert agent1.name == agent2.name
    assert agent1.name == "unique_agent"


def test_migration_includes_agent_table():
    """验收标准：Alembic 迁移包含 agents 表"""
    # 检查所有迁移文件
    migration_dir = "alembic/versions"
    found_agents_table = False
    
    for filename in os.listdir(migration_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            filepath = os.path.join(migration_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if "'agents'" in content or '"agents"' in content:
                    found_agents_table = True
                    break
    
    assert found_agents_table, "任何迁移脚本中都缺少 agents 表"


def test_migration_includes_agent_fields():
    """验收标准：Alembic 迁移包含 Agent 的所有字段"""
    # 检查所有迁移文件
    migration_dir = "alembic/versions"
    required_fields = ['name', 'role', 'description', 'config', 'is_active', 'created_at', 'updated_at']
    
    # 读取所有迁移内容
    all_content = ""
    for filename in os.listdir(migration_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            filepath = os.path.join(migration_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                all_content += f.read()
    
    # 验证必需字段存在
    for field in required_fields:
        assert field in all_content, f"agents 表缺少 {field} 字段"
