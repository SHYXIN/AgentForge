"""
MySQL Repository 实现模块

提供基于 MySQL 的 Repository 实现。
"""
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.config import AppConfig
from backend.models import (
    Base, User as UserModel, UserCreate, 
    Document as DocumentModel,
    Conversation as ConversationModel,
    Message as MessageModel,
    Agent as AgentModel,
)


class MySQLUserRepository:
    """用户 MySQL 存储实现。"""

    def __init__(self, session: Session):
        self.session = session

    async def create(self, user: UserCreate) -> UserModel:
        """创建用户。"""
        existing = await self.get_by_username(user.username)
        if existing:
            raise ValueError(f"用户名 {user.username} 已存在")

        new_user = UserModel(
            username=user.username,
            email=user.email,
            password=user.password,
        )

        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)

        return new_user

    async def get_by_id(self, user_id: str) -> Optional[UserModel]:
        """通过 ID 获取用户。"""
        return self.session.query(UserModel).filter(UserModel.id == user_id).first()

    async def get_by_username(self, username: str) -> Optional[UserModel]:
        """通过用户名获取用户。"""
        return self.session.query(UserModel).filter(UserModel.username == username).first()

    async def delete(self, user_id: str) -> bool:
        """删除用户。"""
        user = await self.get_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False


class MySQLDocumentRepository:
    """文档 MySQL 存储实现。"""

    def __init__(self, session: Session):
        self.session = session

    async def create(self, filename: str, content_type: str, content: bytes) -> DocumentModel:
        """创建文档。"""
        new_doc = DocumentModel(
            filename=filename,
            content_type=content_type,
            content=content,
        )

        self.session.add(new_doc)
        self.session.commit()
        self.session.refresh(new_doc)

        return new_doc

    async def get_by_id(self, document_id: str) -> Optional[DocumentModel]:
        """通过 ID 获取文档。"""
        return self.session.query(DocumentModel).filter(DocumentModel.id == document_id).first()

    async def list_all(self) -> List[DocumentModel]:
        """获取所有文档。"""
        return self.session.query(DocumentModel).all()

    async def delete(self, document_id: str) -> bool:
        """删除文档。"""
        doc = await self.get_by_id(document_id)
        if doc:
            self.session.delete(doc)
            self.session.commit()
            return True
        return False


class MySQLConversationRepository:
    """对话 MySQL 存储实现。"""

    def __init__(self, session: Session):
        self.session = session

    async def create(self, conversation: ConversationModel) -> ConversationModel:
        """创建对话。"""
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    async def get_by_id(self, conversation_id: str) -> Optional[ConversationModel]:
        """通过 ID 获取对话。"""
        return self.session.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()

    async def list_by_user(self, user_id: str) -> List[ConversationModel]:
        """获取用户的所有对话。"""
        return self.session.query(ConversationModel).filter(ConversationModel.user_id == user_id).all()

    async def update(self, conversation: ConversationModel) -> ConversationModel:
        """更新对话。"""
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    async def delete(self, conversation_id: str) -> bool:
        """删除对话。"""
        conversation = await self.get_by_id(conversation_id)
        if conversation:
            self.session.delete(conversation)
            self.session.commit()
            return True
        return False


class MySQLMessageRepository:
    """消息 MySQL 存储实现。"""

    def __init__(self, session: Session):
        self.session = session

    async def create(self, message: MessageModel) -> MessageModel:
        """创建消息。"""
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    async def list_by_conversation(self, conversation_id: str) -> List[MessageModel]:
        """获取对话的所有消息。"""
        return self.session.query(MessageModel).filter(MessageModel.conversation_id == conversation_id).all()

    async def delete_by_conversation(self, conversation_id: str) -> bool:
        """删除对话的所有消息。"""
        messages = await self.list_by_conversation(conversation_id)
        for msg in messages:
            self.session.delete(msg)
        self.session.commit()
        return len(messages) > 0


class MySQLAgentRepository:
    """Agent MySQL 存储实现。"""

    def __init__(self, session: Session):
        self.session = session

    async def create(self, agent: AgentModel) -> AgentModel:
        """创建 Agent。"""
        self.session.add(agent)
        self.session.commit()
        self.session.refresh(agent)
        return agent

    async def get_by_id(self, agent_id: str) -> Optional[AgentModel]:
        """通过 ID 获取 Agent。"""
        return self.session.query(AgentModel).filter(AgentModel.id == agent_id).first()

    async def get_by_name(self, name: str) -> Optional[AgentModel]:
        """通过名称获取 Agent。"""
        return self.session.query(AgentModel).filter(AgentModel.name == name).first()

    async def list_all(self) -> List[AgentModel]:
        """获取所有 Agent。"""
        return self.session.query(AgentModel).all()

    async def list_active(self) -> List[AgentModel]:
        """获取所有启用的 Agent。"""
        return self.session.query(AgentModel).filter(AgentModel.is_active == 1).all()

    async def update(self, agent: AgentModel) -> AgentModel:
        """更新 Agent。"""
        self.session.commit()
        self.session.refresh(agent)
        return agent

    async def delete(self, agent_id: str) -> bool:
        """删除 Agent。"""
        agent = await self.get_by_id(agent_id)
        if agent:
            self.session.delete(agent)
            self.session.commit()
            return True
        return False

    async def enable(self, agent_id: str) -> bool:
        """启用 Agent。"""
        agent = await self.get_by_id(agent_id)
        if agent:
            agent.is_active = 1
            self.session.commit()
            return True
        return False

    async def disable(self, agent_id: str) -> bool:
        """禁用 Agent。"""
        agent = await self.get_by_id(agent_id)
        if agent:
            agent.is_active = 0
            self.session.commit()
            return True
        return False


def get_mysql_session() -> Session:
    """获取 MySQL 会话。"""
    config = AppConfig()
    db_url = f"mysql+pymysql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
