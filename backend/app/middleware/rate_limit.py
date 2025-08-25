import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from app.core.database import get_redis
import redis.asyncio as redis

class RateLimiter:
    """频率限制器"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window: int = 60
    ) -> tuple[bool, Dict[str, int]]:
        """
        检查是否允许请求
        
        Args:
            key: 限制key（通常是用户ID或IP）
            limit: 限制次数
            window: 时间窗口（秒）
            
        Returns:
            (是否允许, 统计信息)
        """
        now = int(time.time())
        pipe = self.redis.pipeline()
        
        # 使用滑动窗口算法
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window)
        
        results = await pipe.execute()
        current_requests = results[1]
        
        info = {
            "limit": limit,
            "remaining": max(0, limit - current_requests - 1),
            "reset_time": now + window
        }
        
        return current_requests < limit, info

async def rate_limit_middleware(request: Request, call_next):
    """频率限制中间件"""
    redis_client = await get_redis()
    rate_limiter = RateLimiter(redis_client)
    
    # 获取客户端标识（优先用户ID，其次IP地址）
    client_id = None
    if hasattr(request.state, "user_id"):
        client_id = f"user:{request.state.user_id}"
    else:
        client_ip = request.client.host
        client_id = f"ip:{client_ip}"
    
    # 不同端点的限制配置
    rate_limits = {
        "/api/v1/auth/": {"limit": 10, "window": 60},  # 认证接口
        "/api/v1/homework/correct": {"limit": 20, "window": 60},  # 批改接口
        "default": {"limit": 100, "window": 60}  # 默认限制
    }
    
    # 获取当前路径的限制配置
    path = request.url.path
    limit_config = rate_limits.get("default")
    
    for pattern, config in rate_limits.items():
        if pattern != "default" and path.startswith(pattern):
            limit_config = config
            break
    
    # 检查频率限制
    allowed, info = await rate_limiter.is_allowed(
        f"rate_limit:{client_id}:{path}",
        limit_config["limit"],
        limit_config["window"]
    )
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求频率过高，请稍后重试",
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset_time"])
            }
        )
    
    # 处理请求
    response = await call_next(request)
    
    # 添加频率限制头信息
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(info["reset_time"])
    
    return response