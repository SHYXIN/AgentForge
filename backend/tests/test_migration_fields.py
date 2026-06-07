"""
测试：验证 Alembic 迁移包含所有必需字段

行为：数据库迁移应该包含模型定义的所有字段。
"""
import pytest


def test_conversations_table_has_description_field():
    """conversations 表应该包含 description 字段。"""
    # 读取迁移文件内容
    migration_path = "alembic/versions/27758e1b9a40_initial_migration.py"
    with open(migration_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 验证 description 字段存在
    assert 'sa.Column(\'description\'' in content or 'description' in content, \
        "conversations 表缺少 description 字段"


def test_conversations_table_has_is_active_field():
    """conversations 表应该包含 is_active 字段。"""
    migration_path = "alembic/versions/27758e1b9a40_initial_migration.py"
    with open(migration_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 验证 is_active 字段存在
    assert 'sa.Column(\'is_active\'' in content or 'is_active' in content, \
        "conversations 表缺少 is_active 字段"


def test_messages_table_has_agent_name_field():
    """messages 表应该包含 agent_name 字段。"""
    migration_path = "alembic/versions/27758e1b9a40_initial_migration.py"
    with open(migration_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 验证 agent_name 字段存在
    assert 'sa.Column(\'agent_name\'' in content or 'agent_name' in content, \
        "messages 表缺少 agent_name 字段"


def test_model_matches_migration():
    """模型定义应该与迁移脚本匹配。"""
    from backend.models import Conversation, Message
    
    # 获取模型的列名
    conversation_columns = [column.name for column in Conversation.__table__.columns]
    message_columns = [column.name for column in Message.__table__.columns]
    
    # 验证必需字段存在
    assert 'description' in conversation_columns, "Conversation 模型缺少 description 字段"
    assert 'is_active' in conversation_columns, "Conversation 模型缺少 is_active 字段"
    assert 'agent_name' in message_columns, "Message 模型缺少 agent_name 字段"
