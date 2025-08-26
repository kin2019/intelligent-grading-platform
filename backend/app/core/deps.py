from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User

# HTTP Bearer Token认证
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    print(f"DEBUG: Received token: {token}")
    
    # 临时测试：直接返回ID=1的用户，跳过token验证 
    if token == "test-token-123":
        print("DEBUG: Using test token bypass")
        # 从数据库获取真实的用户记录
        user = db.query(User).filter(User.id == 1).first()
        if user:
            print(f"DEBUG: Found real user ID=1: {user.nickname}")
            return user
        else:
            print("DEBUG: User ID=1 not found, creating new user")
            # 如果找不到用户，创建一个新的用户记录
            user = User(
                openid="test_user_1",
                unionid="test_user_1",
                nickname="测试用户",
                role="student",
                is_active=True,
                avatar_url=None,
                grade="五年级",
                phone=None,
                email=None,
                is_vip=False,
                vip_expire_time=None,
                daily_quota=5,
                daily_used=0,
                total_used=0,
                settings=None
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
    
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 查询用户，如果不存在则创建模拟用户
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        # 创建模拟用户用于测试
        user = User(
            openid=user_id,
            unionid=f"mock_openid_{user_id}",
            nickname="测试用户",
            role="student",
            is_active=True,
            is_vip=False,
            daily_quota=5,
            daily_used=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="用户账号已被禁用"
        )
    return current_user

def get_db_session() -> Generator:
    """获取数据库会话（同步版本，用于依赖注入）"""
    return Depends(get_db)