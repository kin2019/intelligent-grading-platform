"""
缓存工具函数
"""
import json
import pickle
import logging
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
from functools import wraps
import redis
from ..config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Redis连接池
redis_pool = redis.ConnectionPool.from_url(
    settings.redis.url,
    encoding=settings.redis.encoding,
    decode_responses=settings.redis.decode_responses,
    max_connections=settings.redis.max_connections
)

# Redis客户端
redis_client = redis.Redis(connection_pool=redis_pool)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_client: redis.Redis = redis_client):
        self.redis = redis_client
        self.default_ttl = 3600  # 默认过期时间1小时
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            # 序列化数据
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, (str, int, float, bool)):
                serialized_value = value
            else:
                serialized_value = pickle.dumps(value)
            
            return self.redis.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False
    
    def get(self, key: str) -> Any:
        """获取缓存"""
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            
            # 尝试JSON反序列化
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                pass
            
            # 尝试pickle反序列化
            try:
                return pickle.loads(value)
            except (pickle.PickleError, TypeError):
                pass
            
            # 返回原始值
            return value
        except Exception as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"删除缓存失败 {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"检查缓存存在性失败 {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """设置缓存过期时间"""
        try:
            return bool(self.redis.expire(key, ttl))
        except Exception as e:
            logger.error(f"设置缓存过期时间失败 {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """获取缓存剩余时间"""
        try:
            return self.redis.ttl(key)
        except Exception as e:
            logger.error(f"获取缓存剩余时间失败 {key}: {e}")
            return -1
    
    def clear_pattern(self, pattern: str) -> int:
        """根据模式清除缓存"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"清除缓存模式失败 {pattern}: {e}")
            return 0
    
    def increment(self, key: str, amount: int = 1) -> int:
        """增加缓存数值"""
        try:
            return self.redis.incr(key, amount)
        except Exception as e:
            logger.error(f"增加缓存数值失败 {key}: {e}")
            return 0
    
    def decrement(self, key: str, amount: int = 1) -> int:
        """减少缓存数值"""
        try:
            return self.redis.decr(key, amount)
        except Exception as e:
            logger.error(f"减少缓存数值失败 {key}: {e}")
            return 0
    
    def health_check(self) -> bool:
        """Redis健康检查"""
        try:
            return self.redis.ping()
        except Exception as e:
            logger.error(f"Redis健康检查失败: {e}")
            return False


# 全局缓存管理器实例
cache_manager = CacheManager()


def cache_key(*args, **kwargs) -> str:
    """生成缓存键"""
    key_parts = []
    for arg in args:
        if isinstance(arg, (str, int, float)):
            key_parts.append(str(arg))
        else:
            key_parts.append(str(hash(str(arg))))
    
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)


def cached(ttl: int = 3600, key_prefix: str = ""):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            func_name = f"{func.__module__}.{func.__name__}"
            cache_key_str = cache_key(func_name, key_prefix, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key_str)
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key_str}")
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 保存到缓存
            cache_manager.set(cache_key_str, result, ttl)
            logger.debug(f"缓存保存: {cache_key_str}")
            
            return result
        return wrapper
    return decorator


def cache_user_data(user_id: int, data: Dict[str, Any], ttl: int = 1800) -> bool:
    """缓存用户数据"""
    key = f"user:data:{user_id}"
    return cache_manager.set(key, data, ttl)


def get_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """获取用户缓存数据"""
    key = f"user:data:{user_id}"
    return cache_manager.get(key)


def cache_homework_result(homework_id: int, result: Dict[str, Any], ttl: int = 86400) -> bool:
    """缓存作业批改结果"""
    key = f"homework:result:{homework_id}"
    return cache_manager.set(key, result, ttl)


def get_homework_result(homework_id: int) -> Optional[Dict[str, Any]]:
    """获取作业批改结果缓存"""
    key = f"homework:result:{homework_id}"
    return cache_manager.get(key)


def cache_ocr_result(image_hash: str, result: Dict[str, Any], ttl: int = 604800) -> bool:
    """缓存OCR识别结果"""
    key = f"ocr:result:{image_hash}"
    return cache_manager.set(key, result, ttl)


def get_ocr_result(image_hash: str) -> Optional[Dict[str, Any]]:
    """获取OCR识别结果缓存"""
    key = f"ocr:result:{image_hash}"
    return cache_manager.get(key)


def cache_similar_questions(question_id: int, questions: List[Dict[str, Any]], ttl: int = 86400) -> bool:
    """缓存相似题目"""
    key = f"similar:questions:{question_id}"
    return cache_manager.set(key, questions, ttl)


def get_similar_questions(question_id: int) -> Optional[List[Dict[str, Any]]]:
    """获取相似题目缓存"""
    key = f"similar:questions:{question_id}"
    return cache_manager.get(key)


def cache_user_quota(user_id: int, quota_data: Dict[str, Any], ttl: int = 3600) -> bool:
    """缓存用户配额信息"""
    key = f"user:quota:{user_id}"
    return cache_manager.set(key, quota_data, ttl)


def get_user_quota(user_id: int) -> Optional[Dict[str, Any]]:
    """获取用户配额缓存"""
    key = f"user:quota:{user_id}"
    return cache_manager.get(key)


def increment_daily_usage(user_id: int) -> int:
    """增加用户每日使用次数"""
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"user:daily_usage:{user_id}:{today}"
    
    # 设置过期时间为明天凌晨
    tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    ttl = int((tomorrow - datetime.now()).total_seconds())
    
    usage = cache_manager.increment(key)
    if usage == 1:  # 第一次使用，设置过期时间
        cache_manager.expire(key, ttl)
    
    return usage


def get_daily_usage(user_id: int) -> int:
    """获取用户每日使用次数"""
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"user:daily_usage:{user_id}:{today}"
    usage = cache_manager.get(key)
    return int(usage) if usage else 0


def clear_user_cache(user_id: int) -> int:
    """清除用户相关缓存"""
    pattern = f"user:*:{user_id}*"
    return cache_manager.clear_pattern(pattern)


def cache_analysis_result(analysis_id: str, result: Dict[str, Any], ttl: int = 86400) -> bool:
    """缓存分析结果"""
    key = f"analysis:result:{analysis_id}"
    return cache_manager.set(key, result, ttl)


def get_analysis_result(analysis_id: str) -> Optional[Dict[str, Any]]:
    """获取分析结果缓存"""
    key = f"analysis:result:{analysis_id}"
    return cache_manager.get(key)


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, cache_manager: CacheManager = cache_manager):
        self.cache = cache_manager
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """检查是否允许访问"""
        try:
            current = self.cache.get(key) or 0
            if current >= limit:
                return False
            
            # 增加计数
            self.cache.increment(key)
            
            # 第一次访问时设置过期时间
            if current == 0:
                self.cache.expire(key, window)
            
            return True
        except Exception as e:
            logger.error(f"速率限制检查失败 {key}: {e}")
            return True  # 出错时允许访问
    
    def get_remaining(self, key: str, limit: int) -> int:
        """获取剩余次数"""
        try:
            current = self.cache.get(key) or 0
            return max(0, limit - current)
        except Exception as e:
            logger.error(f"获取剩余次数失败 {key}: {e}")
            return limit


# 全局速率限制器实例
rate_limiter = RateLimiter()