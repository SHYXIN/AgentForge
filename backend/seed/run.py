#!/usr/bin/env python3
"""
Seed 数据初始化脚本

用法:
    python seed/run.py                    # 默认 development 环境
    python seed/run.py --env production   # production 环境
    python seed/run.py --env test         # test 环境
    python seed/run.py --no-clean         # 不清理旧数据
"""
import asyncio
import argparse
import sys
import os

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.seed.config import get_config
from backend.seed.users import seed_users
from backend.seed.documents import seed_documents
from backend.seed.conversations import seed_conversations
from backend.seed.rag_documents import seed_rag_documents


async def run_seed(env: str = "development", clean: bool = True):
    """运行 seed 数据初始化。

    Args:
        env: 环境名称
        clean: 是否清理旧数据
    """
    print(f"=" * 60)
    print(f"开始初始化 seed 数据")
    print(f"环境: {env}")
    print(f"清理旧数据: {clean}")
    print(f"=" * 60)

    # 1. 创建用户数据
    print("\n[1/4] 创建用户数据...")
    await seed_users(clean=clean)

    # 2. 创建文档数据
    print("\n[2/4] 创建文档数据...")
    await seed_documents(clean=clean)

    # 3. 创建对话数据
    print("\n[3/4] 创建对话数据...")
    await seed_conversations(clean=clean)

    # 4. 创建知识库文档数据
    print("\n[4/4] 创建知识库文档数据...")
    await seed_rag_documents(clean=clean)

    print(f"\n{'=' * 60}")
    print(f"Seed 数据初始化完成!")
    print(f"{'=' * 60}")


def main():
    """主函数。"""
    parser = argparse.ArgumentParser(description="Seed 数据初始化脚本")
    parser.add_argument(
        "--env",
        type=str,
        default="development",
        choices=["development", "production", "test"],
        help="环境名称 (default: development)"
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="不清理旧数据"
    )

    args = parser.parse_args()

    # 运行 seed
    asyncio.run(run_seed(
        env=args.env,
        clean=not args.no_clean
    ))


if __name__ == "__main__":
    main()
