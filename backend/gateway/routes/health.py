"""
健康检查路由
"""
from datetime import datetime
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from ...shared.models.base import HealthCheckModel
from ...shared.utils.database import db_manager
from ...shared.utils.cache import cache_manager
from ...shared.config.settings import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/", response_model=HealthCheckModel)
async def health_check():
    """基础健康检查"""
    return HealthCheckModel(
        status="ok",
        timestamp=datetime.now(),
        version="1.0.0",
        environment=settings.environment
    )


@router.get("/detailed")
async def detailed_health_check():
    """详细健康检查"""
    services = {}
    overall_status = "ok"
    
    # 检查数据库
    try:
        db_healthy = db_manager.health_check()
        services["database"] = "ok" if db_healthy else "error"
        if not db_healthy:
            overall_status = "degraded"
    except Exception as e:
        services["database"] = f"error: {str(e)}"
        overall_status = "degraded"
    
    # 检查Redis
    try:
        redis_healthy = cache_manager.health_check()
        services["redis"] = "ok" if redis_healthy else "error"
        if not redis_healthy:
            overall_status = "degraded"
    except Exception as e:
        services["redis"] = f"error: {str(e)}"
        overall_status = "degraded"
    
    # 检查外部服务（可选）
    services["ocr_service"] = "ok"  # 这里可以添加实际的OCR服务检查
    services["ai_service"] = "ok"   # 这里可以添加实际的AI服务检查
    
    response_data = {
        "status": overall_status,
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "environment": settings.environment,
        "services": services
    }
    
    # 根据状态设置HTTP状态码
    status_code = status.HTTP_200_OK if overall_status == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(content=response_data, status_code=status_code)


@router.get("/readiness")
async def readiness_check():
    """就绪检查"""
    try:
        # 检查关键依赖是否就绪
        db_ready = db_manager.health_check()
        redis_ready = cache_manager.health_check()
        
        if db_ready and redis_ready:
            return {"status": "ready", "timestamp": datetime.now()}
        else:
            return JSONResponse(
                content={"status": "not_ready", "timestamp": datetime.now()},
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.now()
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@router.get("/liveness")
async def liveness_check():
    """存活检查"""
    return {"status": "alive", "timestamp": datetime.now()}