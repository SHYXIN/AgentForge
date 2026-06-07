"""
Repository 接口定义模块

定义所有 Repository 的接口（Protocol），实现依赖倒置。
"""
from typing import Optional, List, Protocol
from backend.models import User, UserCreate, Document, DocumentResponse, Conversation, Message, Agent


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


class ConversationRepository(Protocol):
    """对话数据访问接口。"""
    
    async def create(self, conversation: Conversation) -> Conversation:
        """创建对话。"""
        ...
    
    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """通过 ID 获取对话。"""
        ...
    
    async def list_by_user(self, user_id: str) -> List[Conversation]:
        """获取用户的所有对话。"""
        ...
    
    async def update(self, conversation: Conversation) -> Conversation:
        """更新对话。"""
        ...
    
    async def delete(self, conversation_id: str) -> bool:
        """删除对话。"""
        ...


class MessageRepository(Protocol):
    """消息数据访问接口。"""
    
    async def create(self, message: Message) -> Message:
        """创建消息。"""
        ...
    
    async def list_by_conversation(self, conversation_id: str) -> List[Message]:
        """获取对话的所有消息。"""
        ...
    
    async def delete_by_conversation(self, conversation_id: str) -> bool:
        """删除对话的所有消息。"""
        ...


class AgentRepository(Protocol):
    """Agent 数据访问接口。"""
    
    async def create(self, agent: Agent) -> Agent:
        """创建 Agent。"""
        ...
    
    async def get_by_id(self, agent_id: str) -> Optional[Agent]:
        """通过 ID 获取 Agent。"""
        ...
    
    async def get_by_name(self, name: str) -> Optional[Agent]:
        """通过名称获取 Agent。"""
        ...
    
    async def list_all(self) -> List[Agent]:
        """获取所有 Agent。"""
        ...
    
    async def list_active(self) -> List[Agent]:
        """获取所有启用的 Agent。"""
        ...
    
    async def update(self, agent: Agent) -> Agent:
        """更新 Agent。"""
        ...
    
    async def delete(self, agent_id: str) -> bool:
        """删除 Agent。"""
        ...
    
    async def enable(self, agent_id: str) -> bool:
        """启用 Agent。"""
        ...
    
    async def disable(self, agent_id: str) -> bool:
        """禁用 Agent。"""
        ...
