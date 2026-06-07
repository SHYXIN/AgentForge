"""
依赖注入容器模块

提供统一的依赖注入容器，管理所有服务的生命周期和依赖关系。
支持通过环境变量切换存储后端（memory/mysql）。
"""
import logging
import os
from dependency_injector import containers, providers

from backend.config import AppConfig

# 内存存储单例（确保 seed 和 app 使用相同实例）
_memory_user_repo = None
_memory_doc_repo = None


def get_memory_user_repository():
    """获取内存用户 Repository 单例。"""
    global _memory_user_repo
    if _memory_user_repo is None:
        from backend.repositories.memory import InMemoryUserRepository
        _memory_user_repo = InMemoryUserRepository()
    return _memory_user_repo


def get_memory_document_repository():
    """获取内存文档 Repository 单例。"""
    global _memory_doc_repo
    if _memory_doc_repo is None:
        from backend.repositories.memory import InMemoryDocumentRepository
        _memory_doc_repo = InMemoryDocumentRepository()
    return _memory_doc_repo


def create_user_repository():
    """创建用户 Repository。"""
    from backend.config import config as app_config

    if app_config.repo_backend == "mysql":
        from backend.repositories.mysql import MySQLUserRepository, get_mysql_session
        session = get_mysql_session()
        return MySQLUserRepository(session)
    else:
        return get_memory_user_repository()


def create_document_repository():
    """创建文档 Repository。"""
    from backend.config import config as app_config

    if app_config.repo_backend == "mysql":
        from backend.repositories.mysql import MySQLDocumentRepository, get_mysql_session
        session = get_mysql_session()
        return MySQLDocumentRepository(session)
    else:
        return get_memory_document_repository()


class Container(containers.DeclarativeContainer):
    """应用依赖注入容器。"""

    # 配置
    config = providers.Configuration()

    # 日志服务
    logger = providers.Singleton(
        logging.getLogger,
        name="agentforge"
    )

    # Repository 层（根据环境变量选择实现）
    user_repository = providers.Singleton(create_user_repository)
    document_repository = providers.Singleton(create_document_repository)

    @classmethod
    def init_resources(cls):
        """初始化资源。"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


def create_container() -> Container:
    """创建并配置容器。"""
    container = Container()
    container.config.from_dict({
        'debug': False,
        'log_level': 'INFO',
        'repo': {
            'backend': 'memory',
        },
        'db': {
            'enabled': False,
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '123456',
            'name': 'agentforge',
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
        },
        'chroma': {
            'host': 'localhost',
            'port': 8001,
        },
    })
    container.init_resources()
    return container


# 全局容器实例
container = create_container()
