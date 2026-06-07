"""
测试：对话 Repository

行为：对话 Repository 应该能正确创建、读取、更新、删除对话。
"""
import pytest
import asyncio
from datetime import datetime
from backend.models import Conversation, Message


@pytest.fixture
def conversation_repo():
    """创建内存对话 Repository。"""
    from backend.repositories.conversation_memory import InMemoryConversationRepository
    return InMemoryConversationRepository()


@pytest.fixture
def message_repo():
    """创建内存消息 Repository。"""
    from backend.repositories.conversation_memory import InMemoryMessageRepository
    return InMemoryMessageRepository()


@pytest.mark.asyncio
async def test_create_conversation(conversation_repo):
    """应该能创建对话。"""
    conversation = Conversation(
        user_id="user-123",
        title="测试对话",
        description="这是一个测试",
        is_active=1
    )
    
    created = await conversation_repo.create(conversation)
    
    assert created is not None
    assert created.id is not None
    assert created.user_id == "user-123"
    assert created.title == "测试对话"
    assert created.created_at is not None


@pytest.mark.asyncio
async def test_get_conversation_by_id(conversation_repo):
    """应该能通过 ID 获取对话。"""
    conversation = Conversation(
        user_id="user-123",
        title="测试对话",
        is_active=1
    )
    created = await conversation_repo.create(conversation)
    
    fetched = await conversation_repo.get_by_id(created.id)
    
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "测试对话"


@pytest.mark.asyncio
async def test_list_conversations_by_user(conversation_repo):
    """应该能获取用户的所有对话。"""
    # 创建多个对话
    for i in range(3):
        await conversation_repo.create(Conversation(
            user_id="user-123",
            title=f"对话 {i}",
            is_active=1
        ))
    
    # 创建其他用户的对话
    await conversation_repo.create(Conversation(
        user_id="user-456",
        title="其他用户的对话",
        is_active=1
    ))
    
    conversations = await conversation_repo.list_by_user("user-123")
    
    assert len(conversations) == 3
    assert all(conv.user_id == "user-123" for conv in conversations)


@pytest.mark.asyncio
async def test_update_conversation(conversation_repo):
    """应该能更新对话。"""
    conversation = Conversation(
        user_id="user-123",
        title="旧标题",
        is_active=1
    )
    created = await conversation_repo.create(conversation)
    
    created.title = "新标题"
    updated = await conversation_repo.update(created)
    
    assert updated is not None
    assert updated.title == "新标题"
    
    # 验证已更新
    fetched = await conversation_repo.get_by_id(created.id)
    assert fetched.title == "新标题"


@pytest.mark.asyncio
async def test_delete_conversation(conversation_repo):
    """应该能删除对话。"""
    conversation = Conversation(
        user_id="user-123",
        title="待删除",
        is_active=1
    )
    created = await conversation_repo.create(conversation)
    
    result = await conversation_repo.delete(created.id)
    
    assert result is True
    
    # 验证已删除
    fetched = await conversation_repo.get_by_id(created.id)
    assert fetched is None


@pytest.mark.asyncio
async def test_create_message(message_repo):
    """应该能创建消息。"""
    message = Message(
        conversation_id="conv-123",
        role="user",
        content="你好"
    )
    
    created = await message_repo.create(message)
    
    assert created is not None
    assert created.id is not None
    assert created.conversation_id == "conv-123"
    assert created.role == "user"
    assert created.content == "你好"


@pytest.mark.asyncio
async def test_list_messages_by_conversation(message_repo):
    """应该能获取对话的所有消息。"""
    # 创建多个消息
    for i in range(3):
        await message_repo.create(Message(
            conversation_id="conv-123",
            role="user" if i % 2 == 0 else "assistant",
            content=f"消息 {i}"
        ))
    
    # 创建其他对话的消息
    await message_repo.create(Message(
        conversation_id="conv-456",
        role="user",
        content="其他对话的消息"
    ))
    
    messages = await message_repo.list_by_conversation("conv-123")
    
    assert len(messages) == 3
    assert all(msg.conversation_id == "conv-123" for msg in messages)


@pytest.mark.asyncio
async def test_delete_messages_by_conversation(message_repo):
    """应该能删除对话的所有消息。"""
    # 创建消息
    for i in range(3):
        await message_repo.create(Message(
            conversation_id="conv-123",
            role="user",
            content=f"消息 {i}"
        ))
    
    result = await message_repo.delete_by_conversation("conv-123")
    
    assert result is True
    
    # 验证已删除
    messages = await message_repo.list_by_conversation("conv-123")
    assert len(messages) == 0
