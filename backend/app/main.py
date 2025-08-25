from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from loguru import logger
import time
import os

from app.core.config import settings
from app.core.database import init_db
from app.middleware.cors import setup_cors
from app.middleware.logging import logging_middleware
from app.middleware.rate_limit import rate_limit_middleware
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    logger.info("正在初始化数据库连接...")
    init_db()
    logger.info("数据库初始化完成")
    
    yield
    
    # 关闭时清理资源
    logger.info("正在关闭应用...")

# 创建FastAPI应用
app = FastAPI(
    title="中小学智能批改平台",
    description="基于AI的中小学作业智能批改系统，支持数学、语文、英语等多学科批改",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# 配置CORS中间件
setup_cors(app)

# 添加自定义中间件
app.middleware("http")(logging_middleware)
app.middleware("http")(rate_limit_middleware)

# 配置静态文件服务
uploads_path = os.path.join(os.getcwd(), "uploads")
os.makedirs(uploads_path, exist_ok=True)
print(f"静态文件路径: {uploads_path}")
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"全局异常: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "服务器内部错误",
            "error": str(exc) if settings.ENVIRONMENT != "production" else "Internal server error"
        }
    )

# 健康检查端点
@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# 根路径重定向
@app.get("/")
async def root():
    """根路径接口"""
    return {
        "message": "欢迎使用中小学智能批改平台API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# 注册API路由
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"启动服务器，环境: {settings.ENVIRONMENT}")
    logger.info(f"服务地址: http://localhost:{settings.PORT}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        access_log=True,
        log_level="info"
    )