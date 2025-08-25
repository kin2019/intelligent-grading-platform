"""
基础数据模型
"""
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, Integer, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel, ConfigDict


class Base(DeclarativeBase):
    """SQLAlchemy基础模型"""
    pass


class BaseTable(Base):
    """数据表基础模型"""
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )


class BaseSchema(BaseModel):
    """Pydantic基础模型"""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True
    )


class ResponseModel(BaseSchema):
    """统一响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


class PaginationModel(BaseSchema):
    """分页模型"""
    page: int = 1
    size: int = 20
    total: int = 0
    pages: int = 0
    has_next: bool = False
    has_prev: bool = False


class PaginatedResponseModel(ResponseModel):
    """分页响应模型"""
    data: Optional[Any] = None
    pagination: Optional[PaginationModel] = None


class ErrorDetail(BaseSchema):
    """错误详情模型"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponseModel(BaseSchema):
    """错误响应模型"""
    code: int
    message: str
    details: Optional[list[ErrorDetail]] = None
    request_id: Optional[str] = None


class HealthCheckModel(BaseSchema):
    """健康检查模型"""
    status: str = "ok"
    timestamp: datetime
    version: str
    environment: str
    services: Dict[str, str] = {}


class FileUploadModel(BaseSchema):
    """文件上传模型"""
    filename: str
    content_type: str
    size: int
    url: str
    cdn_url: Optional[str] = None