"""
应用配置管理
"""
from functools import lru_cache
from typing import Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    """数据库配置"""
    url: str
    echo: bool = False
    pool_size: int = 20
    max_overflow: int = 30
    pool_recycle: int = 3600


class RedisSettings(BaseModel):
    """Redis配置"""
    url: str
    encoding: str = "utf-8"
    decode_responses: bool = True
    max_connections: int = 20


class JWTSettings(BaseModel):
    """JWT配置"""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


class WeChatSettings(BaseModel):
    """微信配置"""
    app_id: str
    app_secret: str


class OCRSettings(BaseModel):
    """OCR服务配置"""
    baidu_api_key: Optional[str] = None
    baidu_secret_key: Optional[str] = None
    mathpix_app_id: Optional[str] = None
    mathpix_app_key: Optional[str] = None


class AISettings(BaseModel):
    """AI服务配置"""
    openai_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    baidu_wenxin_api_key: Optional[str] = None
    youdao_api_key: Optional[str] = None
    youdao_secret_key: Optional[str] = None


class OSSSettings(BaseModel):
    """对象存储配置"""
    access_key_id: str
    access_key_secret: str
    bucket_name: str
    endpoint: str


class PaymentSettings(BaseModel):
    """支付配置"""
    wechat_mch_id: Optional[str] = None
    wechat_api_key: Optional[str] = None
    alipay_app_id: Optional[str] = None
    alipay_private_key: Optional[str] = None
    alipay_public_key: Optional[str] = None


class Settings(BaseSettings):
    """应用设置"""
    # 基础配置
    app_name: str = "ZYJC智能批改平台"
    debug: bool = False
    environment: str = "production"
    log_level: str = "INFO"
    
    # 数据库配置
    database_url: str
    redis_url: str
    
    # JWT配置
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 微信配置
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    
    # OCR配置
    baidu_ocr_api_key: Optional[str] = None
    baidu_ocr_secret_key: Optional[str] = None
    mathpix_app_id: Optional[str] = None
    mathpix_app_key: Optional[str] = None
    
    # AI服务配置
    openai_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    baidu_wenxin_api_key: Optional[str] = None
    youdao_api_key: Optional[str] = None
    youdao_secret_key: Optional[str] = None
    
    # 文件存储配置
    aliyun_oss_access_key_id: str = ""
    aliyun_oss_access_key_secret: str = ""
    aliyun_oss_bucket_name: str = ""
    aliyun_oss_endpoint: str = ""
    
    # 支付配置
    wechat_pay_mch_id: Optional[str] = None
    wechat_pay_api_key: Optional[str] = None
    alipay_app_id: Optional[str] = None
    alipay_private_key: Optional[str] = None
    alipay_public_key: Optional[str] = None
    
    # 监控配置
    sentry_dsn: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def database(self) -> DatabaseSettings:
        """数据库配置"""
        return DatabaseSettings(
            url=self.database_url,
            echo=self.debug
        )
    
    @property
    def redis(self) -> RedisSettings:
        """Redis配置"""
        return RedisSettings(url=self.redis_url)
    
    @property
    def jwt(self) -> JWTSettings:
        """JWT配置"""
        return JWTSettings(
            secret_key=self.secret_key,
            algorithm=self.algorithm,
            access_token_expire_minutes=self.access_token_expire_minutes
        )
    
    @property
    def wechat(self) -> WeChatSettings:
        """微信配置"""
        return WeChatSettings(
            app_id=self.wechat_app_id,
            app_secret=self.wechat_app_secret
        )
    
    @property
    def ocr(self) -> OCRSettings:
        """OCR配置"""
        return OCRSettings(
            baidu_api_key=self.baidu_ocr_api_key,
            baidu_secret_key=self.baidu_ocr_secret_key,
            mathpix_app_id=self.mathpix_app_id,
            mathpix_app_key=self.mathpix_app_key
        )
    
    @property
    def ai(self) -> AISettings:
        """AI服务配置"""
        return AISettings(
            openai_api_key=self.openai_api_key,
            claude_api_key=self.claude_api_key,
            baidu_wenxin_api_key=self.baidu_wenxin_api_key,
            youdao_api_key=self.youdao_api_key,
            youdao_secret_key=self.youdao_secret_key
        )
    
    @property
    def oss(self) -> OSSSettings:
        """对象存储配置"""
        return OSSSettings(
            access_key_id=self.aliyun_oss_access_key_id,
            access_key_secret=self.aliyun_oss_access_key_secret,
            bucket_name=self.aliyun_oss_bucket_name,
            endpoint=self.aliyun_oss_endpoint
        )
    
    @property
    def payment(self) -> PaymentSettings:
        """支付配置"""
        return PaymentSettings(
            wechat_mch_id=self.wechat_pay_mch_id,
            wechat_api_key=self.wechat_pay_api_key,
            alipay_app_id=self.alipay_app_id,
            alipay_private_key=self.alipay_private_key,
            alipay_public_key=self.alipay_public_key
        )


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


# 全局配置实例
settings = get_settings()