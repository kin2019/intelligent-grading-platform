"""
数学批改服务主入口
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from .api import elementary, middle, homework
from .engines import arithmetic, algebra, geometry, function_engine
from ....shared.config.settings import get_settings
from ....shared.utils.database import db_manager
from ....shared.utils.cache import cache_manager

logger = structlog.get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("数学批改服务启动中...")
    
    # 初始化数学引擎
    try:
        arithmetic.init_engine()
        algebra.init_engine()
        geometry.init_engine()
        function_engine.init_engine()
        logger.info("数学引擎初始化完成")
    except Exception as e:
        logger.error(f"数学引擎初始化失败: {e}")
        raise
    
    logger.info("数学批改服务启动成功")
    yield
    logger.info("数学批改服务关闭中...")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="数学批改服务",
        description="小学和初中数学作业智能批改",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        lifespan=lifespan
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(homework.router, prefix="/homework", tags=["作业批改"])
    app.include_router(elementary.router, prefix="/elementary", tags=["小学数学"])
    app.include_router(middle.router, prefix="/middle", tags=["初中数学"])
    
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": "math-service", "version": "1.0.0"}
    
    return app


app = create_app()