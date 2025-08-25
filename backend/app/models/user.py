from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from typing import Optional

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(100), unique=True, index=True, nullable=False, comment="微信OpenID")
    unionid = Column(String(100), index=True, nullable=True, comment="微信UnionID") 
    nickname = Column(String(100), nullable=True, comment="用户昵称")
    avatar_url = Column(String(500), nullable=True, comment="头像URL")
    phone = Column(String(20), index=True, nullable=True, comment="手机号")
    email = Column(String(100), index=True, nullable=True, comment="邮箱")
    
    # 角色和权限
    role = Column(String(20), default="student", nullable=False, comment="用户角色: student/parent/teacher/admin")
    grade = Column(String(20), nullable=True, comment="年级")
    
    # 会员状态
    is_vip = Column(Boolean, default=False, comment="是否VIP用户")
    vip_expire_time = Column(DateTime, nullable=True, comment="VIP过期时间")
    
    # 使用额度
    daily_quota = Column(Integer, default=3, comment="每日免费额度")
    daily_used = Column(Integer, default=0, comment="今日已使用次数")
    last_quota_reset = Column(DateTime, default=func.current_date(), comment="上次额度重置时间")
    total_used = Column(Integer, default=0, comment="总使用次数")
    
    # 状态字段
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    
    # 扩展信息
    settings = Column(Text, nullable=True, comment="用户设置JSON")
    
    # 关联关系
    study_plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname}, role={self.role})>"
    
    @property
    def is_student(self) -> bool:
        """是否学生用户"""
        return self.role == "student"
    
    @property 
    def is_parent(self) -> bool:
        """是否家长用户"""
        return self.role == "parent"
    
    @property
    def is_teacher(self) -> bool:
        """是否教师用户"""  
        return self.role == "teacher"
    
    @property
    def is_admin(self) -> bool:
        """是否管理员用户"""
        return self.role == "admin"
    
    def can_use_service(self) -> bool:
        """检查是否可以使用服务"""
        if self.is_vip:
            return True
        return self.daily_used < self.daily_quota
    
    def reset_daily_quota(self):
        """重置每日额度"""
        today = datetime.now().date()
        if self.last_quota_reset != today:
            self.daily_used = 0
            self.last_quota_reset = today