"""
多 Agent 协作服务模块

提供 AgentForge 的多 Agent 协作功能，包括：
- Agent 基类定义
- Orchestrator、Coder、Researcher 等专业 Agent
- Agent 间通信和协作机制
- 任务分解和并行执行
"""
import asyncio
import uuid
from enum import Enum
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from uuid import uuid4

# 导入 RAG 服务
from backend.services.rag import RAGPipeline


# ============ 枚举定义 ============

class AgentRole(Enum):
    """Agent 角色枚举"""
    ORCHESTRATOR = "orchestrator"
    CODER = "coder"
    RESEARCHER = "researcher"
    ANALYZER = "analyzer"
    TESTER = "tester"


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageType(Enum):
    """消息类型枚举"""
    TASK = "task"
    RESULT = "result"
    QUERY = "query"
    RESPONSE = "response"
    ERROR = "error"
    STATUS = "status"


# ============ 数据模型 ============

@dataclass
class AgentMessage:
    """
    Agent 消息类

    用于 Agent 之间传递消息和任务。
    """
    sender_id: str
    receiver_id: str
    content: str
    message_type: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """将消息转换为字典"""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class AgentTask:
    """
    Agent 任务类

    表示一个需要 Agent 处理的任务。
    """
    task_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    parent_task_id: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    result: Optional['AgentResult'] = None

    def to_dict(self) -> Dict[str, Any]:
        """将任务转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "parameters": self.parameters,
            "status": self.status.value,
            "parent_task_id": self.parent_task_id,
            "assigned_agent_id": self.assigned_agent_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "result": self.result.to_dict() if self.result else None
        }


@dataclass
class AgentResult:
    """
    Agent 结果类

    表示 Agent 执行任务的结果。
    """
    task_id: str
    agent_id: str
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """将结果转换为字典"""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "artifacts": self.artifacts,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat()
        }


# ============ RAG 服务实例 ============

# 全局 RAG 服务实例
rag_service = RAGPipeline()


# ============ Agent 基类 ============

class AgentBase(ABC):
    """
    Agent 基类

    所有 Agent 的基类，定义了 Agent 的基本接口和行为。
    """

    def __init__(self, agent_id: str, role: AgentRole):
        """
        初始化 Agent。

        Args:
            agent_id: Agent 唯一标识
            role: Agent 角色
        """
        self.agent_id = agent_id
        self.role = role
        self.is_active = True
        self.capabilities: List[str] = []
        self.message_inbox: List[AgentMessage] = []
        self.message_outbox: List[AgentMessage] = []

    def add_capability(self, capability: str):
        """添加 Agent 能力"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)

    def has_capability(self, capability: str) -> bool:
        """检查 Agent 是否具有某能力"""
        return capability in self.capabilities

    async def send_message(self, message: AgentMessage):
        """
        发送消息到消息队列。

        Args:
            message: 要发送的消息
        """
        self.message_outbox.append(message)

    async def receive_message(self, message: AgentMessage):
        """
        接收消息。

        Args:
            message: 接收到的消息
        """
        self.message_inbox.append(message)

    def get_next_message(self) -> Optional[AgentMessage]:
        """获取下一条消息"""
        if self.message_inbox:
            return self.message_inbox.pop(0)
        return None

    @abstractmethod
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """
        执行任务（子类必须实现）。

        Args:
            task: 要执行的任务

        Returns:
            任务执行结果
        """
        pass

    async def process_messages(self):
        """处理消息队列中的消息"""
        while self.message_inbox:
            message = self.message_inbox.pop(0)
            await self.handle_message(message)

    async def handle_message(self, message: AgentMessage):
        """
        处理单条消息（子类可重写）。

        Args:
            message: 要处理的消息
        """
        pass


# ============ Orchestrator Agent ============

