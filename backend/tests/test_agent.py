"""
测试：Agent 对话功能

行为：系统应该能够接收用户消息，通过 Agent 处理，并返回响应。
"""
import pytest
from fastapi.testclient import TestClient


def test_agent_chat_endpoint():
    """Agent 应该能够处理聊天消息。"""
    from backend.main import app
    
    client = TestClient(app)
    
    # 发送聊天消息
    response = client.post(
        "/api/chat",
        json={
            "message": "你好，请介绍一下你自己"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "agent_thoughts" in data
    assert len(data["response"]) > 0


def test_agent_chat_with_history():
    """Agent 应该能够处理多轮对话。"""
    from backend.main import app
    
    client = TestClient(app)
    
    # 第一轮对话
    response1 = client.post(
        "/api/chat",
        json={
            "message": "你好"
        }
    )
    assert response1.status_code == 200
    
    # 第二轮对话（带上下文）
    response2 = client.post(
        "/api/chat",
        json={
            "message": "你能做什么？",
            "conversation_id": "test-conversation"
        }
    )
    assert response2.status_code == 200
    data = response2.json()
    assert "response" in data


def test_agent_chat_empty_message():
    """Agent 应该能够处理空消息。"""
    from backend.main import app
    
    client = TestClient(app)
    
    # 发送空消息
    response = client.post(
        "/api/chat",
        json={
            "message": ""
        }
    )
    
    # 应该返回 400 错误
    assert response.status_code == 400


def test_agent_chat_long_message():
    """Agent 应该能够处理长消息。"""
    from backend.main import app
    
    client = TestClient(app)
    
    # 发送长消息
    long_message = "这是一个很长的消息" * 100
    
    response = client.post(
        "/api/chat",
        json={
            "message": long_message
        }
    )
    
    # 应该正常处理（可能需要截断）
    assert response.status_code in [200, 400]
