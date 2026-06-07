# Docker 代码执行沙箱服务

## 概述

这是一个基于 Docker 的安全代码执行沙箱服务，用于在隔离的环境中执行 Python 代码。

## 特性

### 1. 安全隔离
- 每次执行启动独立的 Docker 容器
- 执行完后自动销毁容器
- 网络隔离（禁止外部网络访问）
- 文件系统隔离（只读 + 临时目录）

### 2. 资源限制
- 执行时间限制：默认 30 秒
- 内存限制：默认 512MB
- CPU 限制：默认 0.5 核心
- 可配置的超时和资源限制

### 3. 安全检查
- 危险函数过滤（os.system, eval, exec 等）
- 危险模块导入检查（subprocess, shutil 等）
- 可自定义安全策略

### 4. 模拟执行
- 当 Docker 不可用时，自动切换到本地模拟执行
- 支持在没有 Docker 的环境中进行开发和测试

## 使用方法

### 1. 基本使用

```python
from backend.services.code_executor import CodeExecutor

# 创建执行器（使用默认配置）
executor = CodeExecutor()

# 执行代码
result = executor.execute("print('Hello, World!')")

print(f"标准输出: {result['stdout']}")
print(f"标准错误: {result['stderr']}")
print(f"退出码: {result['exit_code']}")
```

### 2. 自定义配置

```python
# 自定义超时、内存和 CPU 限制
executor = CodeExecutor(
    timeout=60,          # 60 秒超时
    memory_limit="1g",   # 1GB 内存
    cpu_limit=1.0,       # 1 个 CPU 核心
    image="python:3.10-slim"
)
```

### 3. 传递环境变量

```python
result = executor.execute(
    code="import os; print(os.environ.get('MY_VAR'))",
    env={'MY_VAR': 'hello'}
)
```

### 4. 设置工作目录

```python
result = executor.execute(
    code="import os; print(os.getcwd())",
    workdir="/workspace"
)
```

### 5. 使用上下文管理器

```python
with CodeExecutor() as executor:
    result = executor.execute("print('test')")
    # 自动关闭 Docker 客户端连接
```

## API 端点

### POST /api/execute

执行 Python 代码。

**请求体：**
```json
{
  "code": "print('Hello, World!')",
  "env": {
    "MY_VAR": "value"
  },
  "workdir": "/workspace"
}
```

**响应体：**
```json
{
  "stdout": "Hello, World!\n",
  "stderr": "",
  "exit_code": 0
}
```

## 测试

运行测试套件：

```bash
cd backend
python -m pytest tests/test_code_executor.py -v
```

## 配置参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| timeout | int | 30 | 执行超时时间（秒） |
| memory_limit | str | "512m" | 内存限制（如 "512m", "1g"） |
| cpu_limit | float | 0.5 | CPU 限制（0.5 表示 0.5 个核心） |
| image | str | "python:3.10-slim" | Docker 镜像名称 |
| docker_base_url | str | "unix:///var/run/docker.sock" | Docker daemon 地址 |

## 安全注意事项

1. **危险代码过滤**：服务会自动过滤包含危险函数和模块的代码
2. **资源限制**：强制执行超时、内存和 CPU 限制
3. **网络隔离**：容器内无法访问外部网络
4. **文件系统隔离**：除 /tmp 目录外，文件系统只读
5. **容器清理**：执行完成后自动销毁容器

## 故障排除

### Docker 不可用

如果 Docker 未安装或无法连接，服务会自动切换到模拟执行模式。在模拟模式下：
- 资源限制不会生效
- 网络隔离不会生效
- 文件系统隔离不会生效
- 仅用于开发和测试

### 安装 Docker

**Linux/macOS:**
```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 启动 Docker
sudo systemctl start docker
```

**Windows:**
1. 下载 Docker Desktop：https://www.docker.com/products/docker-desktop
2. 安装并启动 Docker Desktop

## 依赖

- Python 3.10+
- Docker SDK for Python
- FastAPI（用于 API）

安装依赖：
```bash
pip install docker fastapi
```

## 许可证

MIT License
