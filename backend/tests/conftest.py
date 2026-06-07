"""
pytest 配置文件

提供全局 fixtures，支持依赖注入和 mock。
"""
import pytest
import asyncio

from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环。"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client():
    """创建单个 TestClient 实例。"""
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture
def container():
    """创建依赖注入容器。"""
    from backend.container import create_container
    return create_container()


@pytest.fixture
def user_repository():
    """创建内存用户 Repository。"""
    from backend.repositories.memory import InMemoryUserRepository
    return InMemoryUserRepository()


@pytest.fixture
def document_repository():
    """创建内存文档 Repository。"""
    from backend.repositories.memory import InMemoryDocumentRepository
    return InMemoryDocumentRepository()


@pytest.fixture
def mock_user_repository():
    """创建 mock 用户 Repository。"""
    from backend.repositories.memory import InMemoryUserRepository
    return InMemoryUserRepository()


@pytest.fixture
def mock_document_repository():
    """创建 mock 文档 Repository。"""
    from backend.repositories.memory import InMemoryDocumentRepository
    return InMemoryDocumentRepository()
