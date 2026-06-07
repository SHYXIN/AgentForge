"""
测试：错误处理中间件

行为：系统应该能够捕获异常并返回统一的错误响应格式。
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException


def test_http_exception_returns_json():
    """HTTP 异常应该返回 JSON 格式的错误响应。"""
    from backend.main import app
    
    client = TestClient(app)
    
    # 触发 404 错误
    response = client.get("/nonexistent")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_validation_error_returns_422():
    """验证错误应该返回 422 状态码。"""
    from backend.main import app
    
    client = TestClient(app)
    
    # 发送无效数据（缺少必填字段）
    response = client.post("/api/auth/register", json={})
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_internal_server_error_returns_500():
    """内部服务器错误应该返回 500 状态码。"""
    # 这里我们测试错误处理中间件是否正确捕获异常
    # 实际实现时需要一个会抛出异常的端点
    pass