class OrchestratorAgent(AgentBase):
    """
    Orchestrator Agent

    负责接收用户指令，分解复杂任务，分配给其他 Agent，并汇总结果。
    """

    def __init__(self):
        """初始化 Orchestrator Agent"""
        super().__init__("orchestrator", AgentRole.ORCHESTRATOR)
        self.add_capability("task_decomposition")
        self.add_capability("task_assignment")
        self.add_capability("result_aggregation")

    async def execute_task(self, task: AgentTask) -> AgentResult:
        """
        执行编排任务。

        Args:
            task: 要执行的编排任务

        Returns:
            编排结果
        """
        # 分解任务
        subtasks = await self.decompose_task(task)

        return AgentResult(
            task_id=task.task_id,
            agent_id=self.agent_id,
            success=True,
            result=f"成功分解任务为 {len(subtasks)} 个子任务",
            artifacts={"subtasks": [t.to_dict() for t in subtasks]}
        )

    async def decompose_task(self, task: AgentTask) -> List[AgentTask]:
        """
        分解复杂任务为子任务。

        Args:
            task: 复杂任务

        Returns:
            子任务列表
        """
        subtasks = []

        # 简单的任务分解逻辑
        if "代码" in task.description or "应用" in task.description:
            # 生成代码相关子任务
            subtasks.append(AgentTask(
                task_id=f"{task.task_id}_sub_1",
                task_type="research",
                description="研究相关技术栈和最佳实践",
                parent_task_id=task.task_id
            ))
            subtasks.append(AgentTask(
                task_id=f"{task.task_id}_sub_2",
                task_type="code_generation",
                description="生成核心代码",
                parent_task_id=task.task_id
            ))
            subtasks.append(AgentTask(
                task_id=f"{task.task_id}_sub_3",
                task_type="code_generation",
                description="生成测试代码",
                parent_task_id=task.task_id
            ))
        elif "研究" in task.description or "调研" in task.description:
            # 研究相关子任务
            subtasks.append(AgentTask(
                task_id=f"{task.task_id}_sub_1",
                task_type="research",
                description="搜索相关资料",
                parent_task_id=task.task_id
            ))
            subtasks.append(AgentTask(
                task_id=f"{task.task_id}_sub_2",
                task_type="analysis",
                description="分析整理信息",
                parent_task_id=task.task_id
            ))
        else:
            # 默认单个任务
            subtasks.append(AgentTask(
                task_id=f"{task.task_id}_sub_1",
                task_type=task.task_type,
                description=task.description,
                parent_task_id=task.task_id
            ))

        return subtasks

    async def assign_tasks(self, subtasks: List[AgentTask], agents: List[AgentBase]) -> Dict[str, AgentBase]:
        """
        将子任务分配给合适的 Agent。

        Args:
            subtasks: 子任务列表
            agents: 可用的 Agent 列表

        Returns:
            任务分配映射
        """
        assignments = {}

        # 按能力分配任务
        for subtask in subtasks:
            assigned = False
            for agent in agents:
                # 根据任务类型匹配 Agent
                if subtask.task_type == "code_generation" and agent.role == AgentRole.CODER:
                    subtask.assigned_agent_id = agent.agent_id
                    assignments[subtask.task_id] = agent
                    assigned = True
                    break
                elif subtask.task_type == "research" and agent.role == AgentRole.RESEARCHER:
                    subtask.assigned_agent_id = agent.agent_id
                    assignments[subtask.task_id] = agent
                    assigned = True
                    break
                elif subtask.task_type == "analysis" and agent.role == AgentRole.ANALYZER:
                    subtask.assigned_agent_id = agent.agent_id
                    assignments[subtask.task_id] = agent
                    assigned = True
                    break

            # 如果没有匹配的 Agent，分配给第一个可用的 Agent
            if not assigned and agents:
                subtask.assigned_agent_id = agents[0].agent_id
                assignments[subtask.task_id] = agents[0]

        return assignments

    async def aggregate_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        汇总多个 Agent 的结果。

        Args:
            results: Agent 执行结果列表

        Returns:
            汇总后的结果
        """
        aggregated = {}
        for result in results:
            aggregated[result.task_id] = result.to_dict()
        return aggregated


# ============ Coder Agent ============

class CoderAgent(AgentBase):
    """
    Coder Agent

    负责生成代码，调用代码执行沙箱，根据执行结果调试优化。
    """

    def __init__(self):
        """初始化 Coder Agent"""
        super().__init__("coder", AgentRole.CODER)
        self.add_capability("code_generation")
        self.add_capability("debugging")
        self.add_capability("code_review")

    async def execute_task(self, task: AgentTask) -> AgentResult:
        """
        执行代码相关任务。

        Args:
            task: 代码任务

        Returns:
            代码执行结果
        """
        if task.task_type == "code_generation":
            return await self.generate_code(task)
        elif task.task_type == "debug":
            return await self.debug_code(task)
        else:
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=f"不支持的任务类型: {task.task_type}"
            )

    async def generate_code(self, task: AgentTask) -> AgentResult:
        """
        生成代码。

        Args:
            task: 代码生成任务

        Returns:
            生成结果
        """
        # 模拟代码生成
        language = task.parameters.get("language", "python")
        code = self._generate_sample_code(language)

        return AgentResult(
            task_id=task.task_id,
            agent_id=self.agent_id,
            success=True,
            result="代码生成成功",
            artifacts={"code": code, "language": language}
        )

    async def debug_code(self, task: AgentTask) -> AgentResult:
        """
        调试代码。

        Args:
            task: 调试任务

        Returns:
            调试结果
        """
        code = task.parameters.get("code", "")
        error = task.parameters.get("error", "")

        # 模拟代码调试
        fixed_code = self._fix_code(code, error)

        return AgentResult(
            task_id=task.task_id,
            agent_id=self.agent_id,
            success=True,
            result="代码调试完成",
            artifacts={"fixed_code": fixed_code, "original_error": error}
        )

    def _generate_sample_code(self, language: str) -> str:
        """生成示例代码"""
        if language == "python":
            return """
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
"""
        elif language == "javascript":
            return """
