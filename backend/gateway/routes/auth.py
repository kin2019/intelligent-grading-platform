"""
认证路由
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from ...shared.models.user import LoginRequest, LoginResponse, UserCreate, UserResponse
from ...shared.models.base import ResponseModel
from ...shared.utils.auth import auth_manager
from ...shared.utils.database import get_db
from ...shared.utils.cache import cache_user_data, get_user_data, increment_daily_usage
from ...services.user_service.repositories.user_repository import UserRepository

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """微信小程序登录"""
    try:
        # 获取微信会话信息
        wechat_session = await auth_manager.get_wechat_session(request.code)
        if not wechat_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="微信登录失败，请检查code是否有效"
            )
        
        openid = wechat_session["openid"]
        session_key = wechat_session.get("session_key")
        
        # 查找或创建用户
        user_repo = UserRepository()
        user = user_repo.get_by_openid(db, openid)
        
        if not user:
            # 创建新用户
            user_data = UserCreate(openid=openid)
            user = user_repo.create(db, **user_data.model_dump())
        
        # 创建访问令牌
        token_data = auth_manager.create_user_token_data(user)
        access_token = auth_manager.create_access_token(token_data)
        
        # 缓存用户数据
        user_cache_data = {
            "id": user.id,
            "openid": user.openid,
            "nickname": user.nickname,
            "role": user.role.value,
            "vip_type": user.vip_type.value,
            "session_key": session_key  # 用于后续的微信API调用
        }
        cache_user_data(user.id, user_cache_data)
        
        # 准备响应
        user_response = UserResponse.model_validate(user)
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_manager.access_token_expire_minutes * 60,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(current_user: dict = Depends(auth_manager.get_current_user_token)):
    """刷新访问令牌"""
    try:
        # 从缓存获取用户数据
        user_data = get_user_data(int(current_user["sub"]))
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户信息已过期，请重新登录"
            )
        
        # 创建新的访问令牌
        token_data = {
            "sub": current_user["sub"],
            "openid": current_user["openid"],
            "role": current_user["role"],
            "nickname": current_user.get("nickname"),
            "vip_type": current_user.get("vip_type")
        }
        access_token = auth_manager.create_access_token(token_data)
        
        # 构建用户响应
        user_response = UserResponse(
            id=int(current_user["sub"]),
            openid=current_user["openid"],
            role=current_user["role"],
            nickname=current_user.get("nickname"),
            vip_type=current_user.get("vip_type"),
            created_at=datetime.now()  # 这里应该从数据库获取真实的创建时间
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_manager.access_token_expire_minutes * 60,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新令牌失败: {str(e)}"
        )


@router.post("/logout", response_model=ResponseModel)
async def logout(current_user: dict = Depends(auth_manager.get_current_user_token)):
    """用户登出"""
    try:
        user_id = int(current_user["sub"])
        
        # 清除用户缓存数据
        from ...shared.utils.cache import clear_user_cache
        clear_user_cache(user_id)
        
        return ResponseModel(
            code=200,
            message="登出成功"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(auth_manager.get_current_user_token), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    try:
        user_id = int(current_user["sub"])
        
        # 从数据库获取最新用户信息
        user_repo = UserRepository()
        user = user_repo.get_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )


@router.get("/quota", response_model=ResponseModel)
async def get_user_quota(current_user: dict = Depends(auth_manager.get_current_user_token), db: Session = Depends(get_db)):
    """获取用户配额信息"""
    try:
        user_id = int(current_user["sub"])
        
        # 从数据库获取用户信息
        user_repo = UserRepository()
        user = user_repo.get_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 获取今日使用次数
        from ...shared.utils.cache import get_daily_usage
        daily_used = get_daily_usage(user_id)
        
        # 计算剩余配额
        if user.vip_type.value == "free":
            daily_limit = 3
        elif user.vip_type.value == "basic":
            daily_limit = 50
        else:  # premium, family
            daily_limit = -1  # 无限制
        
        remaining = max(0, daily_limit - daily_used) if daily_limit > 0 else -1
        
        quota_info = {
            "daily_limit": daily_limit,
            "daily_used": daily_used,
            "remaining": remaining,
            "vip_type": user.vip_type.value,
            "vip_expire_time": user.vip_expire_time.isoformat() if user.vip_expire_time else None,
            "unlimited": daily_limit == -1
        }
        
        return ResponseModel(
            code=200,
            message="获取配额信息成功",
            data=quota_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取配额信息失败: {str(e)}"
        )


@router.post("/check-quota", response_model=ResponseModel)
async def check_and_consume_quota(current_user: dict = Depends(auth_manager.get_current_user_token), db: Session = Depends(get_db)):
    """检查并消费配额"""
    try:
        user_id = int(current_user["sub"])
        
        # 从数据库获取用户信息
        user_repo = UserRepository()
        user = user_repo.get_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查配额
        if user.vip_type.value == "free":
            daily_limit = 3
        elif user.vip_type.value == "basic":
            daily_limit = 50
        else:  # premium, family
            # VIP用户无限制
            increment_daily_usage(user_id)
            return ResponseModel(
                code=200,
                message="配额检查通过",
                data={"consumed": True, "unlimited": True}
            )
        
        # 获取今日使用次数
        from ...shared.utils.cache import get_daily_usage
        daily_used = get_daily_usage(user_id)
        
        if daily_used >= daily_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"今日配额已用完，当前限制: {daily_limit}次/天"
            )
        
        # 消费配额
        new_usage = increment_daily_usage(user_id)
        
        return ResponseModel(
            code=200,
            message="配额检查通过",
            data={
                "consumed": True,
                "daily_used": new_usage,
                "daily_limit": daily_limit,
                "remaining": max(0, daily_limit - new_usage),
                "unlimited": False
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"配额检查失败: {str(e)}"
        )