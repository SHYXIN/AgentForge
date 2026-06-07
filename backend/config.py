"""
配置管理模块

提供统一的配置管理，支持环境变量和默认值。
"""
import os
from pathlib import Path

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


class AppConfig:
    """应用配置。"""

    # LLM 配置
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.longcat.chat/openai")
    openai_model: str = os.getenv("OPENAI_MODEL", "LongCat-2.0-Preview")

    # BGE 嵌入模型路径
    bge_model_path: str = os.getenv("BGE_MODEL_PATH", "backend/fast-bge-small-zh-v1.5")

    # Chroma 配置
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
    chroma_host: str = os.getenv("CHROMA_HOST", "localhost")
    chroma_port: int = int(os.getenv("CHROMA_PORT", "8001"))

    # Repository 配置
    repo_backend: str = os.getenv("REPO_BACKEND", "memory")

    # 数据库配置
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "123456")
    db_name: str = os.getenv("DB_NAME", "agentforge")

    # Redis 配置
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))

    # 应用配置
    debug: bool = os.getenv("APP_DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("APP_LOG_LEVEL", "INFO")


# 全局配置实例
config = AppConfig()
