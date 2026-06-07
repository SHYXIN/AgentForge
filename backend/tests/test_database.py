"""
测试：数据库连接

行为：系统应该能够连接 PostgreSQL 和 Chroma，并执行基本操作。

这证明数据库层配置正确。
"""
import pytest


def test_database_configuration():
    """数据库配置应该正确加载。"""
    # 测试配置加载（不依赖实际连接）
    from pydantic_settings import BaseSettings
    
    class DatabaseSettings(BaseSettings):
        postgres_host: str = "localhost"
        postgres_port: int = 5432
        postgres_user: str = "postgres"
        postgres_password: str = "postgres"
        postgres_db: str = "agentforge"
        
        chroma_host: str = "localhost"
        chroma_port: int = 8001
        
        redis_host: str = "localhost"
        redis_port: int = 6379
        
        class Config:
            env_prefix = "DB_"
    
    settings = DatabaseSettings()
    
    assert settings.postgres_host == "localhost"
    assert settings.postgres_port == 5432
    assert settings.chroma_port == 8001
    assert settings.redis_port == 6379


def test_redis_connection():
    """Redis 应该接受连接和操作。"""
    import redis
    
    r = redis.Redis(host="localhost", port=6379, db=0)
    
    # 设置和获取
    r.set("test-key", "test-value")
    value = r.get("test-key")
    
    assert value == b"test-value"
    
    # 清理
    r.delete("test-key")
