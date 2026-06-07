"""
依赖注入容器模块

提供统一的依赖注入容器，管理所有服务的生命周期和依赖关系。
支持通过环境变量切换存储后端（memory/mysql）。
"""
import logging
import os
from dependency_injector import containers, providers

from backend.config import AppConfig


def create_user_repository():
    """创建用户 Repository。"""
    from backend.config import config as app_config

    if app_config.repo_backend == "mysql":
        from backend.repositories.mysql import MySQLUserRepository, get_mysql_session
        session = get_mysql_session()
        return MySQLUserRepository(session)
    else:
        from backend.repositories.memory import InMemoryUserRepository
        return InMemoryUserRepository()


def create_document_repository():
    """创建文档 Repository。"""
    from backend.config import config as app_config

    if app_config.repo_backend == "mysql":
        from backend.repositories.mysql import MySQLDocumentRepository, get_mysql_session
        session = get_mysql_session()
        return MySQLDocumentRepository(session)
    else:
        from backend.repositories.memory import InMemoryDocumentRepository
        return InMemoryDocumentRepository()


def create_conversation_repository():
    """创建对话 Repository。"""
    from backend.config import config as app_config

    if app_config.repo_backend == "mysql":
        from backend.repositories.mysql import MySQLConversationRepository, get_mysql_session
        session = get_mysql_session()
        return MySQLConversationRepository(session)
    else:
        from backend.repositories.conversation_memory import InMemoryConversationRepository
        return InMemoryConversationRepository()


def create_message_repository():
    """创建消息 Repository。"""
    from backend.config import config as app_config

    if app_config.repo_backend == "mysql":
        from backend.repositories.mysql import MySQLMessageRepository, get_mysql_session
        session = get_mysql_session()
        return MySQLMessageRepository(session)
    else:
        from backend.repositories.conversation_memory import InMemoryMessageRepository
        return InMemoryMessageRepository()


def create_agent_repository():
    """创建 Agent Repository。"""
    from backend.config import config as app_config

    if app_config.repo_backend == "mysql":
        from backend.repositories.mysql import MySQLAgentRepository, get_mysql_session
        session = get_mysql_session()
        return MySQLAgentRepository(session)
    else:
        from backend.repositories.agent_memory import InMemoryAgentRepository
        return InMemoryAgentRepository()


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
    conversation_repository = providers.Singleton(create_conversation_repository)
    message_repository = providers.Singleton(create_message_repository)
    agent_repository = providers.Singleton(create_agent_repository)

    @classmethod
    def init_resources(cls):
        """初始化资源。"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


def create_container() -> Container:
    """创建并配置容器。"""
    from backend.config import AppConfig
    app_config = AppConfig()

    container = Container()
    container.config.from_dict({
        'debug': app_config.debug,
        'log_level': app_config.log_level,
        'repo': {
            'backend': app_config.repo_backend,
        },
        'db': {
            'enabled': app_config.db_enabled if hasattr(app_config, 'db_enabled') else False,
            'host': app_config.db_host,
            'port': app_config.db_port,
            'user': app_config.db_user,
            'password': app_config.db_password,
            'name': app_config.db_name,
        },
        'redis': {
            'host': app_config.redis_host,
            'port': app_config.redis_port,
            'db': app_config.redis_db,
        },
        'chroma': {
            'host': app_config.chroma_host,
            'port': app_config.chroma_port,
        },
    })
    container.init_resources()
    return container


# 全局容器实例
container = create_container()
