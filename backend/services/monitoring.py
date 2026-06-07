"""
监控服务

提供 Prometheus 指标、结构化日志和 Agent 决策追踪。
"""
import time
import uuid
import logging
from functools import wraps
from typing import Callable, Any

from prometheus_client import Counter, Histogram, Gauge, generate_latest

# ============ Prometheus 指标 ============

# 请求计数器
REQUEST_COUNT = Counter(
    'http_requests_total',
    'HTTP 请求总数',
    ['method', 'endpoint', 'status']
)

# 请求延迟直方图
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP 请求延迟（秒）',
    ['method', 'endpoint']
)

# 错误计数器
ERROR_COUNT = Counter(
    'http_errors_total',
    'HTTP 错误总数',
    ['method', 'endpoint', 'status']
)

# 活跃连接数
ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    '活跃连接数'
)

# Agent 调用计数
AGENT_CALLS = Counter(
    'agent_calls_total',
    'Agent 调用总数',
    ['agent_type', 'status']
)

# Agent 调用延迟
AGENT_LATENCY = Histogram(
    'agent_call_duration_seconds',
    'Agent 调用延迟（秒）',
    ['agent_type']
)


# ============ 结构化日志 ============

def setup_logging():
    """配置结构化日志。"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def get_logger(name: str) -> logging.Logger:
    """获取命名日志器。"""
    return logging.getLogger(name)


# ============ 请求追踪 ============

def track_request(method: str, endpoint: str):
    """请求追踪装饰器。"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            status = "success"
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                
                # 记录指标
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()
                
                REQUEST_LATENCY.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
                
                if status == "error":
                    ERROR_COUNT.labels(
                        method=method,
                        endpoint=endpoint,
                        status="500"
                    ).inc()
        
        return wrapper
    return decorator


# ============ Agent 追踪 ============

class AgentTracer:
    """Agent 决策追踪器。"""
    
    def __init__(self):
        self.traces = {}
    
    def start_trace(self, agent_type: str) -> str:
        """开始追踪。"""
        trace_id = str(uuid.uuid4())
        self.traces[trace_id] = {
            "agent_type": agent_type,
            "start_time": time.time(),
            "steps": [],
            "status": "running"
        }
        return trace_id
    
    def add_step(self, trace_id: str, step: str, detail: str = ""):
        """添加追踪步骤。"""
        if trace_id in self.traces:
            self.traces[trace_id]["steps"].append({
                "step": step,
                "detail": detail,
                "timestamp": time.time()
            })
    
    def end_trace(self, trace_id: str, status: str = "success"):
        """结束追踪。"""
        if trace_id in self.traces:
            self.traces[trace_id]["end_time"] = time.time()
            self.traces[trace_id]["status"] = status
            self.traces[trace_id]["duration"] = (
                self.traces[trace_id]["end_time"] -
                self.traces[trace_id]["start_time"]
            )
            
            # 记录指标
            AGENT_CALLS.labels(
                agent_type=self.traces[trace_id]["agent_type"],
                status=status
            ).inc()
            
            AGENT_LATENCY.labels(
                agent_type=self.traces[trace_id]["agent_type"]
            ).observe(self.traces[trace_id]["duration"])
    
    def get_trace(self, trace_id: str) -> dict:
        """获取追踪信息。"""
        return self.traces.get(trace_id, {})


# 全局追踪器实例
agent_tracer = AgentTracer()


# ============ 指标导出 ============

def get_metrics() -> bytes:
    """获取 Prometheus 指标。"""
    return generate_latest()
