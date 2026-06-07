"""
LangGraph Supervisor 图模块

使用 LangGraph 构建 Supervisor 图，协调多个 Worker Agent 协作完成任务。
禁用代理以确保无论用户是否启用代理都能正常运行。
"""
import os
from typing import Optional, Dict, Any, List
import httpx
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated

from backend.config import AppConfig


def _create_sync_client():
    """创建禁用代理的同步 HTTP 客户端。"""
    return httpx.Client(proxies=None, timeout=30.0, follow_redirects=True)


def _create_async_client():
    """创建禁用代理的异步 HTTP 客户端。"""
    return httpx.AsyncClient(proxies=None, timeout=30.0, follow_redirects=True)


# ============ 状态定义 ============

class AgentState(TypedDict):
    """Agent 状态。"""
    messages: Annotated[list, add_messages]
    next_worker: str
    task_type: str
    result: str
    worker_results: Dict[str, str]


# ============ Worker Agent ============

class WorkerAgent:
    """Worker Agent 基类。"""

    def __init__(self, name: str, role: str, description: str):
        self.name = name
        self.role = role
        self.description = description
        self.llm = self._create_llm()

    def _create_llm(self) -> ChatOpenAI:
        """创建 LLM（禁用代理）。"""
        config = AppConfig()
        return ChatOpenAI(
            model_name=config.openai_model,
            openai_api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            temperature=0.7,
            max_tokens=2000,
            http_client=_create_sync_client(),
            http_async_client=_create_async_client(),
        )

    async def execute(self, task: str, context: Dict[str, Any] = None) -> str:
        """执行任务。"""
        try:
            messages = [
                HumanMessage(content=f"你是一个 {self.role}。{self.description}\n\n请完成以下任务：\n{task}")
            ]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            return f"Worker {self.name} 执行失败: {str(e)}"


class CoderAgent(WorkerAgent):
    """代码生成 Agent。"""

    def __init__(self):
        super().__init__(
            name="coder",
            role="代码工程师",
            description="你是一个专业的代码工程师，擅长编写、分析和优化代码。"
        )


class ResearcherAgent(WorkerAgent):
    """研究员 Agent。"""

    def __init__(self):
        super().__init__(
            name="researcher",
            role="研究员",
            description="你是一个专业的研究员，擅长信息检索、分析和总结。"
        )


class TesterAgent(WorkerAgent):
    """测试员 Agent。"""

    def __init__(self):
        super().__init__(
            name="tester",
            role="测试工程师",
            description="你是一个专业的测试工程师，擅长编写测试用例和代码审查。"
        )


# ============ Supervisor 图 ============

class SupervisorGraph:
    """Supervisor 图，协调多个 Worker Agent。"""

    def __init__(self):
        self.config = AppConfig()
        self.llm = self._create_llm()
        self.workers = self._create_workers()
        self.graph = self._build_graph()

    def _create_llm(self) -> ChatOpenAI:
        """创建 Supervisor LLM。"""
        return ChatOpenAI(
            model_name=self.config.openai_model,
            openai_api_key=self.config.openai_api_key,
            openai_api_base=self.config.openai_base_url,
            temperature=0.3,
            max_tokens=500,
        )

    def _create_workers(self) -> Dict[str, WorkerAgent]:
        """创建 Worker Agent。"""
        workers = {
            "coder": CoderAgent(),
            "researcher": ResearcherAgent(),
            "tester": TesterAgent(),
        }
        return workers

    def _build_graph(self):
        """构建 LangGraph 图。"""
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("supervisor", self._supervisor_node)
        for name, worker in self.workers.items():
            workflow.add_node(name, self._create_worker_node(worker))

        # 添加边
        workflow.set_entry_point("supervisor")

        # Supervisor 到 Worker 的边
        for name in self.workers:
            workflow.add_edge(name, "supervisor")

        # Supervisor 到 END 的边
        workflow.add_conditional_edges(
            "supervisor",
            self._route_to_worker,
            {name: name for name in self.workers} | {"end": END}
        )

        return workflow.compile()

    def _supervisor_node(self, state: AgentState) -> AgentState:
        """Supervisor 节点，决定调用哪个 Worker。"""
        messages = state.get("messages", [])
        if not messages:
            return {"next_worker": "end", "result": "没有消息"}

        last_message = messages[-1].content if messages else ""

        # 使用 LLM 决定调用哪个 Worker
        try:
            response = self.llm.invoke([
                HumanMessage(content=f"分析以下任务，决定应该调用哪个 Worker Agent。可选: coder(写代码), researcher(研究分析), tester(测试审查), end(结束)。\n\n任务: {last_message}\n\n只返回 worker 名称。")
            ])
            worker_name = response.content.strip().lower()

            if worker_name in self.workers:
                return {"next_worker": worker_name}
            else:
                return {"next_worker": "end"}
        except Exception:
            return {"next_worker": "end"}

    def _create_worker_node(self, worker: WorkerAgent):
        """创建 Worker 节点。"""
        async def worker_node(state: AgentState) -> AgentState:
            messages = state.get("messages", [])
            last_message = messages[-1].content if messages else ""

            result = await worker.execute(last_message)

            return {
                "messages": [AIMessage(content=result)],
                "worker_results": {worker.name: result}
            }

        return worker_node

    def _route_to_worker(self, state: AgentState) -> str:
        """路由到 Worker。"""
        return state.get("next_worker", "end")

    async def process_message(self, message: str, conversation_id: str = None) -> dict:
        """处理用户消息。"""
        try:
            # 初始化状态
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "next_worker": "",
                "task_type": "",
                "result": "",
                "worker_results": {}
            }

            # 运行图
            result = await self.graph.ainvoke(initial_state)

            # 提取结果
            final_messages = result.get("messages", [])
            final_response = final_messages[-1].content if final_messages else ""

            return {
                "response": final_response,
                "agent_thoughts": f"Supervisor 协调 Worker Agent 完成任务: '{message}'",
                "conversation_id": conversation_id or "default",
                "worker_results": result.get("worker_results", {})
            }

        except Exception as e:
            # 降级
            print(f"Supervisor 图执行失败: {e}")
            return {
                "response": f"收到你的消息：{message}。我正在处理中...",
                "agent_thoughts": f"Supervisor 图执行失败: {str(e)}",
                "conversation_id": conversation_id or "default"
            }
