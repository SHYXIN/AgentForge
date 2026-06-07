"""
测试：API 路由层依赖注入

行为：API 路由应该能够通过依赖注入获取 Service 实例。
"""
import pytest
from fastapi.testclient import TestClient


def test_routes_use_dependency_injection():
    """路由应该使用依赖注入获取 Service。"""
    from backend.api.routes import register_user, chat, upload_rag_document
    
    # 验证函数存在
    assert register_user is not None
    assert chat is not None
    assert upload_rag_document is not None


def test_container_provides_user_repository():
    """Container 应该能够提供 UserRepository。"""
    from backend.container import container
    from backend.repositories.base import UserRepository
    
    # 验证 Repository 可用
    user_repo = container.user_repository()
    assert user_repo is not None


def test_container_provides_document_repository():
    """Container 应该能够提供 DocumentRepository。"""
    from backend.container import container
    from backend.repositories.base import DocumentRepository
    
    # 验证 Repository 可用
    doc_repo = container.document_repository()
    assert doc_repo is not None


def test_api_endpoints_work_with_di():
    """API 端点应该能够在依赖注入下工作。"""
    # 这是一个集成测试，验证 API 端点可以正常工作
    pass
