"""
网关中间件
"""
import time
import uuid
import logging
from typing import Callable, List, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog
from ..shared.utils.auth import auth_manager
from ..shared.utils.cache import rate_limiter, cache_manager

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始
        start_time = time.time()
        logger.info(
            "请求开始",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            headers=dict(request.headers),
            client_ip=request.client.host if request.client else None
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录请求完成
            logger.info(
                "请求完成",
                request_id=request_id,
                status_code=response.status_code,
                process_time=process_time
            )
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录请求错误
            logger.error(
                "请求错误",
                request_id=request_id,
                error=str(e),
                process_time=process_time,
                exc_info=True
            )
            
            # 返回错误响应
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "服务器内部错误",
                    "request_id": request_id
                },
                headers={"X-Request-ID": request_id}
            )


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""
    
    # 无需认证的路径
    EXCLUDED_PATHS = [
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/metrics",
        "/auth/login",
        "/auth/refresh",
        "/api/v1/student/"  # 临时排除学生API路径进行测试
    ]
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查是否需要认证
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # 获取认证头
        authorization = request.headers.get("Authorization")
        if not authorization:
            return self._unauthorized_response("缺少认证头")
        
        # 验证Bearer Token
        if not authorization.startswith("Bearer "):
            return self._unauthorized_response("无效的认证格式")
        
        token = authorization[7:]  # 移除"Bearer "
        
        # 验证令牌
        payload = auth_manager.verify_token(token)
        if not payload:
            return self._unauthorized_response("无效的认证令牌")
        
        # 检查令牌是否过期
        exp = payload.get("exp")
        if exp and time.time() > exp:
            return self._unauthorized_response("认证令牌已过期")
        
        # 将用户信息添加到请求状态
        request.state.user = {
            "id": int(payload["sub"]),
            "openid": payload["openid"],
            "role": payload["role"],
            "nickname": payload.get("nickname"),
            "vip_type": payload.get("vip_type")
        }
        
        return await call_next(request)
    
    def _is_excluded_path(self, path: str) -> bool:
        """检查路径是否需要排除认证"""
        for excluded_path in self.EXCLUDED_PATHS:
            if path.startswith(excluded_path):
                return True
        return False
    
    def _unauthorized_response(self, message: str) -> JSONResponse:
        """返回未授权响应"""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "code": status.HTTP_401_UNAUTHORIZED,
                "message": message
            },
            headers={"WWW-Authenticate": "Bearer"}
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""
    
    # 不同端点的速率限制配置
    RATE_LIMITS = {
        "/auth/login": {"limit": 5, "window": 300},      # 登录：5次/5分钟
        "/api/homework/submit": {"limit": 10, "window": 60},  # 提交作业：10次/分钟
        "/api/ocr": {"limit": 20, "window": 60},         # OCR：20次/分钟
        "default": {"limit": 100, "window": 60}          # 默认：100次/分钟
    }
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 获取用户ID（如果已认证）
        user_id = None
        if hasattr(request.state, "user"):
            user_id = request.state.user["id"]
        
        # 构建速率限制键
        path = request.url.path
        rate_limit_key = f"rate_limit:{path}:{user_id or client_ip}"
        
        # 获取速率限制配置
        config = self.RATE_LIMITS.get(path, self.RATE_LIMITS["default"])
        limit = config["limit"]
        window = config["window"]
        
        # 检查速率限制
        if not rate_limiter.is_allowed(rate_limit_key, limit, window):
            remaining_time = cache_manager.ttl(rate_limit_key)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "code": status.HTTP_429_TOO_MANY_REQUESTS,
                    "message": f"请求过于频繁，请在{remaining_time}秒后重试",
                    "retry_after": remaining_time
                },
                headers={"Retry-After": str(remaining_time)}
            )
        
        # 处理请求
        response = await call_next(request)
        
        # 添加速率限制响应头
        remaining = rate_limiter.get_remaining(rate_limit_key, limit)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(window)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 返回直接连接IP
        return request.client.host if request.client else "unknown"


class MetricsMiddleware(BaseHTTPMiddleware):
    """监控指标中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始时间
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录监控指标
        from .main import REQUEST_COUNT, REQUEST_DURATION, ACTIVE_CONNECTIONS
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()
        
        REQUEST_DURATION.observe(process_time)
        
        # 记录自定义指标到Redis
        self._record_custom_metrics(request, response, process_time)
        
        return response
    
    def _record_custom_metrics(self, request: Request, response: Response, process_time: float):
        """记录自定义指标"""
        try:
            # 构建指标数据
            metric_data = {
                "timestamp": time.time(),
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
                "user_id": getattr(request.state, "user", {}).get("id"),
                "user_agent": request.headers.get("User-Agent"),
                "client_ip": request.client.host if request.client else None
            }
            
            # 保存到Redis（可选，用于实时监控）
            metric_key = f"metrics:request:{time.time()}"
            cache_manager.set(metric_key, metric_data, ttl=86400)  # 保存24小时
            
        except Exception as e:
            logger.error("记录监控指标失败", error=str(e))


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查恶意请求
        if self._is_malicious_request(request):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "请求被安全策略拒绝"
                }
            )
        
        # 处理请求
        response = await call_next(request)
        
        # 添加安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
    
    def _is_malicious_request(self, request: Request) -> bool:
        """检查是否为恶意请求"""
        # 检查SQL注入
        query_string = str(request.url.query)
        if self._contains_sql_injection(query_string):
            logger.warning("检测到SQL注入尝试", url=str(request.url))
            return True
        
        # 检查XSS
        user_agent = request.headers.get("User-Agent", "")
        if self._contains_xss(user_agent):
            logger.warning("检测到XSS尝试", user_agent=user_agent)
            return True
        
        # 检查请求大小
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            logger.warning("请求体过大", content_length=content_length)
            return True
        
        return False
    
    def _contains_sql_injection(self, text: str) -> bool:
        """检查SQL注入"""
        sql_keywords = [
            "union", "select", "insert", "update", "delete", "drop",
            "create", "alter", "exec", "execute", "script", "iframe"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in sql_keywords)
    
    def _contains_xss(self, text: str) -> bool:
        """检查XSS"""
        xss_patterns = ["<script", "javascript:", "onload=", "onerror=", "onclick="]
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in xss_patterns)