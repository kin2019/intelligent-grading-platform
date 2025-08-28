from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "中小学智能批改平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 安全配置
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "zyjc_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres123"
    DATABASE_URL: str = "sqlite:///./app.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_POOL_OVERFLOW: int = 0
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_EXPIRE_TIME: int = 3600  # 1小时
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",  # 添加前端服务地址
        "http://localhost:8001",  # 添加新的前端服务地址
        "http://localhost:8080",
        "https://localhost:3000",
        "https://localhost:8000",  # 添加HTTPS版本
        "https://localhost:8001",  # 添加HTTPS版本
        "https://localhost:8080",
    ]
    
    # 微信小程序配置
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    
    # OCR服务配置
    BAIDU_OCR_API_KEY: str = ""
    BAIDU_OCR_SECRET_KEY: str = ""
    
    # 文件存储配置
    UPLOAD_PATH: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings() -> Settings:
    """获取设置实例"""
    return Settings()

# 创建全局设置实例
settings = get_settings()

# 创建必要的目录
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
os.makedirs("logs", exist_ok=True)