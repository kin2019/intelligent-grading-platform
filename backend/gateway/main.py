"""
API网关主入口
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from prometheus_client import generate_latest, Counter, Histogram, Gauge
import time
import structlog
from .middleware import (
    AuthMiddleware,
    RateLimitMiddleware,
    LoggingMiddleware,
    MetricsMiddleware
)
from .routes import auth, health, proxy
from ..shared.config.settings import get_settings
from ..shared.utils.cache import cache_manager
from ..shared.utils.database import db_manager

# 配置日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)
settings = get_settings()

# 监控指标
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status_code'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active connections')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("API网关启动中...")
    
    # 检查数据库连接
    if not db_manager.health_check():
        logger.error("数据库连接失败")
        raise Exception("数据库连接失败")
    
    # 检查Redis连接
    if not cache_manager.health_check():
        logger.error("Redis连接失败")
        raise Exception("Redis连接失败")
    
    logger.info("API网关启动成功")
    
    yield
    
    # 关闭时清理
    logger.info("API网关关闭中...")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="ZYJC智能批改平台API网关",
        description="中小学全学科智能批改平台API网关",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加受信任主机中间件
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
        )
    
    # 添加自定义中间件
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuthMiddleware)
    
    # 注册路由
    app.include_router(health.router, prefix="/health", tags=["健康检查"])
    app.include_router(auth.router, prefix="/auth", tags=["认证"])
    app.include_router(proxy.router, prefix="/api", tags=["代理"])
    
    # 异常处理器
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTP异常处理"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """请求验证异常处理"""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "请求参数验证失败",
                "details": exc.errors(),
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理"""
        logger.error("未处理的异常", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "服务器内部错误",
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    # 根路径
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "message": "ZYJC智能批改平台API网关",
            "version": "1.0.0",
            "status": "running",
            "timestamp": time.time()
        }
    
    # 监控指标端点
    @app.get("/metrics")
    async def metrics():
        """Prometheus监控指标"""
        return generate_latest()
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )