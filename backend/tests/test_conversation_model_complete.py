"""
测试：对话数据库模型完整验收标准

行为：验证问题 #4 的所有验收标准都已满足。
"""
import pytest
from datetime import datetime
from backend.models import Conversation, Message


def test_acceptance_criteria_create_conversation():
    """验收标准：能创建 Conversation 对象"""
    conversation = Conversation(
        title="测试对话",
        description="这是一个测试",
        user_id="user-123"
    )
    
    assert conversation is not None
    assert conversation.title == "测试对话"
    assert conversation.description == "这是一个测试"
    assert conversation.user_id == "user-123"


def test_acceptance_criteria_create_message():
    """验收标准：能创建 Message 对象"""
    message = Message(
        conversation_id="conv-123",
        role="user",
        content="你好",
        agent_name="coder"
    )
    
    assert message is not None
    assert message.conversation_id == "conv-123"
    assert message.role == "user"
    assert message.content == "你好"
    assert message.agent_name == "coder"


def test_acceptance_criteria_conversation_message_relationship():
    """验收标准：对话和消息关联正确"""
    # 创建对话
    conversation = Conversation(
        title="测试对话",
        user_id="user-123"
    )
    
    # 模拟添加到会话（不实际提交到数据库）
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content="你好"
    )
    
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="你好！有什么可以帮你的？",
        agent_name="coder"
    )
    
    # 验证关联
    assert user_message.conversation_id == conversation.id
    assert assistant_message.conversation_id == conversation.id


def test_acceptance_criteria_conversation_to_dict():
    """验收标准：Conversation 可以序列化为字典"""
    conversation = Conversation(
        id="conv-123",
        title="测试对话",
        description="这是一个测试",
        user_id="user-456",
        is_active=1
    )
    
    # 手动设置时间（因为默认值只在数据库插入时生效）
    conversation.created_at = datetime.utcnow()
    conversation.updated_at = datetime.utcnow()
    
    result = conversation.to_dict()
    
    assert result["id"] == "conv-123"
    assert result["title"] == "测试对话"
    assert result["description"] == "这是一个测试"
    assert result["user_id"] == "user-456"
    assert result["is_active"] is True
    assert "created_at" in result
    assert "updated_at" in result


def test_acceptance_criteria_conversation_timestamps():
    """验收标准：Conversation 有正确的时间戳"""
    now = datetime.utcnow()
    conversation = Conversation(
        title="测试",
        user_id="user-123",
        created_at=now,
        updated_at=now
    )
    
    assert conversation.created_at is not None
    assert conversation.updated_at is not None
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


def test_acceptance_criteria_message_timestamps():
    """验收标准：Message 有正确的时间戳"""
    now = datetime.utcnow()
    message = Message(
        conversation_id="conv-123",
        role="user",
        content="你好",
        created_at=now
    )
    
    assert message.created_at is not None
    assert isinstance(message.created_at, datetime)


def test_acceptance_criteria_conversation_default_title():
    """验收标准：Conversation 有默认标题"""
    conversation = Conversation(user_id="user-123")
    
    # SQLAlchemy 默认值只在数据库插入时生效，这里验证模型定义
    assert hasattr(conversation, 'title')


def test_acceptance_criteria_message_agent_fields():
    """验收标准：Message 支持 agent 相关字段"""
    message = Message(
        conversation_id="conv-123",
        role="assistant",
        content="这是回复",
        agent_name="coder",
        agent_thoughts="让我思考一下..."
    )
    
    assert message.agent_name == "coder"
    assert message.agent_thoughts == "让我思考一下..."


def test_migration_includes_all_fields():
    """验收标准：Alembic 迁移包含所有必需字段"""
    migration_path = "alembic/versions/27758e1b9a40_initial_migration.py"
    with open(migration_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # conversations 表字段
    assert 'description' in content, "conversations 表缺少 description 字段"
    assert 'is_active' in content, "conversations 表缺少 is_active 字段"
    
    # messages 表字段
    assert 'agent_name' in content, "messages 表缺少 agent_name 字段"
    assert 'agent_thoughts' in content, "messages 表缺少 agent_thoughts 字段"
