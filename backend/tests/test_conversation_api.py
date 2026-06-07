"""
测试：对话 CRUD API

行为：对话 API 应该支持创建、读取、更新、删除对话。
"""
import pytest
from fastapi.testclient import TestClient


def test_create_conversation(client: TestClient):
    """应该能创建新对话。"""
    response = client.post(
        "/api/conversations",
        json={
            "title": "测试对话",
            "description": "这是一个测试对话",
            "user_id": "user-123"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "测试对话"
    assert data["description"] == "这是一个测试对话"


def test_list_conversations(client: TestClient):
    """应该能获取对话列表。"""
    response = client.get("/api/conversations?user_id=user-123")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_conversation(client: TestClient):
    """获取不存在的对话应该返回 404。"""
    response = client.get("/api/conversations/nonexistent-id")

    assert response.status_code == 404


def test_rename_conversation(client: TestClient):
    """应该能重命名对话。"""
    # 先创建对话
    create_response = client.post(
        "/api/conversations",
        json={"title": "旧标题", "user_id": "user-123"}
    )
    conversation_id = create_response.json()["id"]

    response = client.put(
        f"/api/conversations/{conversation_id}",
        json={"title": "新标题"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "新标题"


def test_delete_conversation(client: TestClient):
    """应该能删除对话。"""
    # 先创建对话
    create_response = client.post(
        "/api/conversations",
        json={"title": "待删除", "user_id": "user-123"}
    )
    conversation_id = create_response.json()["id"]

    response = client.delete(f"/api/conversations/{conversation_id}")

    assert response.status_code == 204

    # 验证已删除
    get_response = client.get(f"/api/conversations/{conversation_id}")
    assert get_response.status_code == 404
