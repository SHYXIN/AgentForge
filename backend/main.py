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

# 导入对话路由
from backend.api.conversation_routes import router as conversation_router
from backend.api.agent_routes import router as agent_router

# 注册路由
app.include_router(conversation_router)
app.include_router(agent_router)


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
        "status": "healthy",
        "version": VERSION,
        "service": "AgentForge"
    }


@app.get("/")
async def root():
    """根端点。"""
    return {
        "message": "Welcome to AgentForge API",
        "version": VERSION,
        "docs": "/docs"
    }


@app.post("/auth/register")
async def register(user: UserCreate):
    """用户注册。"""
    return await register_user(user)


@app.post("/auth/login")
async def login(request: LoginRequest):
    """用户登录。"""
    return await login_user(request)


@app.post("/api/documents/upload")
async def upload(file: UploadFile = File(...)):
    """上传文档。"""
    return await upload_document(file)


@app.get("/api/documents")
async def list_docs():
    """获取文档列表。"""
    return await list_documents()


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """聊天端点。"""
    return await chat(request)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点。"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            response = await handle_websocket_message(websocket, data)
            await websocket.send_json(response)
    except WebSocketDisconnect:
        logger.info("WebSocket 连接断开")
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
