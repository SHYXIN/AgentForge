"""
测试：Repository 接口和内存实现

行为：Repository 应该能够通过接口访问数据。
"""
import pytest
from typing import Optional


def test_user_repository_interface_exists():
    """UserRepository 接口应该存在。"""
    from backend.repositories.base import UserRepository
    from backend.models import UserCreate, User

    # 验证接口存在
    assert UserRepository is not None


def test_in_memory_user_repository_can_be_created():
    """InMemoryUserRepository 应该能够被创建。"""
    from backend.repositories.memory import InMemoryUserRepository

    repo = InMemoryUserRepository()
    assert repo is not None


def test_in_memory_user_repository_can_create_user():
    """InMemoryUserRepository 应该能够创建用户。"""
    import asyncio
    from backend.repositories.memory import InMemoryUserRepository
    from backend.models import UserCreate

    async def test():
        repo = InMemoryUserRepository()
        user = await repo.create(UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        ))
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    asyncio.run(test())


def test_in_memory_user_repository_can_get_user():
    """InMemoryUserRepository 应该能够获取用户。"""
    import asyncio
    from backend.repositories.memory import InMemoryUserRepository
    from backend.models import UserCreate

    async def test():
        repo = InMemoryUserRepository()
        created = await repo.create(UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        ))

        # 通过 ID 获取
        user = await repo.get_by_id(created.id)
        assert user is not None
        assert user.username == "testuser"

        # 通过用户名获取
        user = await repo.get_by_username("testuser")
        assert user is not None
        assert user.id == created.id

    asyncio.run(test())


def test_in_memory_user_repository_can_delete_user():
    """InMemoryUserRepository 应该能够删除用户。"""
    import asyncio
    from backend.repositories.memory import InMemoryUserRepository
    from backend.models import UserCreate

    async def test():
        repo = InMemoryUserRepository()
        user = await repo.create(UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        ))

        # 删除用户
        result = await repo.delete(user.id)
        assert result is True

        # 验证已删除
        deleted = await repo.get_by_id(user.id)
        assert deleted is None

    asyncio.run(test())
