"""
Repository 接口定义模块

定义所有 Repository 的接口（Protocol），实现依赖倒置。
"""
from typing import Optional, List, Protocol
from backend.models import User, UserCreate, Document, DocumentResponse


class UserRepository(Protocol):
    """用户数据访问接口。"""
    
    async def create(self, user: UserCreate) -> User:
        """创建用户。"""
        ...
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """通过 ID 获取用户。"""
        ...
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户。"""
        ...
    
    async def delete(self, user_id: str) -> bool:
        """删除用户。"""
        ...


class DocumentRepository(Protocol):
    """文档数据访问接口。"""
    
    async def create(self, filename: str, content_type: str, content: bytes) -> Document:
        """创建文档。"""
        ...
    
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """通过 ID 获取文档。"""
        ...
    
    async def list_all(self) -> List[Document]:
        """获取所有文档。"""
        ...
    
    async def delete(self, document_id: str) -> bool:
        """删除文档。"""
        ...
