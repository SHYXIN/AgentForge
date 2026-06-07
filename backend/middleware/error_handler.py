"""
错误处理中间件

提供全局异常捕获和统一错误响应格式。
"""
import logging
import traceback
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """错误处理中间件，捕获所有未处理的异常。"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        try:
            response = await self.app(scope, receive, send)
            return response
        except Exception as e:
            # 记录错误日志
            error_id = str(uuid.uuid4())
            logger.error(
                f"[{error_id}] 未处理的异常: {str(e)}",
                extra={
                    "error_id": error_id,
                    "path": request.url.path,
                    "method": request.method,
                    "traceback": traceback.format_exc()
                }
            )
            
            # 返回统一错误响应
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "error_id": error_id,
                    "message": "服务器内部错误，请稍后重试",
                    "path": request.url.path
                }
            )


def add_error_handler_middleware(app):
    """向 FastAPI 应用添加错误处理中间件。"""
    app.add_middleware(ErrorHandlerMiddleware)