function helloWorld() {
    console.log("Hello, World!");
}

helloWorld();
"""
        else:
            return "// 代码示例"

    def _fix_code(self, code: str, error: str) -> str:
        """修复代码错误"""
        # 简单的代码修复逻辑
        if "SyntaxError" in error:
            # 添加缺失的冒号
            if "def " in code and ":" not in code.split("\n")[0]:
                return code.replace("def hello()", "def hello():")
        return code


# ============ Researcher Agent ============

class ResearcherAgent(AgentBase):
    """
    Researcher Agent

    负责检索知识库（RAG），总结和整理信息，为其他 Agent 提供知识支持。
    """

    def __init__(self):
        """初始化 Researcher Agent"""
        super().__init__("researcher", AgentRole.RESEARCHER)
        self.add_capability("knowledge_retrieval")
        self.add_capability("summarization")
        self.add_capability("information_analysis")

    async def execute_task(self, task: AgentTask) -> AgentResult:
        """
        执行研究任务。

        Args:
            task: 研究任务

        Returns:
            研究结果
        """
        if task.task_type == "research":
            return await self.search_knowledge(task)
        elif task.task_type == "analysis":
            return await self.analyze_information(task)
        else:
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=f"不支持的任务类型: {task.task_type}"
            )

    async def search_knowledge(self, task: AgentTask) -> AgentResult:
        """
        搜索知识库。

        Args:
            task: 搜索任务

        Returns:
            搜索结果
        """
        try:
            # 调用 RAG 服务查询（在线程池中执行同步调用）
            loop = asyncio.get_event_loop()
            query_result = await loop.run_in_executor(
                None,
                lambda: rag_service.query(task.description, top_k=5)
            )

            if query_result.get("status") == "success":
                documents = query_result.get("documents", [[]])[0]
                return AgentResult(
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    success=True,
                    result=f"找到 {len(documents)} 条相关资料",
                    artifacts={
                        "research_results": documents,
                        "query": task.description
                    }
                )
            else:
                return AgentResult(
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    success=False,
                    error="知识库查询失败"
                )
        except Exception as e:
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=f"知识库查询异常: {str(e)}"
            )

    async def analyze_information(self, task: AgentTask) -> AgentResult:
        """
        分析信息。

        Args:
            task: 分析任务

        Returns:
            分析结果
        """
        # 模拟信息分析
        return AgentResult(
            task_id=task.task_id,
            agent_id=self.agent_id,
            success=True,
            result="信息分析完成",
            artifacts={
                "analysis": "这是分析结果的摘要",
                "key_points": ["要点1", "要点2", "要点3"]
            }
        )

    async def summarize(self, research_results: List[str]) -> str:
        """
        总结研究结果。

        Args:
            research_results: 研究结果列表

        Returns:
            总结文本
        """
        if not research_results:
            return "没有找到相关资料"

        # 简单的总结逻辑
        summary = f"共研究了 {len(research_results)} 份资料。主要发现：\n"
        for i, result in enumerate(research_results, 1):
            summary += f"{i}. {result[:100]}...\n"

        return summary


# ============ Agent 编排器 ============

class AgentOrchestrator:
    """
    Agent 编排器

    负责协调多个 Agent 的工作，管理任务执行和结果汇总。
    """

    def __init__(self, agents: List[AgentBase]):
        """
        初始化编排器。

        Args:
            agents: Agent 列表
        """
        self.agents = agents
        self.task_registry: Dict[str, AgentTask] = {}
        self.message_bus: asyncio.Queue = asyncio.Queue()

    async def register_task(self, task: AgentTask):
        """
        注册任务到任务注册表。

        Args:
            task: 要注册的任务
        """
        self.task_registry[task.task_id] = task

    async def execute_parallel(self, tasks: List[AgentTask]) -> List[AgentResult]:
        """
        并行执行多个任务。

        Args:
            tasks: 任务列表

        Returns:
            执行结果列表
        """
        # 创建并发任务
        coroutines = [self._execute_single_task(task) for task in tasks]

        # 并行执行
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(AgentResult(
                    task_id=tasks[i].task_id,
                    agent_id="unknown",
                    success=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_single_task(self, task: AgentTask) -> AgentResult:
        """
        执行单个任务。

        Args:
            task: 要执行的任务

        Returns:
            执行结果
        """
        # 查找合适的 Agent
        agent = self._find_agent_for_task(task)

        if agent is None:
            return AgentResult(
                task_id=task.task_id,
                agent_id="none",
                success=False,
                error="没有找到合适的 Agent"
            )

        # 更新任务状态
        task.status = TaskStatus.IN_PROGRESS
        task.assigned_agent_id = agent.agent_id

        # 执行任务
        result = await agent.execute_task(task)

        # 更新任务状态
        task.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
        task.result = result

        return result

    def _find_agent_for_task(self, task: AgentTask) -> Optional[AgentBase]:
        """
        查找处理任务的合适 Agent。

        Args:
            task: 要处理的任务

        Returns:
            合适的 Agent 或 None
        """
        # 如果任务已分配，直接返回对应的 Agent
        if task.assigned_agent_id:
            for agent in self.agents:
                if agent.agent_id == task.assigned_agent_id:
                    return agent

        # 根据任务类型匹配 Agent
        for agent in self.agents:
            if task.task_type == "code_generation" and agent.role == AgentRole.CODER:
                return agent
            elif task.task_type == "research" and agent.role == AgentRole.RESEARCHER:
                return agent
            elif task.task_type == "analysis" and agent.role == AgentRole.ANALYZER:
                return agent

        # 返回第一个可用的 Agent
        return self.agents[0] if self.agents else None

    async def aggregate_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        汇总多个结果。

        Args:
            results: 结果列表

        Returns:
            汇总结果
        """
        aggregated = {}
        for result in results:
            aggregated[result.task_id] = result.to_dict()
        return aggregated


