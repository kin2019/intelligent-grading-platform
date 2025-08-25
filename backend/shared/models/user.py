"""
用户相关数据模型
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import String, Boolean, DateTime, Text, Integer, ForeignKey, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseTable, BaseSchema


class UserRole(str, Enum):
    """用户角色枚举"""
    STUDENT = "student"      # 学生
    PARENT = "parent"        # 家长
    TEACHER = "teacher"      # 教师
    ADMIN = "admin"          # 管理员


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"        # 活跃
    INACTIVE = "inactive"    # 未激活
    SUSPENDED = "suspended"  # 暂停
    BANNED = "banned"        # 封禁


class GradeLevel(str, Enum):
    """年级枚举"""
    GRADE_1 = "grade_1"      # 一年级
    GRADE_2 = "grade_2"      # 二年级
    GRADE_3 = "grade_3"      # 三年级
    GRADE_4 = "grade_4"      # 四年级
    GRADE_5 = "grade_5"      # 五年级
    GRADE_6 = "grade_6"      # 六年级
    GRADE_7 = "grade_7"      # 七年级
    GRADE_8 = "grade_8"      # 八年级
    GRADE_9 = "grade_9"      # 九年级


class VIPType(str, Enum):
    """VIP类型枚举"""
    FREE = "free"            # 免费版
    BASIC = "basic"          # 标准版
    PREMIUM = "premium"      # 专业版
    FAMILY = "family"        # 家庭版


# SQLAlchemy 模型
class User(BaseTable):
    """用户表"""
    __tablename__ = "users"
    
    # 基本信息
    openid: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="微信OpenID")
    nickname: Mapped[Optional[str]] = mapped_column(String(100), comment="昵称")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), comment="头像URL")
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, comment="手机号")
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, comment="邮箱")
    
    # 角色和状态
    role: Mapped[UserRole] = mapped_column(String(20), default=UserRole.PARENT, comment="用户角色")
    status: Mapped[UserStatus] = mapped_column(String(20), default=UserStatus.ACTIVE, comment="用户状态")
    
    # VIP信息
    vip_type: Mapped[VIPType] = mapped_column(String(20), default=VIPType.FREE, comment="VIP类型")
    vip_expire_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="VIP过期时间")
    
    # 配额信息
    daily_quota: Mapped[int] = mapped_column(Integer, default=3, comment="每日配额")
    daily_used: Mapped[int] = mapped_column(Integer, default=0, comment="每日已用")
    last_quota_reset: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="配额重置时间")
    
    # 统计信息
    total_corrections: Mapped[int] = mapped_column(Integer, default=0, comment="总批改次数")
    total_questions: Mapped[int] = mapped_column(Integer, default=0, comment="总题目数")
    accuracy_rate: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), comment="正确率")
    
    # 关联关系
    students: Mapped[List["Student"]] = relationship("Student", back_populates="parent")
    homework: Mapped[List["Homework"]] = relationship("Homework", back_populates="user")
    error_questions: Mapped[List["ErrorQuestion"]] = relationship("ErrorQuestion", back_populates="user")


class Student(BaseTable):
    """学生表"""
    __tablename__ = "students"
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(50), comment="学生姓名")
    grade: Mapped[GradeLevel] = mapped_column(String(20), comment="年级")
    school: Mapped[Optional[str]] = mapped_column(String(100), comment="学校名称")
    class_name: Mapped[Optional[str]] = mapped_column(String(50), comment="班级")
    
    # 关联信息
    parent_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="家长ID")
    teacher_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teachers.id"), comment="教师ID")
    
    # 学习统计
    total_homework: Mapped[int] = mapped_column(Integer, default=0, comment="总作业数")
    completed_homework: Mapped[int] = mapped_column(Integer, default=0, comment="完成作业数")
    average_score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), comment="平均分数")
    
    # 关联关系
    parent: Mapped["User"] = relationship("User", back_populates="students")
    teacher: Mapped[Optional["Teacher"]] = relationship("Teacher", back_populates="students")
    homework: Mapped[List["Homework"]] = relationship("Homework", back_populates="student")


class Teacher(BaseTable):
    """教师表"""
    __tablename__ = "teachers"
    
    # 基本信息
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, comment="用户ID")
    real_name: Mapped[str] = mapped_column(String(50), comment="真实姓名")
    id_card: Mapped[str] = mapped_column(String(18), unique=True, comment="身份证号")
    teaching_subjects: Mapped[str] = mapped_column(Text, comment="教学科目JSON")
    teaching_grades: Mapped[str] = mapped_column(Text, comment="教学年级JSON")
    qualification_cert: Mapped[Optional[str]] = mapped_column(String(255), comment="教师资格证")
    
    # 认证信息
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否认证")
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="认证时间")
    
    # 教学统计
    total_students: Mapped[int] = mapped_column(Integer, default=0, comment="学生总数")
    total_corrections: Mapped[int] = mapped_column(Integer, default=0, comment="批改总数")
    rating: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2), comment="评分")
    
    # 收入统计
    total_income: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0, comment="总收入")
    withdraw_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0, comment="已提现金额")
    
    # 关联关系
    user: Mapped["User"] = relationship("User")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="teacher")


# Pydantic 模型
class UserBase(BaseSchema):
    """用户基础模型"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class UserCreate(UserBase):
    """创建用户模型"""
    openid: str
    role: UserRole = UserRole.PARENT


class UserUpdate(BaseSchema):
    """更新用户模型"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    openid: str
    role: UserRole
    status: UserStatus
    vip_type: VIPType
    vip_expire_time: Optional[datetime] = None
    daily_quota: int
    daily_used: int
    total_corrections: int
    accuracy_rate: Optional[float] = None
    created_at: datetime


class StudentBase(BaseSchema):
    """学生基础模型"""
    name: str
    grade: GradeLevel
    school: Optional[str] = None
    class_name: Optional[str] = None


class StudentCreate(StudentBase):
    """创建学生模型"""
    parent_id: int


class StudentUpdate(BaseSchema):
    """更新学生模型"""
    name: Optional[str] = None
    grade: Optional[GradeLevel] = None
    school: Optional[str] = None
    class_name: Optional[str] = None
    teacher_id: Optional[int] = None


class StudentResponse(StudentBase):
    """学生响应模型"""
    id: int
    parent_id: int
    teacher_id: Optional[int] = None
    total_homework: int
    completed_homework: int
    average_score: Optional[float] = None
    created_at: datetime


class TeacherBase(BaseSchema):
    """教师基础模型"""
    real_name: str
    id_card: str
    teaching_subjects: List[str]
    teaching_grades: List[GradeLevel]
    qualification_cert: Optional[str] = None


class TeacherCreate(TeacherBase):
    """创建教师模型"""
    user_id: int


class TeacherUpdate(BaseSchema):
    """更新教师模型"""
    real_name: Optional[str] = None
    teaching_subjects: Optional[List[str]] = None
    teaching_grades: Optional[List[GradeLevel]] = None
    qualification_cert: Optional[str] = None


class TeacherResponse(TeacherBase):
    """教师响应模型"""
    id: int
    user_id: int
    is_verified: bool
    verified_at: Optional[datetime] = None
    total_students: int
    total_corrections: int
    rating: Optional[float] = None
    total_income: float
    created_at: datetime


class LoginRequest(BaseSchema):
    """登录请求模型"""
    code: str  # 微信登录code


class LoginResponse(BaseSchema):
    """登录响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse