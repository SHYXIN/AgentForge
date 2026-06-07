"""
数据模型定义

使用 SQLAlchemy ORM 定义数据库模型。
"""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def generate_uuid():
    """生成 UUID。"""
    return str(uuid.uuid4())


class Agent(Base):
    """Agent 模型。"""
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False)
    role = Column(String(50), nullable=False)
    description = Column(Text, default="")
    config = Column(Text, default="")  # JSON 配置
    is_active = Column(Integer, default=1, nullable=False)  # 0=禁用, 1=启用
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "config": self.config,
            "is_active": bool(self.is_active),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class User(Base):
    """用户模型。"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "user_id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Document(Base):
    """文档模型。"""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "document_id": self.id,
            "filename": self.filename,
            "content_type": self.content_type,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class Conversation(Base):
    """对话模型。"""
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True, default="新对话")
    description = Column(Text, default="")
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "is_active": bool(self.is_active),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "message_count": len(self.messages) if self.messages else 0
        }


class Message(Base):
    """消息模型。"""
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    agent_name = Column(String(50), nullable=True)
    agent_thoughts = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    conversation = relationship("Conversation", back_populates="messages")


# Pydantic 模型（用于 API）
from pydantic import BaseModel as PydanticBase


class UserCreate(PydanticBase):
    username: str
    email: str
    password: str


class UserResponse(PydanticBase):
    user_id: str
    username: str
    email: str


class LoginRequest(PydanticBase):
    username: str
    password: str


class LoginResponse(PydanticBase):
    access_token: str
    token_type: str


class DocumentCreate(PydanticBase):
    filename: str
    content_type: str
    content: bytes


class DocumentResponse(PydanticBase):
    document_id: str
    filename: str
    content_type: str
    uploaded_at: str


class ChatRequest(PydanticBase):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(PydanticBase):
    response: str
    agent_thoughts: str
    conversation_id: str


class RAGDocumentUpload(PydanticBase):
    document_id: str
    filename: str
    content_type: str
    chunks_count: int
    status: str


class RAGQueryRequest(PydanticBase):
    query: str
    top_k: int = 5


class RAGQueryResponse(PydanticBase):
    status: str
    documents: List[List[str]]
    distances: List[List[float]]
    ids: List[List[str]]


class RAGDocumentDelete(PydanticBase):
    status: str
    document_id: str
    message: str


class MultiAgentChatRequest(PydanticBase):
    """多 Agent 聊天请求"""
    message: str
    task_type: str = "user_request"


class MultiAgentChatResponse(PydanticBase):
    """多 Agent 聊天响应"""
    task_id: str
    response: str
    result: Optional[dict] = None
    error: Optional[str] = None


class TaskStatusResponse(PydanticBase):
    """任务状态响应"""
    task_id: str
    status: str
    message: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
