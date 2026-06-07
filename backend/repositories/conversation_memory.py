"""
对话内存 Repository 实现模块

提供基于内存的对话和消息 Repository 实现，用于开发和测试。
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict

from backend.models import Conversation, Message
from backend.repositories.base import ConversationRepository, MessageRepository


class InMemoryConversationRepository(ConversationRepository):
    """对话内存存储实现。"""

    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}

    async def create(self, conversation: Conversation) -> Conversation:
        """创建对话。"""
        if not conversation.id:
            conversation.id = str(uuid.uuid4())
        
        now = datetime.utcnow()
        conversation.created_at = now
        conversation.updated_at = now
        
        self.conversations[conversation.id] = conversation
        return conversation

    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """通过 ID 获取对话。"""
        return self.conversations.get(conversation_id)

    async def list_by_user(self, user_id: str) -> List[Conversation]:
        """获取用户的所有对话。"""
        return [
            conv for conv in self.conversations.values()
            if conv.user_id == user_id
        ]

    async def update(self, conversation: Conversation) -> Conversation:
        """更新对话。"""
        if conversation.id in self.conversations:
            conversation.updated_at = datetime.utcnow()
            self.conversations[conversation.id] = conversation
            return conversation
        return None

    async def delete(self, conversation_id: str) -> bool:
        """删除对话。"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False


class InMemoryMessageRepository(MessageRepository):
    """消息内存存储实现。"""

    def __init__(self):
        self.messages: Dict[str, Message] = {}

    async def create(self, message: Message) -> Message:
        """创建消息。"""
        if not message.id:
            message.id = str(uuid.uuid4())
        
        now = datetime.utcnow()
        message.created_at = now
        
        self.messages[message.id] = message
        return message

    async def list_by_conversation(self, conversation_id: str) -> List[Message]:
        """获取对话的所有消息。"""
        return [
            msg for msg in self.messages.values()
            if msg.conversation_id == conversation_id
        ]

    async def delete_by_conversation(self, conversation_id: str) -> bool:
        """删除对话的所有消息。"""
        message_ids = [
            msg_id for msg_id, msg in self.messages.items()
            if msg.conversation_id == conversation_id
        ]
        for msg_id in message_ids:
            del self.messages[msg_id]
        return len(message_ids) > 0
