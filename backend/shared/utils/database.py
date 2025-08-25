"""
数据库工具函数
"""
import logging
from typing import Generator, Optional
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import contextmanager, asynccontextmanager
from ..config.settings import get_settings
from ..models.base import Base

logger = logging.getLogger(__name__)
settings = get_settings()

# 同步数据库引擎
engine = create_engine(
    settings.database.url,
    echo=settings.database.echo,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_recycle=settings.database.pool_recycle,
)

# 异步数据库引擎（如果需要）
async_engine = create_async_engine(
    settings.database.url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.database.echo,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_recycle=settings.database.pool_recycle,
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


def create_tables():
    """创建所有数据表"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据表创建成功")
    except Exception as e:
        logger.error(f"数据表创建失败: {e}")
        raise


def drop_tables():
    """删除所有数据表"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("数据表删除成功")
    except Exception as e:
        logger.error(f"数据表删除失败: {e}")
        raise


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """获取数据库会话（同步版本）"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"数据库操作失败: {e}")
        raise
    finally:
        session.close()


@asynccontextmanager
async def get_async_db_session() -> AsyncSession:
    """获取数据库会话（异步版本）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise


def get_db() -> Generator[Session, None, None]:
    """FastAPI依赖注入使用的数据库会话获取函数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """FastAPI依赖注入使用的异步数据库会话获取函数"""
    async with AsyncSessionLocal() as session:
        yield session


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = engine
        self.async_engine = async_engine
        self.session_factory = SessionLocal
        self.async_session_factory = AsyncSessionLocal
    
    def health_check(self) -> bool:
        """数据库健康检查"""
        try:
            with get_db_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False
    
    async def async_health_check(self) -> bool:
        """异步数据库健康检查"""
        try:
            async with get_async_db_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"异步数据库健康检查失败: {e}")
            return False
    
    def get_table_info(self) -> dict:
        """获取数据表信息"""
        try:
            metadata = MetaData()
            metadata.reflect(bind=engine)
            tables = {}
            for table_name, table in metadata.tables.items():
                tables[table_name] = {
                    "columns": [col.name for col in table.columns],
                    "primary_keys": [col.name for col in table.primary_key],
                    "foreign_keys": [
                        f"{fk.parent.name} -> {fk.column.table.name}.{fk.column.name}"
                        for fk in table.foreign_keys
                    ]
                }
            return tables
        except Exception as e:
            logger.error(f"获取数据表信息失败: {e}")
            return {}
    
    def backup_database(self, backup_file: str) -> bool:
        """备份数据库"""
        try:
            # 这里可以实现数据库备份逻辑
            # 例如使用 pg_dump 等工具
            logger.info(f"数据库备份到: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return False
    
    def restore_database(self, backup_file: str) -> bool:
        """恢复数据库"""
        try:
            # 这里可以实现数据库恢复逻辑
            # 例如使用 pg_restore 等工具
            logger.info(f"从备份文件恢复数据库: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"数据库恢复失败: {e}")
            return False


# 全局数据库管理器实例
db_manager = DatabaseManager()


class BaseRepository:
    """基础仓储类"""
    
    def __init__(self, model_class):
        self.model_class = model_class
    
    def create(self, db: Session, **kwargs):
        """创建记录"""
        db_obj = self.model_class(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, db: Session, id: int):
        """根据ID获取记录"""
        return db.query(self.model_class).filter(self.model_class.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100):
        """获取多条记录"""
        return db.query(self.model_class).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj, **kwargs):
        """更新记录"""
        for field, value in kwargs.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int):
        """删除记录"""
        db_obj = self.get_by_id(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj
    
    def count(self, db: Session) -> int:
        """获取记录总数"""
        return db.query(self.model_class).count()
    
    def exists(self, db: Session, **kwargs) -> bool:
        """检查记录是否存在"""
        query = db.query(self.model_class)
        for field, value in kwargs.items():
            if hasattr(self.model_class, field):
                query = query.filter(getattr(self.model_class, field) == value)
        return query.first() is not None


def paginate(query, page: int = 1, size: int = 20):
    """分页查询"""
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size if total > 0 else 0,
        "has_next": page * size < total,
        "has_prev": page > 1
    }