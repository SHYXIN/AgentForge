# 多 Agent 协作架构实现

## 概述

本文档描述了 AgentForge 项目中多 Agent 协作架构的实现。该架构使用 TDD（测试驱动开发）方式开发，确保代码质量和可维护性。

## 架构设计

### 核心组件

1. **Agent 基类 (`AgentBase`)**
   - 定义 Agent 的基本接口
   - 支持同步和异步执行
   - 消息传递机制
   - 能力管理

2. **专业 Agent**
   - **Orchestrator Agent**: 负责任务分解和分配
   - **Coder Agent**: 负责代码生成和调试
   - **Researcher Agent**: 负责知识检索和信息总结

3. **Agent 编排器 (`AgentOrchestrator`)**
   - 协调多个 Agent 的工作
   - 管理任务生命周期
   - 支持并行执行

4. **多 Agent 服务 (`MultiAgentService`)**
   - 提供高层 API 接口
   - 管理任务存储和状态
   - 处理用户交互

### 数据模型

- **AgentMessage**: Agent 间消息传递
- **AgentTask**: 任务定义和状态管理
- **AgentResult**: 任务执行结果

### 通信机制

Agent 之间使用消息传递进行通信：
- 每个 Agent 都有 inbox 和 outbox
- 支持异步消息处理
- 消息类型包括：task, result, query, response, error, status

## API 端点

### 1. 多 Agent 聊天

```
POST /api/multi-agent/chat
```

**请求体：**
```json
{
  "message": "帮我生成一个计算器应用",
  "task_type": "user_request"
}
```

**响应：**
```json
{
  "task_id": "uuid",
  "response": "任务处理完成",
  "result": {
    "task_id_1": {...},
    "task_id_2": {...}
  }
}
```

### 2. 查询任务状态

```
GET /api/multi-agent/status/{task_id}
```

**响应：**
```json
{
  "task_id": "uuid",
  "status": "completed",
  "message": "帮我生成一个计算器应用",
  "result": {...}
}
```

## 测试覆盖

### 测试统计

- 总测试数: 31
- 测试通过率: 100%
- 测试类别:
  - 数据模型测试: 4
  - Agent 基类测试: 5
  - Orchestrator 测试: 3
  - Coder Agent 测试: 3
  - Researcher Agent 测试: 3
  - Agent 编排器测试: 4
  - 多 Agent 服务测试: 4
  - API 端点测试: 3

### TDD 开发流程

1. **RED 阶段**: 编写失败的测试
2. **GREEN 阶段**: 实现功能让测试通过
3. **REFACTOR 阶段**: 优化代码结构和质量

## 技术栈

- Python 3.10
- FastAPI
- asyncio
- pytest
- Pydantic
- dataclasses

## 文件结构

```
backend/
├── services/
│   ├── multi_agent.py          # 多 Agent 服务实现
│   └── ...
├── tests/
│   ├── test_multi_agent.py     # 多 Agent 测试
│   └── ...
├── api/
│   ├── multi_agent_routes.py   # API 路由
│   └── ...
└── models/
    └── __init__.py             # 数据模型定义
```

## 设计决策

### 1. 异步设计

所有 Agent 操作都使用 async/await，以支持：
- 并发任务执行
- 非阻塞 I/O 操作
- 更好的性能

### 2. 消息传递

Agent 之间使用消息传递而非直接调用，以实现：
- 松耦合
- 可扩展性
- 更好的错误处理

### 3. 任务分解

Orchestrator Agent 自动分解复杂任务：
- 识别任务类型（代码生成、研究等）
- 创建子任务
- 分配给合适的 Agent

### 4. 错误处理

完善的错误处理机制：
- 任务级别错误捕获
- Agent 级别错误恢复
- API 级别错误响应

## 扩展指南

### 添加新的 Agent 类型

1. 创建新 Agent 类继承 `AgentBase`
2. 实现 `execute_task` 方法
3. 在 `MultiAgentService` 中注册
4. 添加相应的测试

### 添加新的任务类型

1. 在 `AgentTask` 中支持新类型
2. 在对应的 Agent 中实现处理逻辑
3. 更新 Orchestrator 的任务分配策略
4. 添加测试用例

## 性能考虑

### 并行执行

- 使用 `asyncio.gather` 实现任务并行
- Agent 独立运行，无阻塞
- 支持动态添加 Agent

### 资源管理

- 任务状态持久化（当前为内存，可扩展为数据库）
- 消息队列管理
- 错误重试机制

## 安全考虑

- 输入验证（使用 Pydantic）
- 错误信息不泄露内部细节
- 任务隔离（每个任务独立执行）

## 后续改进

1. **持久化存储**: 将任务状态存储到数据库
2. **WebSocket 支持**: 实时任务状态更新
3. **Agent 池管理**: 动态创建和销毁 Agent
4. **更智能的任务分配**: 基于 Agent 负载和能力的动态分配
5. **结果缓存**: 缓存相似任务的结果
