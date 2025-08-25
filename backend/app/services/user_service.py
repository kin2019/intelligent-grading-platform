from typing import Optional, List
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import create_access_token, verify_password, get_password_hash
import json

class UserService:
    """用户服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(
        self,
        openid: str,
        unionid: Optional[str] = None,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None,
        role: str = "student",
        grade: Optional[str] = None
    ) -> User:
        """创建新用户"""
        # 检查用户是否已存在
        existing_user = await self.get_user_by_openid(openid)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="用户已存在"
            )
        
        user = User(
            openid=openid,
            unionid=unionid,
            nickname=nickname or f"用户{openid[-6:]}",
            avatar_url=avatar_url,
            role=role,
            grade=grade,
            daily_quota=3,
            daily_used=0,
            last_quota_reset=date.today()
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_openid(self, openid: str) -> Optional[User]:
        """根据OpenID获取用户"""
        result = await self.db.execute(
            select(User).where(User.openid == openid, User.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def update_user_info(
        self,
        user_id: int,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        grade: Optional[str] = None
    ) -> User:
        """更新用户信息"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        update_data = {}
        if nickname is not None:
            update_data["nickname"] = nickname
        if avatar_url is not None:
            update_data["avatar_url"] = avatar_url
        if phone is not None:
            update_data["phone"] = phone
        if email is not None:
            update_data["email"] = email
        if grade is not None:
            update_data["grade"] = grade
        
        if update_data:
            await self.db.execute(
                update(User).where(User.id == user_id).values(**update_data)
            )
            await self.db.commit()
            await self.db.refresh(user)
        
        return user
    
    async def update_last_login(self, user_id: int):
        """更新最后登录时间"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.utcnow())
        )
        await self.db.commit()
    
    async def check_and_reset_daily_quota(self, user: User) -> User:
        """检查并重置每日额度"""
        today = date.today()
        if user.last_quota_reset != today:
            await self.db.execute(
                update(User)
                .where(User.id == user.id)
                .values(
                    daily_used=0,
                    last_quota_reset=today
                )
            )
            await self.db.commit()
            user.daily_used = 0
            user.last_quota_reset = today
        
        return user
    
    async def consume_quota(self, user_id: int) -> bool:
        """消费用户额度"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        # 检查并重置额度
        user = await self.check_and_reset_daily_quota(user)
        
        # 检查是否可以使用服务
        if not user.can_use_service():
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="今日额度已用完，请升级VIP或明日再试"
            )
        
        # 消费额度
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                daily_used=User.daily_used + 1,
                total_used=User.total_used + 1
            )
        )
        await self.db.commit()
        
        return True
    
    async def upgrade_to_vip(self, user_id: int, days: int = 30) -> User:
        """升级为VIP用户"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 计算VIP过期时间
        if user.is_vip and user.vip_expire_time and user.vip_expire_time > datetime.utcnow():
            # 如果已是VIP且未过期，则延长时间
            vip_expire_time = user.vip_expire_time + timedelta(days=days)
        else:
            # 新VIP或已过期，从现在开始计算
            vip_expire_time = datetime.utcnow() + timedelta(days=days)
        
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                is_vip=True,
                vip_expire_time=vip_expire_time
            )
        )
        await self.db.commit()
        
        await self.db.refresh(user)
        return user
    
    async def check_vip_status(self, user: User) -> User:
        """检查VIP状态"""
        if user.is_vip and user.vip_expire_time:
            if user.vip_expire_time <= datetime.utcnow():
                # VIP已过期
                await self.db.execute(
                    update(User)
                    .where(User.id == user.id)
                    .values(is_vip=False)
                )
                await self.db.commit()
                user.is_vip = False
        
        return user
    
    async def get_user_settings(self, user_id: int) -> dict:
        """获取用户设置"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if user.settings:
            try:
                return json.loads(user.settings)
            except json.JSONDecodeError:
                return {}
        
        return {}
    
    async def update_user_settings(self, user_id: int, settings: dict) -> dict:
        """更新用户设置"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        settings_json = json.dumps(settings, ensure_ascii=False)
        
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(settings=settings_json)
        )
        await self.db.commit()
        
        return settings
    
    async def deactivate_user(self, user_id: int):
        """停用用户"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        await self.db.commit()
    
    async def get_users_by_role(self, role: str, limit: int = 100, offset: int = 0) -> List[User]:
        """根据角色获取用户列表"""
        result = await self.db.execute(
            select(User)
            .where(User.role == role, User.is_active == True)
            .limit(limit)
            .offset(offset)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()