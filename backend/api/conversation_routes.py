"""
对话 API 路由模块

提供对话的 CRUD 操作。
"""
import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.models import Conversation, Message
from backend.container import container


router = APIRouter(prefix="/api/conversations", tags=["conversations"])


# ============ Pydantic 模型 ============

class CreateConversationRequest(BaseModel):
    title: str = "新对话"
    description: str = ""
    user_id: str


class UpdateConversationRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]
    message_count: int = 0


# ============ API 端点 ============

@router.post("", status_code=201)
async def create_conversation(request: CreateConversationRequest):
    """创建新对话。"""
    conversation_repo = container.conversation_repository()
    
    now = datetime.utcnow()
    conversation = Conversation(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        title=request.title,
        description=request.description,
        is_active=1,
        created_at=now,
        updated_at=now
    )
    
    created = await conversation_repo.create(conversation)
    
    return {
        "id": created.id,
        "user_id": created.user_id,
        "title": created.title,
        "description": created.description,
        "is_active": bool(created.is_active),
        "created_at": created.created_at.isoformat() if created.created_at else None,
        "updated_at": created.updated_at.isoformat() if created.updated_at else None,
        "message_count": 0
    }


@router.get("")
async def list_conversations(user_id: str = Query(..., description="用户 ID")):
    """获取对话列表。"""
    conversation_repo = container.conversation_repository()
    
    conversations = await conversation_repo.list_by_user(user_id)
    
    result = []
    for conv in conversations:
        result.append({
            "id": conv.id,
            "user_id": conv.user_id,
            "title": conv.title,
            "description": conv.description,
            "is_active": bool(conv.is_active),
            "created_at": conv.created_at.isoformat() if conv.created_at else None,
            "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
            "message_count": 0  # TODO: 查询消息数量
        })
    
    return result


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    """获取单个对话。"""
    conversation_repo = container.conversation_repository()
    
    conversation = await conversation_repo.get_by_id(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "description": conversation.description,
        "is_active": bool(conversation.is_active),
        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
        "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
        "message_count": 0  # TODO: 查询消息数量
    }


@router.put("/{conversation_id}")
async def update_conversation(conversation_id: str, request: UpdateConversationRequest):
    """更新对话（重命名）。"""
    conversation_repo = container.conversation_repository()
    
    conversation = await conversation_repo.get_by_id(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    if request.title is not None:
        conversation.title = request.title
    if request.description is not None:
        conversation.description = request.description
    
    updated = await conversation_repo.update(conversation)
    
    return {
        "id": updated.id,
        "user_id": updated.user_id,
        "title": updated.title,
        "description": updated.description,
        "is_active": bool(updated.is_active),
        "created_at": updated.created_at.isoformat() if updated.created_at else None,
        "updated_at": updated.updated_at.isoformat() if updated.updated_at else None,
        "message_count": 0  # TODO: 查询消息数量
    }


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str):
    """删除对话。"""
    conversation_repo = container.conversation_repository()
    message_repo = container.message_repository()
    
    # 先删除所有消息
    await message_repo.delete_by_conversation(conversation_id)
    
    # 再删除对话
    result = await conversation_repo.delete(conversation_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return None
