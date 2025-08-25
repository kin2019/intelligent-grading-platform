from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy import MetaData, create_engine
from app.core.config import get_settings
import redis.asyncio as redis

settings = get_settings()

# Redis连接池
redis_pool = None

class Base(DeclarativeBase):
    """数据库基类"""
    metadata = MetaData()

# 同步数据库引擎（用于初始化）
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_POOL_OVERFLOW,
    echo=settings.DEBUG
)

# 同步会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """获取同步数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_redis():
    """获取Redis连接"""
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password="redis123",  # 使用Docker配置的密码
            db=0,
            decode_responses=True
        )
    return redis.Redis(connection_pool=redis_pool)

def init_db():
    """初始化数据库"""
    # 导入所有模型，确保它们被注册到metadata中
    from app.models import User, StudyPlan, StudyTask, StudyProgress
    from app.models.parent_child import ParentChild, BindInvite
    from app.models.homework import Homework, ErrorQuestion
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)