"""
用户数据种子模块

创建默认用户和测试用户。
"""
import sys
import os

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.models import UserCreate
from backend.container import get_memory_user_repository


async def seed_users(clean: bool = True):
    """创建用户数据。

    Args:
        clean: 是否清理旧数据
    """
    user_repo = get_memory_user_repository()

    if clean:
        print("清理旧用户数据...")
        # 清理现有用户
        users_to_remove = [uid for uid, u in user_repo.users.items() if u.username in ["admin", "testuser"]]
        for uid in users_to_remove:
            del user_repo.users[uid]

    # 创建管理员用户
    try:
        admin = await user_repo.create(UserCreate(
            username="admin",
            email="admin@example.com",
            password="admin123"
        ))
        print(f"管理员用户创建成功: {admin.username} (ID: {admin.id})")
    except ValueError:
        print("管理员用户已存在，跳过")

    # 创建测试用户
    try:
        test_user = await user_repo.create(UserCreate(
            username="testuser",
            email="test@example.com",
            password="test123"
        ))
        print(f"测试用户创建成功: {test_user.username} (ID: {test_user.id})")
    except ValueError:
        print("测试用户已存在，跳过")

    print(f"用户数据种子完成")
