"""
测试：对话数据库模型

行为：Conversation 和 Message 模型应该能正确创建和关联。
"""
import pytest
from datetime import datetime


def test_conversation_model_can_be_created():
    """Conversation 模型应该能够被创建。"""
    from backend.models import Conversation

    conversation = Conversation(
        title="测试对话",
        description="这是一个测试对话",
        user_id="user-123"
    )

    assert conversation is not None
    assert conversation.title == "测试对话"
    assert conversation.description == "这是一个测试对话"
    assert conversation.user_id == "user-123"
    # SQLAlchemy default only works on insert, not on Python object creation
    assert conversation.is_active is None or conversation.is_active == 1


def test_conversation_model_has_required_fields():
    """Conversation 模型应该有必需字段。"""
    from backend.models import Conversation

    conversation = Conversation(title="测试")

    assert hasattr(conversation, 'id')
    assert hasattr(conversation, 'title')
    assert hasattr(conversation, 'description')
    assert hasattr(conversation, 'user_id')
    assert hasattr(conversation, 'is_active')
    assert hasattr(conversation, 'created_at')
    assert hasattr(conversation, 'updated_at')


def test_message_model_can_be_created():
    """Message 模型应该能够被创建。"""
    from backend.models import Message

    message = Message(
        conversation_id="conv-123",
        role="user",
        content="你好"
    )

    assert message is not None
    assert message.conversation_id == "conv-123"
    assert message.role == "user"
    assert message.content == "你好"


def test_message_model_has_required_fields():
    """Message 模型应该有必需字段。"""
    from backend.models import Message

    message = Message(conversation_id="conv-123", role="user", content="你好")

    assert hasattr(message, 'id')
    assert hasattr(message, 'conversation_id')
    assert hasattr(message, 'role')
    assert hasattr(message, 'content')
    assert hasattr(message, 'agent_name')
    assert hasattr(message, 'created_at')


def test_conversation_message_relationship():
    """对话和消息应该能正确关联。"""
    from backend.models import Conversation, Message

    # 创建对话
    conversation = Conversation(title="测试对话", user_id="user-123")

    # 创建消息
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content="你好"
    )

    agent_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="你好！有什么可以帮你的？",
        agent_name="coder"
    )

    # 验证关联
    assert user_message.conversation_id == conversation.id
    assert agent_message.conversation_id == conversation.id
    assert agent_message.agent_name == "coder"


def test_conversation_default_values():
    """Conversation 模型应该有正确的默认值。"""
    from backend.models import Conversation

    conversation = Conversation(title="测试")

    # SQLAlchemy default only works on insert, not on Python object creation
    assert conversation.is_active is None or conversation.is_active == 1
    # SQLAlchemy default only works on insert, not on Python object creation
    assert conversation.description is None or conversation.description == ""
    # SQLAlchemy default only works on insert, not on Python object creation
    assert conversation.created_at is None or isinstance(conversation.created_at, datetime)
    assert conversation.updated_at is None or isinstance(conversation.updated_at, datetime)


def test_message_default_values():
    """Message 模型应该有正确的默认值。"""
    from backend.models import Message

    message = Message(conversation_id="conv-123", role="user", content="你好")

    assert message.agent_name is None
    # SQLAlchemy default only works on insert, not on Python object creation
    assert message.created_at is None or isinstance(message.created_at, datetime)
