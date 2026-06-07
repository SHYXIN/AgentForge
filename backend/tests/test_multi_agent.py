"""
多 Agent 协作架构测试模块

测试 AgentForge 的多 Agent 协作功能。
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

# 导入待实现的模块
from backend.services.multi_agent import (
    AgentRole,
    AgentMessage,
    AgentTask,
    AgentResult,
    AgentBase,
    OrchestratorAgent,
    CoderAgent,
    ResearcherAgent,
    AgentOrchestrator,
    TaskStatus,
    MultiAgentService
)


class TestAgentMessage:
    """测试 Agent 消息类"""

    def test_create_agent_message(self):
        """测试创建 Agent 消息"""
        # Arrange & Act
        message = AgentMessage(
            sender_id="agent_1",
            receiver_id="agent_2",
            content="测试消息",
            message_type="task"
        )

        # Assert
        assert message.sender_id == "agent_1"
        assert message.receiver_id == "agent_2"
        assert message.content == "测试消息"
        assert message.message_type == "task"
        assert message.message_id is not None
        assert message.timestamp is not None

    def test_message_to_dict(self):
        """测试消息转换为字典"""
        # Arrange
        message = AgentMessage(
            sender_id="agent_1",
            receiver_id="agent_2",
            content="测试内容",
            message_type="result"
        )

        # Act
        message_dict = message.to_dict()

        # Assert
        assert isinstance(message_dict, dict)
        assert message_dict["sender_id"] == "agent_1"
        assert message_dict["receiver_id"] == "agent_2"
        assert message_dict["content"] == "测试内容"
        assert message_dict["message_type"] == "result"


class TestAgentTask:
    """测试 Agent 任务类"""

    def test_create_agent_task(self):
        """测试创建 Agent 任务"""
        # Arrange & Act
        task = AgentTask(
            task_id="task_1",
            task_type="code_generation",
            description="生成一个 Python 函数",
            parameters={"language": "python", "function_name": "hello_world"}
        )

        # Assert
        assert task.task_id == "task_1"
        assert task.task_type == "code_generation"
        assert task.description == "生成一个 Python 函数"
        assert task.parameters["language"] == "python"
        assert task.status == TaskStatus.PENDING

    def test_task_status_update(self):
        """测试任务状态更新"""
        # Arrange
        task = AgentTask(
            task_id="task_1",
            task_type="research",
            description="研究一个主题"
        )

        # Act
        task.status = TaskStatus.IN_PROGRESS

        # Assert
        assert task.status == TaskStatus.IN_PROGRESS


class TestAgentResult:
    """测试 Agent 结果类"""

    def test_create_agent_result(self):
        """测试创建 Agent 结果"""
        # Arrange & Act
        result = AgentResult(
            task_id="task_1",
            agent_id="coder_agent",
            success=True,
            result="代码生成成功",
            artifacts={"code": "def hello(): print('Hello World')"}
        )

        # Assert
        assert result.task_id == "task_1"
        assert result.agent_id == "coder_agent"
        assert result.success is True
        assert result.result == "代码生成成功"
        assert result.artifacts["code"] is not None

    def test_failed_result(self):
        """测试失败的结果"""
        # Arrange & Act
        result = AgentResult(
            task_id="task_1",
            agent_id="coder_agent",
            success=False,
            error="代码执行出错"
        )

        # Assert
        assert result.success is False
        assert result.error == "代码执行出错"


class TestAgentBase:
    """测试 Agent 基类"""

    @pytest.fixture
    def mock_agent(self):
        """创建 Mock Agent"""

        class TestAgent(AgentBase):
            def __init__(self):
                super().__init__("test_agent", AgentRole.CODER)

            async def execute_task(self, task: AgentTask) -> AgentResult:
                return AgentResult(
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    success=True,
                    result="任务执行成功"
                )

        return TestAgent()

    def test_agent_initialization(self, mock_agent):
        """测试 Agent 初始化"""
        # Assert
        assert mock_agent.agent_id == "test_agent"
        assert mock_agent.role == AgentRole.CODER
        assert mock_agent.is_active is True

    def test_agent_capabilities(self, mock_agent):
        """测试 Agent 能力列表"""
        # Arrange
        mock_agent.add_capability("code_generation")
        mock_agent.add_capability("debugging")

        # Assert
        assert "code_generation" in mock_agent.capabilities
        assert "debugging" in mock_agent.capabilities

    @pytest.mark.asyncio
    async def test_agent_send_message(self, mock_agent):
        """测试 Agent 发送消息"""
        # Arrange
        message = AgentMessage(
            sender_id="test_agent",
            receiver_id="other_agent",
            content="协作请求",
            message_type="task"
        )

        # Act
        await mock_agent.send_message(message)

        # Assert
        assert len(mock_agent.message_outbox) == 1
        assert mock_agent.message_outbox[0].content == "协作请求"

    @pytest.mark.asyncio
    async def test_agent_receive_message(self, mock_agent):
        """测试 Agent 接收消息"""
        # Arrange
        message = AgentMessage(
            sender_id="other_agent",
            receiver_id="test_agent",
            content="处理请求",
            message_type="task"
        )

        # Act
        await mock_agent.receive_message(message)

        # Assert
        assert len(mock_agent.message_inbox) == 1
        assert mock_agent.message_inbox[0].content == "处理请求"

    @pytest.mark.asyncio
    async def test_agent_execute_task(self, mock_agent):
        """测试 Agent 执行任务"""
        # Arrange
        task = AgentTask(
            task_id="task_1",
            task_type="test",
            description="测试任务"
        )

        # Act
        result = await mock_agent.execute_task(task)

        # Assert
        assert result.success is True
        assert result.task_id == "task_1"


class TestOrchestratorAgent:
    """测试 Orchestrator Agent"""

    @pytest.fixture
    def orchestrator(self):
        """创建 Orchestrator Agent"""
        return OrchestratorAgent()

    def test_orchestrator_initialization(self, orchestrator):
        """测试 Orchestrator 初始化"""
        # Assert
        assert orchestrator.role == AgentRole.ORCHESTRATOR
        assert orchestrator.agent_id == "orchestrator"

    @pytest.mark.asyncio
    async def test_orchestrator_decompose_task(self, orchestrator):
        """测试 Orchestrator 分解任务"""
        # Arrange
        complex_task = AgentTask(
            task_id="complex_task_1",
            task_type="complex",
            description="生成一个完整的 Web 应用，包含前后端代码和数据库设计"
        )

        # Act
        subtasks = await orchestrator.decompose_task(complex_task)

        # Assert
        assert len(subtasks) > 1
        for subtask in subtasks:
            assert subtask.parent_task_id == complex_task.task_id

    @pytest.mark.asyncio
    async def test_orchestrator_assign_tasks(self, orchestrator):
        """测试 Orchestrator 分配任务"""
        # Arrange
        subtasks = [
            AgentTask(task_id="subtask_1", task_type="code_generation", description="生成后端代码"),
            AgentTask(task_id="subtask_2", task_type="research", description="研究最佳实践"),
            AgentTask(task_id="subtask_3", task_type="code_generation", description="生成前端代码")
        ]

        agents = [
            CoderAgent(),
            ResearcherAgent(),
            CoderAgent()
        ]

        # Act
        assignments = await orchestrator.assign_tasks(subtasks, agents)

        # Assert
        assert len(assignments) == 3
        for task_id, agent in assignments.items():
            assert task_id in [task.task_id for task in subtasks]


class TestCoderAgent:
    """测试 Coder Agent"""

    @pytest.fixture
    def coder_agent(self):
        """创建 Coder Agent"""
        return CoderAgent()

    def test_coder_initialization(self, coder_agent):
        """测试 Coder Agent 初始化"""
        # Assert
        assert coder_agent.role == AgentRole.CODER
        assert coder_agent.agent_id == "coder"

    @pytest.mark.asyncio
    async def test_coder_generate_code(self, coder_agent):
        """测试 Coder 生成代码"""
        # Arrange
        task = AgentTask(
            task_id="code_task_1",
            task_type="code_generation",
            description="生成一个 hello world 函数",
            parameters={"language": "python"}
        )

        # Act
        result = await coder_agent.execute_task(task)

        # Assert
        assert result.success is True
        assert result.artifacts.get("code") is not None

    @pytest.mark.asyncio
    async def test_coder_debug_code(self, coder_agent):
        """测试 Coder 调试代码"""
        # Arrange
        task = AgentTask(
            task_id="debug_task_1",
            task_type="debug",
            description="调试代码错误",
            parameters={
                "code": "def hello()\n    print('hello')",
                "error": "SyntaxError: invalid syntax"
            }
        )

        # Act
        result = await coder_agent.execute_task(task)

        # Assert
        assert result.success is True
        assert "fixed_code" in result.artifacts


class TestResearcherAgent:
    """测试 Researcher Agent"""

    @pytest.fixture
    def researcher_agent(self):
        """创建 Researcher Agent"""
        return ResearcherAgent()

    def test_researcher_initialization(self, researcher_agent):
        """测试 Researcher Agent 初始化"""
        # Assert
        assert researcher_agent.role == AgentRole.RESEARCHER
        assert researcher_agent.agent_id == "researcher"

    @pytest.mark.asyncio
    async def test_researcher_search_knowledge(self, researcher_agent):
        """测试 Researcher 搜索知识库"""
        # Arrange
        task = AgentTask(
            task_id="research_task_1",
            task_type="research",
            description="研究 Python 最佳实践"
        )

        # Mock RAG 服务的 query 方法
        with patch('backend.services.multi_agent.rag_service.query') as mock_query:
            mock_query.return_value = {
                'status': 'success',
                'documents': [['Python 最佳实践包括...', '代码规范...']],
                'distances': [[0.95, 0.92]]
            }

            # Act
            result = await researcher_agent.execute_task(task)

        # Assert
        assert result.success is True
        assert result.artifacts.get("research_results") is not None

    @pytest.mark.asyncio
    async def test_researcher_summarize(self, researcher_agent):
        """测试 Researcher 总结信息"""
        # Arrange
        research_results = [
            "结果1：Python 最佳实践",
            "结果2：代码规范指南",
            "结果3：性能优化技巧"
        ]

        # Act
        summary = await researcher_agent.summarize(research_results)

        # Assert
        assert summary is not None
        assert len(summary) > 0


class TestAgentOrchestrator:
    """测试 Agent 编排器"""

    @pytest.fixture
    def orchestrator(self):
        """创建 Agent 编排器"""
        agents = [
            CoderAgent(),
            ResearcherAgent()
        ]
        return AgentOrchestrator(agents)

    def test_orchestrator_initialization(self, orchestrator):
        """测试编排器初始化"""
        # Assert
        assert len(orchestrator.agents) == 2
        assert orchestrator.task_registry is not None

    @pytest.mark.asyncio
    async def test_orchestrator_register_task(self, orchestrator):
        """测试编排器注册任务"""
        # Arrange
        task = AgentTask(
            task_id="registered_task_1",
            task_type="research",
            description="测试注册任务"
        )

        # Act
        await orchestrator.register_task(task)

        # Assert
        assert task.task_id in orchestrator.task_registry

    @pytest.mark.asyncio
    async def test_orchestrator_execute_parallel_tasks(self, orchestrator):
        """测试编排器并行执行任务"""
        # Arrange
        tasks = [
            AgentTask(task_id="parallel_1", task_type="research", description="任务1"),
            AgentTask(task_id="parallel_2", task_type="research", description="任务2")
        ]

        # Act
        results = await orchestrator.execute_parallel(tasks)

        # Assert
        assert len(results) == 2
        for result in results:
            assert result.success is True

    @pytest.mark.asyncio
    async def test_orchestrator_collect_results(self, orchestrator):
        """测试编排器收集结果"""
        # Arrange
        results = [
            AgentResult(task_id="task_1", agent_id="coder", success=True, result="结果1"),
            AgentResult(task_id="task_2", agent_id="researcher", success=True, result="结果2")
        ]

        # Act
        final_result = await orchestrator.aggregate_results(results)

        # Assert
        assert final_result is not None
        assert "task_1" in final_result
        assert "task_2" in final_result


class TestMultiAgentService:
    """测试多 Agent 服务"""

    @pytest.fixture
    def service(self):
        """创建多 Agent 服务"""
        return MultiAgentService()

    def test_service_initialization(self, service):
        """测试服务初始化"""
        # Assert
        assert service.orchestrator is not None
        assert service.active_tasks is not None

    @pytest.mark.asyncio
    async def test_service_create_task(self, service):
        """测试服务创建任务"""
        # Arrange
        user_message = "帮我生成一个计算器应用"

        # Act
        task_id = await service.create_task(user_message)

        # Assert
        assert task_id is not None
        assert task_id in service.active_tasks

    @pytest.mark.asyncio
    async def test_service_get_task_status(self, service):
        """测试服务获取任务状态"""
        # Arrange
        task_id = str(uuid4())
        service.active_tasks[task_id] = {
            "status": TaskStatus.IN_PROGRESS,
            "message": "测试任务"
        }

        # Act
        status = await service.get_task_status(task_id)

        # Assert
        assert status is not None
        assert status["status"] == TaskStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_service_chat(self, service):
        """测试服务聊天功能"""
        # Arrange
        user_message = "请帮我研究 Python 异步编程"

        # Act
        response = await service.chat(user_message)

        # Assert
        assert response is not None
        assert "task_id" in response
        assert "response" in response


class TestMultiAgentAPI:
    """测试多 Agent API 端点"""

    @pytest.mark.asyncio
    async def test_multi_agent_chat_endpoint(self):
        """测试多 Agent 聊天端点"""
        # Arrange
        from backend.api.multi_agent_routes import multi_agent_chat
        from backend.models import MultiAgentChatRequest

        request = MultiAgentChatRequest(message="测试消息")

        # Act
        response = await multi_agent_chat(request)

        # Assert
        assert response is not None
        assert response.task_id is not None
        assert response.response is not None

    @pytest.mark.asyncio
    async def test_get_task_status_endpoint(self):
        """测试获取任务状态端点"""
        # Arrange
        from backend.api.multi_agent_routes import get_task_status
        from backend.services.multi_agent import multi_agent_service

        # 先创建一个任务
        task_id = await multi_agent_service.create_task("测试任务")

        # Act
        response = await get_task_status(task_id)

        # Assert
        assert response is not None
        assert response.task_id == task_id
        assert response.status is not None

    @pytest.mark.asyncio
    async def test_get_nonexistent_task_status(self):
        """测试获取不存在的任务状态"""
        # Arrange
        from backend.api.multi_agent_routes import get_task_status
        from fastapi import HTTPException

        task_id = "nonexistent_task_id"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_task_status(task_id)

        assert exc_info.value.status_code == 404