# ============ 多 Agent 服务 ============

class MultiAgentService:
    """
    多 Agent 服务

    提供多 Agent 协作的高层接口，管理任务生命周期。
    """

    def __init__(self):
        """初始化多 Agent 服务"""
        # 创建 Agent 实例
        self.coder_agent = CoderAgent()
        self.researcher_agent = ResearcherAgent()
        self.orchestrator_agent = OrchestratorAgent()

        # 创建编排器
        self.orchestrator = AgentOrchestrator([
            self.coder_agent,
            self.researcher_agent,
            self.orchestrator_agent
        ])

        # 任务存储
        self.active_tasks: Dict[str, Dict[str, Any]] = {}

    async def create_task(self, user_message: str) -> str:
        """
        创建新任务。

        Args:
            user_message: 用户消息

        Returns:
            任务 ID
        """
        task_id = str(uuid4())

        # 创建任务记录
        self.active_tasks[task_id] = {
            "task_id": task_id,
            "message": user_message,
            "status": TaskStatus.PENDING,
            "created_at": datetime.now().isoformat()
        }

        return task_id

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态。

        Args:
            task_id: 任务 ID

        Returns:
            任务状态信息
        """
        return self.active_tasks.get(task_id)

    async def chat(self, user_message: str) -> Dict[str, Any]:
        """
        处理用户聊天消息。

        Args:
            user_message: 用户消息

        Returns:
            聊天响应
        """
        # 创建任务
        task_id = await self.create_task(user_message)

        # 创建主任务
        main_task = AgentTask(
            task_id=task_id,
            task_type="user_request",
            description=user_message
        )

        # 注册任务
        await self.orchestrator.register_task(main_task)

        # 更新任务状态
        self.active_tasks[task_id]["status"] = TaskStatus.IN_PROGRESS

        # Orchestrator 分解任务
        orchestrator_result = await self.orchestrator_agent.execute_task(main_task)

        if orchestrator_result.success:
            # 获取子任务
            subtasks_data = orchestrator_result.artifacts.get("subtasks", [])
            subtasks = [
                AgentTask(
                    task_id=subtask["task_id"],
                    task_type=subtask["task_type"],
                    description=subtask["description"],
                    parent_task_id=subtask.get("parent_task_id")
                )
                for subtask in subtasks_data
            ]

            # 分配任务
            assignments = await self.orchestrator_agent.assign_tasks(
                subtasks,
                [self.coder_agent, self.researcher_agent]
            )

            # 并行执行任务
            results = await self.orchestrator.execute_parallel(subtasks)

            # 汇总结果
            final_result = await self.orchestrator.aggregate_results(results)

            # 更新任务状态
            self.active_tasks[task_id]["status"] = TaskStatus.COMPLETED
            self.active_tasks[task_id]["result"] = final_result

            return {
                "task_id": task_id,
                "response": "任务处理完成",
                "result": final_result
            }
        else:
            # 更新任务状态
            self.active_tasks[task_id]["status"] = TaskStatus.FAILED
            self.active_tasks[task_id]["error"] = orchestrator_result.error

            return {
                "task_id": task_id,
                "response": "任务处理失败",
                "error": orchestrator_result.error
            }


# ============ 全局服务实例 ============

# 全局多 Agent 服务实例
multi_agent_service = MultiAgentService()
