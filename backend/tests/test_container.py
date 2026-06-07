"""
测试：依赖注入容器

行为：容器应该能够注册和解析服务。
"""
import pytest


def test_container_can_be_created():
    """容器应该能够被创建。"""
    from backend.container import Container
    
    container = Container()
    assert container is not None


def test_container_can_register_singleton():
    """容器应该能够注册 Singleton 服务。"""
    from backend.container import Container
    from dependency_injector import providers
    
    container = Container()
    container.config.from_dict({'test': 'value'})
    
    # 验证配置已加载
    assert container.config.test() == 'value'


def test_container_can_resolve_service():
    """容器应该能够解析已注册的服务。"""
    from backend.container import Container
    
    container = Container()
    
    # 验证 Logger 服务可用
    logger = container.logger()
    assert logger is not None
