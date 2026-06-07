"""
测试：Agent 数据库模型

行为：Agent 应该能存储在数据库中，包含名称、角色、描述等信息。
"""
import pytest


def test_agent_model_can_be_created():
    """Agent 模型应该能够被创建。"""
    from backend.models import Agent as AgentModel

    agent = AgentModel(
        name="coder",
        role="代码工程师",
        description="负责编写和优化代码",
        is_active=True
    )

    assert agent is not None
    assert agent.name == "coder"
    assert agent.role == "代码工程师"


def test_agent_model_has_required_fields():
    """Agent 模型应该有必需字段。"""
    from backend.models import Agent as AgentModel

    agent = AgentModel(
        name="tester",
        role="测试工程师",
        description="负责测试"
    )

    assert hasattr(agent, 'id')
    assert hasattr(agent, 'name')
    assert hasattr(agent, 'role')
    assert hasattr(agent, 'description')
    assert hasattr(agent, 'is_active')
    assert hasattr(agent, 'created_at')


def test_agent_model_default_values():
    """Agent 模型应该有正确的默认值。"""
    from backend.models import Agent as AgentModel

    agent = AgentModel(name="researcher", role="研究员", is_active=1)

    assert agent.is_active == 1
    assert agent.description is None or agent.description == ""
