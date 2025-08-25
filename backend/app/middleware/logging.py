import time
import uuid
from typing import Callable
from fastapi import Request, Response
from loguru import logger
from app.core.config import settings

async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """日志记录中间件"""
    # 生成请求ID
    request_id = str(uuid.uuid4())
    
    # 记录请求开始
    start_time = time.time()
    logger.info(
        f"请求开始 [{request_id}] {request.method} {request.url}"
    )
    
    # 处理请求
    try:
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录请求完成
        logger.info(
            f"请求完成 [{request_id}] {response.status_code} "
            f"耗时: {process_time:.3f}s"
        )
        
        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # 记录请求异常
        process_time = time.time() - start_time
        logger.error(
            f"请求异常 [{request_id}] {request.method} {request.url} "
            f"错误: {str(e)} 耗时: {process_time:.3f}s"
        )
        raise