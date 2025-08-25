"""
用户服务主入口
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog
from .api import student, parent, teacher, user_management
from ...shared.config.settings import get_settings
from ...shared.utils.database import db_manager, create_tables
from ...shared.utils.cache import cache_manager

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("用户服务启动中...")
    
    # 创建数据表
    try:
        create_tables()
        logger.info("数据表创建/检查完成")
    except Exception as e:
        logger.error(f"数据表创建失败: {e}")
        raise
    
    # 检查数据库连接
    if not db_manager.health_check():
        logger.error("数据库连接失败")
        raise Exception("数据库连接失败")
    
    # 检查Redis连接
    if not cache_manager.health_check():
        logger.error("Redis连接失败") 
        raise Exception("Redis连接失败")
    
    logger.info("用户服务启动成功")
    
    yield
    
    # 关闭时清理
    logger.info("用户服务关闭中...")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="用户服务",
        description="管理学生、家长、教师用户信息",
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
    
    # 注册路由
    app.include_router(user_management.router, prefix="/users", tags=["用户管理"])
    app.include_router(student.router, prefix="/students", tags=["学生管理"])
    app.include_router(parent.router, prefix="/parents", tags=["家长管理"])
    app.include_router(teacher.router, prefix="/teachers", tags=["教师管理"])
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "ok",
            "service": "user-service",
            "version": "1.0.0"
        }
    
    # 异常处理器
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """请求验证异常处理"""
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "message": "请求参数验证失败",
                "details": exc.errors()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理"""
        logger.error("未处理的异常", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "服务器内部错误"
            }
        )
    
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
        log_level=settings.log_level.lower()
    )