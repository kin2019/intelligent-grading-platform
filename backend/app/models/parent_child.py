from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum

class InviteStatus(str, enum.Enum):
    """邀请状态枚举"""
    PENDING = "pending"      # 待接受
    ACCEPTED = "accepted"    # 已接受
    REJECTED = "rejected"    # 已拒绝
    EXPIRED = "expired"      # 已过期

class ParentChild(Base):
    """家长-孩子关联表"""
    __tablename__ = "parent_child"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联用户ID
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="家长用户ID")
    child_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="孩子用户ID")
    
    # 关联信息
    relationship_type = Column(String(20), default="parent", comment="关系类型: parent/guardian")
    nickname = Column(String(50), nullable=True, comment="家长给孩子设置的昵称")
    school = Column(String(100), nullable=True, comment="学校名称")
    class_name = Column(String(50), nullable=True, comment="班级名称")
    
    # 状态和权限
    is_active = Column(Boolean, default=True, comment="关联是否激活")
    can_view_homework = Column(Boolean, default=True, comment="可以查看作业")
    can_view_reports = Column(Boolean, default=True, comment="可以查看报告")
    can_set_limits = Column(Boolean, default=True, comment="可以设置学习限制")
    
    # 学习设置（家长为孩子设置的限制）
    daily_homework_limit = Column(Integer, default=10, comment="每日作业批改次数限制")
    daily_time_limit = Column(Integer, default=120, comment="每日学习时间限制（分钟）")
    bedtime_reminder = Column(String(5), nullable=True, comment="睡觉提醒时间 HH:MM")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="关联创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 外键关联
    parent = relationship("User", foreign_keys=[parent_id], backref="children_relations")
    child = relationship("User", foreign_keys=[child_id], backref="parent_relations")
    
    # 唯一约束：一个家长和一个孩子只能有一个关联记录
    __table_args__ = (
        {"comment": "家长-孩子关联表"}
    )

class BindInvite(Base):
    """绑定邀请表"""
    __tablename__ = "bind_invites"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 邀请信息
    invite_code = Column(String(32), unique=True, index=True, nullable=False, comment="邀请码")
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="邀请人用户ID")
    inviter_type = Column(String(10), nullable=False, comment="邀请人类型: parent/child")
    
    # 被邀请人信息（可选，如果通过手机号邀请）
    invitee_phone = Column(String(20), nullable=True, comment="被邀请人手机号")
    invitee_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="被邀请人用户ID（接受邀请后填入）")
    
    # 邀请内容
    invite_message = Column(Text, nullable=True, comment="邀请留言")
    relationship_type = Column(String(20), default="parent", comment="关系类型")
    
    # 状态和时间
    status = Column(Enum(InviteStatus), default=InviteStatus.PENDING, comment="邀请状态")
    expires_at = Column(DateTime, nullable=False, comment="过期时间")
    accepted_at = Column(DateTime, nullable=True, comment="接受时间")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 外键关联
    inviter = relationship("User", foreign_keys=[inviter_id], backref="sent_invites")
    invitee = relationship("User", foreign_keys=[invitee_id], backref="received_invites")
    
    __table_args__ = (
        {"comment": "绑定邀请表"}
    )
    
    def is_expired(self) -> bool:
        """检查邀请是否已过期"""
        return datetime.now() > self.expires_at
        
    def can_accept(self) -> bool:
        """检查邀请是否可以接受"""
        return self.status == InviteStatus.PENDING and not self.is_expired()