"""
Agent 数据种子模块

创建测试 Agent 数据。
"""
import sys
import os

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


async def seed_agents(clean: bool = True):
    """创建 Agent 数据。

    Args:
        clean: 是否清理旧数据
    """
    from backend.container import container
    
    agent_repo = container.agent_repository()
    
    # 如果不清空，检查是否已有数据
    if not clean:
        existing = await agent_repo.list_all()
        if existing:
            print(f"已有 {len(existing)} 个 Agent，跳过 Agent 数据种子")
            return
    
    # 定义默认 Agent
    default_agents = [
        {
            "name": "coder",
            "role": "代码工程师",
            "description": "负责编写、优化和调试代码",
            "config": '{"model": "gpt-4", "temperature": 0.7}',
            "is_active": 1,
        },
        {
            "name": "researcher",
            "role": "研究员",
            "description": "负责信息检索、分析和总结",
            "config": '{"model": "gpt-4", "temperature": 0.3}',
            "is_active": 1,
        },
        {
            "name": "writer",
            "role": "作家",
            "description": "负责撰写和编辑文档、文章",
            "config": '{"model": "gpt-4", "temperature": 0.8}',
            "is_active": 1,
        },
        {
            "name": "analyzer",
            "role": "分析师",
            "description": "负责数据分析和报告生成",
            "config": '{"model": "gpt-4", "temperature": 0.2}',
            "is_active": 1,
        },
        {
            "name": "translator",
            "role": "翻译员",
            "description": "负责多语言翻译",
            "config": '{"model": "gpt-4", "temperature": 0.5}',
            "is_active": 0,  # 默认禁用
        },
    ]
    
    # 创建 Agent
    for agent_data in default_agents:
        try:
            # 检查是否已存在
            existing = await agent_repo.get_by_name(agent_data["name"])
            if existing:
                print(f"Agent '{agent_data['name']}' 已存在，跳过")
                continue
            
            from backend.models import Agent
            import uuid
            from datetime import datetime
            
            now = datetime.utcnow()
            agent = Agent(
                id=str(uuid.uuid4()),
                name=agent_data["name"],
                role=agent_data["role"],
                description=agent_data["description"],
                config=agent_data["config"],
                is_active=agent_data["is_active"],
                created_at=now,
                updated_at=now,
            )
            
            await agent_repo.create(agent)
            print(f"创建 Agent: {agent_data['name']} ({agent_data['role']})")
        except Exception as e:
            print(f"创建 Agent '{agent_data['name']}' 失败: {e}")
    
    print(f"Agent 数据种子完成")
