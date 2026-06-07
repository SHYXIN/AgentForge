"""
测试：基础 API 端点

行为：系统应该提供基础 API 端点，包括用户注册、登录和文档管理。
"""
import pytest
import uuid


def test_user_registration(client: object):
    """用户应该能够注册新账户。"""
    # 使用唯一用户名
    unique_id = str(uuid.uuid4())[:8]

    # 注册新用户
    response = client.post(
        "/api/auth/register",
        json={
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "testpass123"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert "user_id" in data
    assert data["username"] == f"testuser_{unique_id}"


def test_user_login(client: object):
    """用户应该能够登录并获取 Token。"""
    # 使用唯一用户名
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_id}"

    # 先注册用户
    client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": f"test_{unique_id}@example.com",
            "password": "testpass123"
        }
    )

    # 登录
    response = client.post(
        "/api/auth/login",
        json={
            "username": username,
            "password": "testpass123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_document_upload(client: object):
    """用户应该能够上传文档。"""
    # 上传文档
    response = client.post(
        "/api/documents",
        files={
            "file": ("test.txt", b"Test document content", "text/plain")
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert "document_id" in data
    assert data["filename"] == "test.txt"


def test_document_list(client: object):
    """用户应该能够获取文档列表。"""
    # 先上传文档
    client.post(
        "/api/documents",
        files={
            "file": ("test.txt", b"Test document content", "text/plain")
        }
    )

    # 获取文档列表
    response = client.get("/api/documents")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
