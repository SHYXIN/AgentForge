"""
MySQL Repository 实现模块

提供基于 MySQL 的 Repository 实现。
"""
from typing import Optional, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

from backend.config import AppConfig
from backend.models import Base, User as UserModel, UserCreate, Document as DocumentModel, DocumentCreate


class MySQLUserRepository:
    """用户 MySQL 存储实现。"""

    def __init__(self, session: Session):
        self.session = session

    async def create(self, user: UserCreate) -> UserModel:
        """创建用户。"""
        # 检查用户名是否已存在
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


def get_mysql_session() -> Session:
    """获取 MySQL 会话。"""
    config = AppConfig()
    db_url = f"mysql+pymysql://{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.name}"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
