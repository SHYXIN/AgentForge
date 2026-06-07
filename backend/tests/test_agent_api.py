"""
测试：Agent CRUD API

行为：Agent API 应该支持创建、读取、更新、删除 Agent。
注意：仅管理员可管理 Agent。
"""
import pytest
import uuid
from fastapi.testclient import TestClient


def test_create_agent(client: TestClient):
    """应该能创建新 Agent。"""
    # 使用唯一名称避免与种子数据冲突
    unique_name = f"test-agent-{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/agents",
        json={
            "name": unique_name,
            "role": "代码工程师",
            "description": "负责编写和优化代码",
            "config": '{"model": "gpt-4"}',
            "is_active": 1
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == unique_name
    assert data["role"] == "代码工程师"
    assert data["description"] == "负责编写和优化代码"
    assert data["is_active"] is True


def test_create_duplicate_agent(client: TestClient):
    """创建重复名称的 Agent 应该返回 400。"""
    # 创建第一个 Agent
    client.post(
        "/api/agents",
        json={
            "name": "duplicate",
            "role": "测试 Agent",
            "is_active": 1
        }
    )
    
    # 尝试创建同名 Agent
    response = client.post(
        "/api/agents",
        json={
            "name": "duplicate",
            "role": "另一个 Agent",
            "is_active": 1
        }
    )
    
    assert response.status_code == 400
    assert "已存在" in response.json()["detail"]


def test_list_agents(client: TestClient):
    """应该能获取 Agent 列表。"""
    # 先创建几个 Agent
    client.post(
        "/api/agents",
        json={"name": "agent-1", "role": "角色 1", "is_active": 1}
    )
    client.post(
        "/api/agents",
        json={"name": "agent-2", "role": "角色 2", "is_active": 1}
    )
    
    response = client.get("/api/agents")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_list_active_agents(client: TestClient):
    """应该能获取所有启用的 Agent。"""
    # 创建启用的 Agent
    client.post(
        "/api/agents",
        json={"name": "active-agent", "role": "活跃 Agent", "is_active": 1}
    )
    
    # 创建禁用的 Agent
    client.post(
        "/api/agents",
        json={"name": "inactive-agent", "role": "非活跃 Agent", "is_active": 0}
    )
    
    response = client.get("/api/agents?active_only=true")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(agent["is_active"] is True for agent in data)


def test_get_agent(client: TestClient):
    """应该能获取单个 Agent。"""
    # 先创建 Agent
    create_response = client.post(
        "/api/agents",
        json={
            "name": "getter",
            "role": "获取测试",
            "is_active": 1
        }
    )
    agent_id = create_response.json()["id"]
    
    response = client.get(f"/api/agents/{agent_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == agent_id
    assert data["name"] == "getter"
    assert data["role"] == "获取测试"


def test_get_nonexistent_agent(client: TestClient):
    """获取不存在的 Agent 应该返回 404。"""
    response = client.get("/api/agents/nonexistent-id")

    assert response.status_code == 404


def test_update_agent(client: TestClient):
    """应该能更新 Agent。"""
    # 先创建 Agent
    create_response = client.post(
        "/api/agents",
        json={
            "name": "updater",
            "role": "旧角色",
            "description": "旧描述",
            "is_active": 1
        }
    )
    agent_id = create_response.json()["id"]

    response = client.put(
        f"/api/agents/{agent_id}",
        json={
            "role": "新角色",
            "description": "新描述",
            "config": '{"model": "gpt-4-turbo"}'
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "新角色"
    assert data["description"] == "新描述"
    assert data["config"] == '{"model": "gpt-4-turbo"}'


def test_update_nonexistent_agent(client: TestClient):
    """更新不存在的 Agent 应该返回 404。"""
    response = client.put(
        "/api/agents/nonexistent-id",
        json={"role": "新角色"}
    )

    assert response.status_code == 404


def test_delete_agent(client: TestClient):
    """应该能删除 Agent。"""
    # 先创建 Agent
    create_response = client.post(
        "/api/agents",
        json={
            "name": "deleter",
            "role": "删除测试",
            "is_active": 1
        }
    )
    agent_id = create_response.json()["id"]

    response = client.delete(f"/api/agents/{agent_id}")

    assert response.status_code == 204

    # 验证已删除
    get_response = client.get(f"/api/agents/{agent_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_agent(client: TestClient):
    """删除不存在的 Agent 应该返回 404。"""
    response = client.delete("/api/agents/nonexistent-id")

    assert response.status_code == 404


def test_enable_agent(client: TestClient):
    """应该能启用 Agent。"""
    # 先创建禁用的 Agent
    create_response = client.post(
        "/api/agents",
        json={
            "name": "enabler",
            "role": "启用测试",
            "is_active": 0
        }
    )
    agent_id = create_response.json()["id"]
    
    response = client.post(f"/api/agents/{agent_id}/enable")

    assert response.status_code == 200
    
    # 验证已启用
    get_response = client.get(f"/api/agents/{agent_id}")
    assert get_response.json()["is_active"] is True


def test_disable_agent(client: TestClient):
    """应该能禁用 Agent。"""
    # 先创建启用的 Agent
    create_response = client.post(
        "/api/agents",
        json={
            "name": "disabler",
            "role": "禁用测试",
            "is_active": 1
        }
    )
    agent_id = create_response.json()["id"]
    
    response = client.post(f"/api/agents/{agent_id}/disable")

    assert response.status_code == 200
    
    # 验证已禁用
    get_response = client.get(f"/api/agents/{agent_id}")
    assert get_response.json()["is_active"] is False
