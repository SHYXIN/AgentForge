"""
内存 Repository 实现模块

提供基于内存的 Repository 实现，用于开发和测试。
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict

from backend.models import User, UserCreate, Document
from backend.repositories.base import UserRepository, DocumentRepository


class InMemoryUserRepository:
    """用户内存存储实现。"""

    def __init__(self):
        self.users: Dict[str, User] = {}

    async def create(self, user: UserCreate) -> User:
        """创建用户。"""
        # 检查用户名是否已存在
        for existing in self.users.values():
            if existing.username == user.username:
                raise ValueError(f"用户名 {user.username} 已存在")

        user_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        new_user = User(
            id=user_id,
            username=user.username,
            email=user.email,
            password=user.password,
            created_at=now
        )

        self.users[user_id] = new_user
        return new_user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """通过 ID 获取用户。"""
        return self.users.get(user_id)

    async def get_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户。"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    async def delete(self, user_id: str) -> bool:
        """删除用户。"""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False


class InMemoryDocumentRepository:
    """文档内存存储实现。"""

    def __init__(self):
        self.documents: Dict[str, Document] = {}

    async def create(self, filename: str, content_type: str, content: bytes) -> Document:
        """创建文档。"""
        document_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        doc = Document(
            id=document_id,
            filename=filename,
            content_type=content_type,
            content=content,
            uploaded_at=now
        )

        self.documents[document_id] = doc
        return doc

    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """通过 ID 获取文档。"""
        return self.documents.get(document_id)

    async def list_all(self) -> List[Document]:
        """获取所有文档。"""
        return list(self.documents.values())

    async def delete(self, document_id: str) -> bool:
        """删除文档。"""
        if document_id in self.documents:
            del self.documents[document_id]
            return True
        return False
