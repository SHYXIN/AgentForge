"""
AgentForge - FastAPI Backend

This is the main application module.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import (
    register_user, login_user, upload_document, list_documents, chat
)
from backend.models import (
    UserCreate, LoginRequest, ChatRequest
)
from backend.middleware.error_handler import add_error_handler_middleware
from backend.services.monitoring import setup_logging, get_logger, get_metrics

# 配置日志
setup_logging()
logger = get_logger(__name__)

# Version constant - single source of truth
VERSION = "0.1.0"

app = FastAPI(
    title="AgentForge",
    description="AI Agent 开发展示项目",
    version=VERSION
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加错误处理中间件
add_error_handler_middleware(app)


# ============ 启动事件 ============

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据。"""
    from backend.config import config as app_config

    # 仅在开发环境且使用内存存储时自动 seed
    if app_config.debug and app_config.repo_backend == "memory":
        logger.info("开发环境，使用内存存储，开始初始化 seed 数据...")
        try:
            from backend.seed.run import run_seed
            await run_seed(env="development", clean=True)
            logger.info("Seed 数据初始化完成")
        except Exception as e:
            logger.error(f"Seed 数据初始化失败: {e}")


# ============ 辅助函数 ============

async def handle_websocket_message(websocket: WebSocket, data: dict) -> dict:
    """处理 WebSocket 消息并生成响应。"""
    # 检查是否是聊天消息
    if data.get("type") == "chat":
        message = data.get("message", "")
        conversation_id = data.get("conversation_id")

        # 通过 Agent 处理消息
        request = ChatRequest(message=message, conversation_id=conversation_id)
        result = await chat(request)

        return {
            "type": "chat_response",
            "response": result.response,
            "agent_thoughts": result.agent_thoughts,
            "conversation_id": result.conversation_id
        }

    # 默认回显
    return {
        "type": "echo",
        "original": data
    }


# ============ API 端点 ============

@app.get("/health")
async def health_check():
    """健康检查端点。"""
    return {
        "status": "ok",
        "version": VERSION
    }


@app.get("/metrics")
async def metrics():
    """Prometheus 指标端点。"""
    from fastapi.responses import Response
    return Response(
        content=get_metrics(),
        media_type="text/plain"
    )


@app.post("/api/auth/register", status_code=201)
async def api_register_user(user: UserCreate):
    """用户注册。"""
    logger.info(f"用户注册: {user.username}")
    return await register_user(user)


@app.post("/api/auth/login")
async def api_login_user(request: LoginRequest):
    """用户登录。"""
    logger.info(f"用户登录: {request.username}")
    return await login_user(request)


@app.post("/api/documents", status_code=201)
async def api_upload_document(file: UploadFile = File(...)):
    """上传文档。"""
    logger.info(f"文档上传: {file.filename}")
    return await upload_document(file)


@app.get("/api/documents")
async def api_list_documents():
    """获取文档列表。"""
    return await list_documents()


@app.post("/api/chat")
async def api_chat(request: ChatRequest):
    """Agent 聊天端点。"""
    logger.info(f"聊天请求: {request.message[:50]}...")
    return await chat(request)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点，用于实时通信。"""
    await websocket.accept()

    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()

            # 处理消息
            response = await handle_websocket_message(websocket, data)

            # 发送响应
            await websocket.send_json(response)
    except WebSocketDisconnect:
        # 处理断开连接
        pass


# ============ RAG API 端点 ============

from backend.api.routes import (
    upload_rag_document, list_rag_documents, query_rag, delete_rag_document
)
from backend.models import RAGQueryRequest


@app.post("/api/rag/documents", status_code=201)
async def api_upload_rag_document(file: UploadFile = File(...)):
    """上传文档到知识库。"""
    logger.info(f"知识库文档上传: {file.filename}")
    return await upload_rag_document(file)


@app.get("/api/rag/documents")
async def api_list_rag_documents():
    """获取知识库文档列表。"""
    return await list_rag_documents()


@app.post("/api/rag/query")
async def api_query_rag(request: RAGQueryRequest):
    """查询知识库。"""
    logger.info(f"知识库查询: {request.query[:50]}...")
    return await query_rag(request)


@app.delete("/api/rag/documents/{document_id}")
async def api_delete_rag_document(document_id: str):
    """删除知识库文档。"""
    logger.info(f"知识库文档删除: {document_id}")
    return await delete_rag_document(document_id)


# ============ 多 Agent 协作 API 端点 ============

from backend.api.multi_agent_routes import multi_agent_chat, get_task_status
from backend.models import MultiAgentChatRequest


@app.post("/api/multi-agent/chat")
async def api_multi_agent_chat(request: MultiAgentChatRequest):
    """多 Agent 聊天端点。"""
    logger.info(f"多 Agent 聊天请求: {request.message[:50]}...")
    return await multi_agent_chat(request)


@app.get("/api/multi-agent/status/{task_id}")
async def api_get_task_status(task_id: str):
    """查询任务状态端点。"""
    logger.info(f"查询任务状态: {task_id}")
    return await get_task_status(task_id)


# ============ 代码执行 API 端点 ============

from backend.services.code_executor import CodeExecutor
from pydantic import BaseModel
from typing import Optional, Dict


class CodeExecutionRequest(BaseModel):
    """代码执行请求模型"""
    code: str
    env: Optional[Dict[str, str]] = None
    workdir: Optional[str] = "/workspace"


class CodeExecutionResponse(BaseModel):
    """代码执行响应模型"""
    stdout: str
    stderr: str
    exit_code: int


# 创建全局代码执行器实例
code_executor = CodeExecutor(timeout=30, memory_limit="512m", cpu_limit=0.5)


@app.post("/api/execute", response_model=CodeExecutionResponse)
async def api_execute_code(request: CodeExecutionRequest):
    """
    代码执行端点

    在 Docker 沙箱中安全执行 Python 代码，支持：
    - 30 秒超时限制
    - 512MB 内存限制
    - 网络隔离
    - 文件系统隔离
    - 危险代码过滤
    """
    logger.info(f"代码执行请求: {request.code[:50]}...")

    result = code_executor.execute(
        code=request.code,
        env=request.env,
        workdir=request.workdir
    )

    return CodeExecutionResponse(**result)
