# AgentForge

AI Agent 开发展示项目 - 多 Agent 协作 + RAG + 代码执行

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 项目简介

AgentForge 是一个用于展示 AI Agent 开发能力的项目，包含多 Agent 协作、RAG 知识检索、代码执行沙箱等核心功能。

**仓库地址**: https://github.com/SHYXIN/AgentForge

## 功能特性

### 后端功能
- **FastAPI 模块化架构** - api、models、services 分层
- **用户认证** - 注册、登录、Token 管理
- **Agent 聊天** - 单 Agent 对话、多轮交互
- **RAG 知识检索** - 文档上传、智能分块、向量化、检索
- **代码执行沙箱** - Docker 隔离、资源限制、安全机制
- **多 Agent 协作** - Orchestrator + Coder + Researcher
- **WebSocket 实时通信** - 流式输出、实时交互
- **错误处理** - 全局异常捕获、统一错误响应
- **监控** - Prometheus 指标、结构化日志

### 前端功能
- **React + TypeScript + Vite** - 现代前端栈
- **对话界面** - 消息列表、流式输出、思考过程展示
- **文档管理** - 拖拽上传、文档列表、知识库管理
- **用户认证** - 登录、注册、Token 管理
- **WebSocket 服务** - 实时通信、自动重连

## 技术栈

### 后端
- Python 3.10
- FastAPI
- SQLAlchemy 2.0（异步）
- Pydantic V2
- Chroma（向量数据库）
- Redis（缓存）
- PostgreSQL（关系数据库）
- Sentence Transformers（Embedding）
- Docker SDK
- Prometheus Client

### 前端
- React 18
- TypeScript
- Vite
- WebSocket API

## 项目结构

```
AgentForge/
├── backend/                    # 后端代码
│   ├── api/                    # API 路由
│   │   └── routes.py
│   │   └── multi_agent_routes.py
│   ├── models/                 # 数据模型
│   │   └── __init__.py
│   ├── services/               # 业务逻辑
│   │   ├── agent.py
│   │   ├── rag.py
│   │   ├── code_executor.py
│   │   ├── multi_agent.py
│   │   └── monitoring.py
│   ├── middleware/              # 中间件
│   │   └── error_handler.py
│   ├── tests/                  # 测试套件
│   │   ├── test_health.py
│   │   ├── test_websocket.py
│   │   ├── test_database.py
│   │   ├── test_api.py
│   │   ├── test_agent.py
│   │   ├── test_rag.py
│   │   ├── test_code_executor.py
│   │   ├── test_multi_agent.py
│   │   └── test_error_handler.py
│   ├── main.py                 # FastAPI 应用入口
│   └── requirements.txt        # Python 依赖
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── components/         # 组件
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── DocumentManager.tsx
│   │   │   └── AuthInterface.tsx
│   │   ├── hooks/              # 自定义 Hooks
│   │   │   └── useWebSocket.tsx
│   │   ├── services/           # API 服务
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── docker/
│   └── docker-compose.yml      # Docker 编排
├── docs/
│   └── agents/                 # Agent 配置文档
└── README.md                   # 本文件
```

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- Docker（可选，用于代码执行沙箱）

### 后端启动

```bash
# 1. 创建虚拟环境
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务（从项目根目录运行）
cd ..
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 启动开发服务器
npm run dev
```

### Docker 启动

```bash
# 启动所有依赖服务
docker-compose up -d
```

## API 文档

启动后端后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Prometheus Metrics: http://localhost:8000/metrics

## 核心 API

### 用户认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

### Agent 聊天
- `POST /api/chat` - 单 Agent 聊天
- `POST /api/multi-agent/chat` - 多 Agent 聊天

### RAG 知识库
- `POST /api/rag/documents` - 上传文档
- `GET /api/rag/documents` - 文档列表
- `POST /api/rag/query` - 知识库查询
- `DELETE /api/rag/documents/{id}` - 删除文档

### 代码执行
- `POST /api/execute` - 执行 Python 代码

### WebSocket
- `ws://localhost:8000/ws` - 实时通信

## 测试

### 后端测试

```bash
cd backend

# 使用内存存储运行测试（推荐）
REPO_BACKEND=memory python -m pytest tests/ -v

# 使用 MySQL 存储运行测试（需要 MySQL 服务）
REPO_BACKEND=mysql python -m pytest tests/ -v

# 运行覆盖率报告
python -m pytest tests/ --cov=. --cov-report=html

# 运行指定测试文件
python -m pytest tests/test_agent_api.py -v
python -m pytest tests/test_conversation_api.py -v
```

### 前端测试

```bash
cd frontend

# 运行所有测试
npm test -- --run

# 运行测试并监视文件变化
npm test
```

### 测试覆盖

- **后端**: 174 个测试，100% 通过率
- **前端**: 21 个测试，100% 通过率
- **总计**: 195 个测试

### 存储后端切换

项目支持两种存储后端，通过环境变量 `REPO_BACKEND` 切换：

- `memory` - 内存存储（用于开发和测试）
- `mysql` - MySQL 存储（用于生产环境）

切换存储后端后，所有数据操作会自动使用对应的 Repository 实现。

## 环境变量

创建 `.env` 文件：

```env
# 数据库
DB_POSTGRES_HOST=localhost
DB_POSTGRES_PORT=5432
DB_POSTGRES_USER=postgres
DB_POSTGRES_PASSWORD=postgres
DB_POSTGRES_DB=agentforge

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Chroma
CHROMA_HOST=localhost
CHROMA_PORT=8001

# MiMo API
MI_MO_API_KEY=your_api_key_here
```

## 部署

### Docker Compose

```bash
docker-compose up -d
```

### 生产环境
1. 配置环境变量
2. 启动 PostgreSQL、Redis、Chroma
3. 启动 FastAPI 后端
4. 构建并部署 React 前端

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 作者

**SHYXIN** - [GitHub](https://github.com/SHYXIN)

---

*This project is for educational and demonstration purposes.*
