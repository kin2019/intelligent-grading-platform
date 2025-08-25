import httpx
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.services.user_service import UserService

class AuthService:
    """认证服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)
    
    async def wechat_login(self, code: str) -> Dict[str, Any]:
        """微信小程序登录"""
        # 调用微信API获取session_key和openid
        wechat_data = await self._get_wechat_session(code)
        
        if "errcode" in wechat_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"微信登录失败: {wechat_data.get('errmsg', '未知错误')}"
            )
        
        openid = wechat_data.get("openid")
        unionid = wechat_data.get("unionid")
        session_key = wechat_data.get("session_key")
        
        if not openid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法获取用户OpenID"
            )
        
        # 查找或创建用户
        user = await self.user_service.get_user_by_openid(openid)
        
        if not user:
            # 创建新用户
            user = await self.user_service.create_user(
                openid=openid,
                unionid=unionid
            )
        else:
            # 更新最后登录时间
            await self.user_service.update_last_login(user.id)
            
            # 检查VIP状态
            user = await self.user_service.check_vip_status(user)
            
            # 检查并重置每日额度
            user = await self.user_service.check_and_reset_daily_quota(user)
        
        # 生成JWT令牌
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "openid": openid,
                "role": user.role
            }
        )
        
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
                "is_vip": user.is_vip,
                "vip_expire_time": user.vip_expire_time.isoformat() if user.vip_expire_time else None,
                "daily_quota": user.daily_quota,
                "daily_used": user.daily_used,
                "can_use_service": user.can_use_service()
            }
        }
    
    async def _get_wechat_session(self, code: str) -> Dict[str, Any]:
        """获取微信session信息"""
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": settings.WECHAT_APP_ID,
            "secret": settings.WECHAT_APP_SECRET,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail="微信API请求超时"
                )
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"微信API请求失败: {str(e)}"
                )
    
    async def update_user_profile(
        self,
        user_id: int,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None,
        gender: Optional[int] = None,
        city: Optional[str] = None
    ) -> User:
        """更新用户资料"""
        update_data = {}
        if nickname:
            update_data["nickname"] = nickname
        if avatar_url:
            update_data["avatar_url"] = avatar_url
        
        if not update_data:
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            return user
        
        return await self.user_service.update_user_info(
            user_id=user_id,
            **update_data
        )
    
    async def refresh_token(self, user_id: int) -> str:
        """刷新访问令牌"""
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用"
            )
        
        # 生成新令牌
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "openid": user.openid,
                "role": user.role
            }
        )
        
        return access_token
    
    async def check_permission(self, user: User, permission: str) -> bool:
        """检查用户权限"""
        # 管理员拥有所有权限
        if user.is_admin:
            return True
        
        # 根据角色检查权限
        role_permissions = {
            "student": [
                "homework:submit",
                "homework:view_own",
                "profile:update_own"
            ],
            "parent": [
                "homework:submit",
                "homework:view_own",
                "homework:view_children",
                "profile:update_own"
            ],
            "teacher": [
                "homework:submit",
                "homework:view_own",
                "homework:view_students",
                "homework:batch_correct",
                "profile:update_own"
            ]
        }
        
        user_permissions = role_permissions.get(user.role, [])
        return permission in user_permissions
    
    async def get_user_quota_info(self, user_id: int) -> Dict[str, Any]:
        """获取用户额度信息"""
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查并重置每日额度
        user = await self.user_service.check_and_reset_daily_quota(user)
        
        # 检查VIP状态
        user = await self.user_service.check_vip_status(user)
        
        return {
            "is_vip": user.is_vip,
            "vip_expire_time": user.vip_expire_time.isoformat() if user.vip_expire_time else None,
            "daily_quota": user.daily_quota,
            "daily_used": user.daily_used,
            "daily_remaining": max(0, user.daily_quota - user.daily_used),
            "can_use_service": user.can_use_service(),
            "total_used": user.total_used
        }