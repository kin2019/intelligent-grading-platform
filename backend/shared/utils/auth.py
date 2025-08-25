"""
认证工具函数
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from ..config.settings import get_settings
from ..models.user import User, UserRole

logger = logging.getLogger(__name__)
settings = get_settings()

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer认证
security = HTTPBearer()


class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.secret_key = settings.jwt.secret_key
        self.algorithm = settings.jwt.algorithm
        self.access_token_expire_minutes = settings.jwt.access_token_expire_minutes
        self.wechat_app_id = settings.wechat.app_id
        self.wechat_app_secret = settings.wechat.app_secret
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"JWT验证失败: {e}")
            return None
    
    def hash_password(self, password: str) -> str:
        """哈希密码"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def get_wechat_session(self, code: str) -> Optional[Dict[str, Any]]:
        """获取微信会话信息"""
        try:
            url = "https://api.weixin.qq.com/sns/jscode2session"
            params = {
                "appid": self.wechat_app_id,
                "secret": self.wechat_app_secret,
                "js_code": code,
                "grant_type": "authorization_code"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()
                
                if "errcode" in data:
                    logger.error(f"微信登录失败: {data}")
                    return None
                
                return data
        except Exception as e:
            logger.error(f"获取微信会话失败: {e}")
            return None
    
    def extract_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """从令牌中提取用户信息"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        return {
            "user_id": payload.get("sub"),
            "openid": payload.get("openid"),
            "role": payload.get("role"),
            "exp": payload.get("exp")
        }
    
    def check_permission(self, user_role: UserRole, required_roles: list[UserRole]) -> bool:
        """检查用户权限"""
        return user_role in required_roles
    
    def create_user_token_data(self, user: User) -> Dict[str, Any]:
        """创建用户令牌数据"""
        return {
            "sub": str(user.id),
            "openid": user.openid,
            "role": user.role.value,
            "nickname": user.nickname,
            "vip_type": user.vip_type.value
        }


# 全局认证管理器实例
auth_manager = AuthManager()


async def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """获取当前用户令牌信息"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = auth_manager.verify_token(token)
        
        if payload is None:
            raise credentials_exception
        
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        return payload
    except Exception as e:
        logger.error(f"获取当前用户失败: {e}")
        raise credentials_exception


async def get_current_user(token_data: Dict[str, Any] = Depends(get_current_user_token)) -> Dict[str, Any]:
    """获取当前用户信息"""
    return {
        "id": int(token_data["sub"]),
        "openid": token_data["openid"],
        "role": token_data["role"],
        "nickname": token_data.get("nickname"),
        "vip_type": token_data.get("vip_type")
    }


def require_roles(allowed_roles: list[UserRole]):
    """要求特定角色的装饰器"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = UserRole(current_user["role"])
        if not auth_manager.check_permission(user_role, allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker


def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)):
    """要求管理员权限"""
    return require_roles([UserRole.ADMIN])(current_user)


def require_teacher(current_user: Dict[str, Any] = Depends(get_current_user)):
    """要求教师权限"""
    return require_roles([UserRole.TEACHER, UserRole.ADMIN])(current_user)


def require_parent_or_teacher(current_user: Dict[str, Any] = Depends(get_current_user)):
    """要求家长或教师权限"""
    return require_roles([UserRole.PARENT, UserRole.TEACHER, UserRole.ADMIN])(current_user)


class PermissionChecker:
    """权限检查器"""
    
    @staticmethod
    def can_view_homework(current_user: Dict[str, Any], homework_user_id: int) -> bool:
        """检查是否可以查看作业"""
        user_role = UserRole(current_user["role"])
        user_id = current_user["id"]
        
        # 管理员可以查看所有作业
        if user_role == UserRole.ADMIN:
            return True
        
        # 用户只能查看自己的作业
        if user_role in [UserRole.PARENT, UserRole.STUDENT] and user_id == homework_user_id:
            return True
        
        # 教师可以查看学生的作业（这里可能需要额外的逻辑检查师生关系）
        if user_role == UserRole.TEACHER:
            return True  # 简化处理，实际应该检查师生关系
        
        return False
    
    @staticmethod
    def can_modify_user(current_user: Dict[str, Any], target_user_id: int) -> bool:
        """检查是否可以修改用户信息"""
        user_role = UserRole(current_user["role"])
        user_id = current_user["id"]
        
        # 管理员可以修改所有用户
        if user_role == UserRole.ADMIN:
            return True
        
        # 用户只能修改自己的信息
        if user_id == target_user_id:
            return True
        
        return False
    
    @staticmethod
    def can_access_analysis(current_user: Dict[str, Any], analysis_user_id: int) -> bool:
        """检查是否可以访问分析数据"""
        user_role = UserRole(current_user["role"])
        user_id = current_user["id"]
        
        # 管理员可以访问所有分析数据
        if user_role == UserRole.ADMIN:
            return True
        
        # 用户只能访问自己的分析数据
        if user_role in [UserRole.PARENT, UserRole.STUDENT] and user_id == analysis_user_id:
            return True
        
        # 教师可以访问学生的分析数据
        if user_role == UserRole.TEACHER:
            return True  # 简化处理，实际应该检查师生关系
        
        return False


# 权限检查器实例
permission_checker = PermissionChecker()


class RateLimitChecker:
    """速率限制检查器"""
    
    @staticmethod
    def check_homework_limit(user: Dict[str, Any]) -> bool:
        """检查作业提交限制"""
        from .cache import get_daily_usage, cache_manager
        
        user_id = user["id"]
        vip_type = user.get("vip_type", "free")
        
        # 获取每日使用次数
        daily_usage = get_daily_usage(user_id)
        
        # 根据VIP类型设置限制
        if vip_type == "free":
            daily_limit = 3
        elif vip_type == "basic":
            daily_limit = 50
        else:  # premium, family
            return True  # 无限制
        
        return daily_usage < daily_limit
    
    @staticmethod
    def check_api_rate_limit(user_id: int, endpoint: str, limit: int = 60, window: int = 60) -> bool:
        """检查API速率限制"""
        from .cache import rate_limiter
        
        key = f"rate_limit:{endpoint}:{user_id}"
        return rate_limiter.is_allowed(key, limit, window)


# 速率限制检查器实例
rate_limit_checker = RateLimitChecker()


def check_homework_quota(current_user: Dict[str, Any] = Depends(get_current_user)):
    """检查作业配额"""
    if not rate_limit_checker.check_homework_limit(current_user):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="今日配额已用完，请升级VIP或明日再试"
        )
    return current_user


def check_api_rate_limit(endpoint: str, limit: int = 60, window: int = 60):
    """API速率限制装饰器"""
    def rate_limit_checker_dep(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_id = current_user["id"]
        if not rate_limit_checker.check_api_rate_limit(user_id, endpoint, limit, window):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后再试"
            )
        return current_user
    return rate_limit_checker_dep