"""
Seed 配置模块

通过环境变量配置 seed 数据。
"""
import os
from pydantic_settings import BaseSettings


class SeedConfig(BaseSettings):
    """Seed 配置。"""

    # 环境：development, production, test
    env: str = "development"

    # 默认管理员用户
    admin_username: str = "admin"
    admin_email: str = "admin@example.com"
    admin_password: str = "admin123"

    # 测试用户
    test_username: str = "testuser"
    test_email: str = "test@example.com"
    test_password: str = "test123"

    # 是否清理旧数据
    clean_before_seed: bool = True

    class Config:
        env_prefix = "SEED_"
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_config() -> SeedConfig:
    """获取 seed 配置。"""
    return SeedConfig()
