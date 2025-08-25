from typing import Any, Dict
import httpx
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()
security = HTTPBearer()

class WeChatLoginRequest(BaseModel):
    code: str = Field(..., description="微信授权码")
    role: str = Field(default="student", description="用户角色：student(学生), parent(家长), teacher(教师)")

class WeChatLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UpdateProfileRequest(BaseModel):
    nickname: str = Field(None, max_length=50, description="用户昵称")
    avatar_url: str = Field(None, max_length=500, description="头像URL")
    gender: int = Field(None, ge=0, le=2, description="性别：0-未知，1-男，2-女")
    city: str = Field(None, max_length=50, description="城市")

async def get_wechat_user_info(code: str) -> Dict[str, Any]:
    """
    通过微信code获取用户信息
    """
    # 如果是开发环境或者没有配置微信，返回模拟数据
    if (settings.ENVIRONMENT == "development" or 
        not settings.WECHAT_APP_ID or 
        not settings.WECHAT_APP_SECRET):
        
        return {
            "openid": f"test_openid_{code}",
            "session_key": f"test_session_{code}",
            "nickname": "测试用户",
            "avatar_url": "https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJI2FqVk7Am7Syh5hSK2o7W7XtGTpFaJCt7gNgvLfvHGGFJ9VJoJVy0J3LqvoGFqv5J2o7W7X/132"
        }
    
    # 生产环境：调用微信API
    try:
        # 第一步：通过code获取session_key和openid
        auth_url = "https://api.weixin.qq.com/sns/jscode2session"
        auth_params = {
            "appid": settings.WECHAT_APP_ID,
            "secret": settings.WECHAT_APP_SECRET,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            auth_response = await client.get(auth_url, params=auth_params)
            auth_data = auth_response.json()
            
            if "errcode" in auth_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"微信授权失败: {auth_data.get('errmsg', '未知错误')}"
                )
            
            return {
                "openid": auth_data["openid"],
                "session_key": auth_data.get("session_key"),
                "nickname": f"微信用户_{auth_data['openid'][-6:]}",  # 默认昵称
                "avatar_url": "https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJI2FqVk7Am7Syh5hSK2o7W7XtGTpFaJCt7gNgvLfvHGGFJ9VJoJVy0J3LqvoGFqv5J2o7W7X/132"  # 默认头像
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"微信API调用失败: {str(e)}"
        )

async def find_or_create_user(db: Session, wechat_user: Dict[str, Any], role: str) -> User:
    """
    查找或创建用户
    """
    # 先查找是否已存在用户
    existing_user = db.query(User).filter(User.openid == wechat_user["openid"]).first()
    
    if existing_user:
        # 用户已存在，更新最后登录时间
        existing_user.last_login_at = datetime.utcnow()
        # 如果角色不同，更新角色
        if existing_user.role != role:
            existing_user.role = role
        db.commit()
        return existing_user
    
    # 创建新用户
    new_user = User(
        openid=wechat_user["openid"],
        nickname=wechat_user["nickname"],
        avatar_url=wechat_user["avatar_url"],
        role=role,
        created_at=datetime.utcnow(),
        last_login_at=datetime.utcnow(),
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/wechat/login", response_model=WeChatLoginResponse, summary="微信小程序登录")
async def wechat_login(
    request: WeChatLoginRequest,
    db: Session = Depends(get_db)
):
    """
    微信小程序登录接口
    
    - **code**: 微信小程序调用wx.login()获得的code
    - **role**: 用户角色（student/parent/teacher）
    
    返回访问令牌和用户信息
    """
    try:
        # 获取微信用户信息
        wechat_user = await get_wechat_user_info(request.code)
        
        # 查找或创建用户
        user = await find_or_create_user(db, wechat_user, request.role)
        
        # 创建访问令牌
        from app.core.security import create_access_token
        access_token = create_access_token(str(user.id))
        
        # 更新最后登录时间
        from datetime import datetime
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "openid": user.openid,
                "nickname": user.nickname,
                "avatar_url": user.avatar_url,
                "role": user.role,
                "grade": user.grade,
                "created_at": user.created_at.isoformat(),
                "is_vip": False
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"微信登录失败: {str(e)}"
        )

@router.post("/refresh", summary="刷新访问令牌")
def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌
    
    需要有效的访问令牌才能调用此接口
    """
    from app.core.security import create_access_token
    new_token = create_access_token({"sub": str(current_user.id)})
    
    return {
        "access_token": new_token,
        "token_type": "bearer"
    }

@router.put("/profile", summary="更新用户资料")
def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户的资料信息
    
    - **nickname**: 用户昵称
    - **avatar_url**: 头像URL地址
    - **gender**: 性别（0-未知，1-男，2-女）
    - **city**: 所在城市
    """
    # 简化版更新逻辑
    if request.nickname:
        current_user.nickname = request.nickname
    if request.avatar_url:
        current_user.avatar_url = request.avatar_url
    if request.gender is not None:
        current_user.gender = request.gender
    if request.city:
        current_user.city = request.city
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "nickname": current_user.nickname,
        "avatar_url": current_user.avatar_url,
        "role": current_user.role,
        "grade": current_user.grade,
        "updated_at": current_user.updated_at.isoformat()
    }

@router.get("/me", summary="获取当前用户信息")
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户的详细信息
    """
    return {
        "id": current_user.id,
        "openid": getattr(current_user, 'openid', None),
        "nickname": current_user.nickname,
        "avatar_url": getattr(current_user, 'avatar_url', None),
        "phone": getattr(current_user, 'phone', None),
        "email": getattr(current_user, 'email', None),
        "role": getattr(current_user, 'role', 'student'),
        "grade": getattr(current_user, 'grade', None),
        "created_at": current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else None,
        "last_login_at": getattr(current_user, 'last_login_at', None),
        "is_vip": False,
        "daily_quota": 5,
        "daily_used": 0
    }

@router.get("/quota", summary="获取用户额度信息")
def get_quota_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的使用额度信息
    
    包括VIP状态、每日额度、已使用次数等
    """
    return {
        "is_vip": False,
        "vip_type": "free",
        "daily_quota": 5,
        "daily_used": 0,
        "monthly_quota": 150,
        "monthly_used": 0,
        "quota_reset_time": "明天 00:00"
    }