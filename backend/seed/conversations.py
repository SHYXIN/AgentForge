"""
对话数据种子模块

创建测试对话和消息。
"""
import sys
import os

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


async def seed_conversations(clean: bool = True):
    """创建对话数据。

    Args:
        clean: 是否清理旧数据
    """
    # TODO: 实现 ConversationRepository 后添加对话数据种子
    print("对话数据种子需要 ConversationRepository 实现")
    print("跳过对话数据种子")
    print(f"对话数据种子完成")
