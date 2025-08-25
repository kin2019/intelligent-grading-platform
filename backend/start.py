#!/usr/bin/env python3
"""
应用启动脚本
"""

import uvicorn
from app.main import app
from app.core.config import settings
from loguru import logger

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("🚀 启动中小学智能批改平台后端服务")
    logger.info("=" * 50)
    logger.info(f"环境: {settings.ENVIRONMENT}")
    logger.info(f"数据库: PostgreSQL - {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    logger.info(f"Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    logger.info(f"服务地址: http://0.0.0.0:{settings.PORT}")
    logger.info(f"API文档: http://localhost:{settings.PORT}/docs")
    logger.info("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        access_log=True,
        log_level="info",
        loop="asyncio"
    )