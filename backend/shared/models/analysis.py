"""
学情分析相关数据模型
"""
from datetime import datetime, date
from enum import Enum
from typing import Any, Dict, List, Optional
from sqlalchemy import String, Boolean, DateTime, Text, Integer, ForeignKey, DECIMAL, JSON, Date
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseTable, BaseSchema
from .homework import Subject


class AnalysisType(str, Enum):
    """分析类型枚举"""
    DAILY = "daily"              # 日报
    WEEKLY = "weekly"            # 周报
    MONTHLY = "monthly"          # 月报
    SEMESTER = "semester"        # 学期报告
    ANNUAL = "annual"            # 年度报告


class PerformanceTrend(str, Enum):
    """表现趋势枚举"""
    IMPROVING = "improving"      # 进步
    STABLE = "stable"           # 稳定
    DECLINING = "declining"     # 下降


class LearningStyle(str, Enum):
    """学习风格枚举"""
    VISUAL = "visual"           # 视觉型
    AUDITORY = "auditory"       # 听觉型
    KINESTHETIC = "kinesthetic" # 动觉型
    MIXED = "mixed"             # 混合型


class RecommendationType(str, Enum):
    """推荐类型枚举"""
    EXERCISE = "exercise"       # 练习推荐
    KNOWLEDGE = "knowledge"     # 知识点推荐
    STUDY_PLAN = "study_plan"   # 学习计划推荐
    REVIEW = "review"           # 复习推荐


# SQLAlchemy 模型
class LearningAnalysis(BaseTable):
    """学习分析表"""
    __tablename__ = "learning_analysis"
    
    # 基本信息
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="用户ID")
    student_id: Mapped[Optional[int]] = mapped_column(ForeignKey("students.id"), comment="学生ID")
    analysis_type: Mapped[AnalysisType] = mapped_column(String(20), comment="分析类型")
    
    # 时间范围
    start_date: Mapped[date] = mapped_column(Date, comment="开始日期")
    end_date: Mapped[date] = mapped_column(Date, comment="结束日期")
    
    # 学科信息
    subject: Mapped[Optional[Subject]] = mapped_column(String(20), comment="学科")
    
    # 分析结果
    analysis_data: Mapped[Dict[str, Any]] = mapped_column(JSON, comment="分析数据")
    summary: Mapped[str] = mapped_column(Text, comment="分析摘要")
    insights: Mapped[List[str]] = mapped_column(JSON, comment="洞察要点")
    recommendations: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, comment="推荐建议")
    
    # 状态信息
    is_auto_generated: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否自动生成")
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment="生成时间")


class PerformanceMetrics(BaseTable):
    """表现指标表"""
    __tablename__ = "performance_metrics"
    
    # 基本信息
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="用户ID")
    subject: Mapped[Subject] = mapped_column(String(20), comment="学科")
    date: Mapped[date] = mapped_column(Date, comment="日期")
    
    # 基础指标
    total_exercises: Mapped[int] = mapped_column(Integer, default=0, comment="总练习数")
    correct_exercises: Mapped[int] = mapped_column(Integer, default=0, comment="正确练习数")
    accuracy_rate: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.0, comment="正确率")
    average_score: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.0, comment="平均分")
    
    # 时间指标
    study_duration: Mapped[int] = mapped_column(Integer, default=0, comment="学习时长(分钟)")
    average_response_time: Mapped[float] = mapped_column(DECIMAL(6, 2), default=0.0, comment="平均响应时间(秒)")
    
    # 进度指标
    completed_knowledge_points: Mapped[int] = mapped_column(Integer, default=0, comment="完成知识点数")
    mastered_knowledge_points: Mapped[int] = mapped_column(Integer, default=0, comment="掌握知识点数")
    progress_percentage: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.0, comment="进度百分比")
    
    # 趋势指标
    performance_trend: Mapped[PerformanceTrend] = mapped_column(String(20), comment="表现趋势")
    improvement_rate: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.0, comment="改进率")


class LearningBehavior(BaseTable):
    """学习行为表"""
    __tablename__ = "learning_behavior"
    
    # 基本信息
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="用户ID")
    session_id: Mapped[str] = mapped_column(String(100), comment="会话ID")
    
    # 行为信息
    action_type: Mapped[str] = mapped_column(String(50), comment="行为类型")
    subject: Mapped[Optional[Subject]] = mapped_column(String(20), comment="学科")
    content_id: Mapped[Optional[int]] = mapped_column(Integer, comment="内容ID")
    
    # 时间信息
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment="开始时间")
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="结束时间")
    duration: Mapped[Optional[int]] = mapped_column(Integer, comment="持续时间(秒)")
    
    # 行为数据
    behavior_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, comment="行为数据")
    result: Mapped[Optional[str]] = mapped_column(String(20), comment="行为结果")
    
    # 设备信息
    device_type: Mapped[Optional[str]] = mapped_column(String(20), comment="设备类型")
    platform: Mapped[Optional[str]] = mapped_column(String(20), comment="平台")


class PersonalizedRecommendation(BaseTable):
    """个性化推荐表"""
    __tablename__ = "personalized_recommendations"
    
    # 基本信息
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="用户ID")
    recommendation_type: Mapped[RecommendationType] = mapped_column(String(20), comment="推荐类型")
    
    # 推荐内容
    title: Mapped[str] = mapped_column(String(200), comment="推荐标题")
    description: Mapped[str] = mapped_column(Text, comment="推荐描述")
    content_data: Mapped[Dict[str, Any]] = mapped_column(JSON, comment="推荐内容数据")
    
    # 推荐理由
    reason: Mapped[str] = mapped_column(Text, comment="推荐理由")
    confidence_score: Mapped[float] = mapped_column(DECIMAL(3, 2), comment="置信度分数")
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    is_viewed: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已查看")
    is_accepted: Mapped[Optional[bool]] = mapped_column(Boolean, comment="是否接受")
    viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="查看时间")
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="响应时间")
    
    # 有效期
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="过期时间")


class LearningProfile(BaseTable):
    """学习画像表"""
    __tablename__ = "learning_profiles"
    
    # 基本信息
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, comment="用户ID")
    
    # 学习特征
    learning_style: Mapped[LearningStyle] = mapped_column(String(20), comment="学习风格")
    preferred_subjects: Mapped[List[str]] = mapped_column(JSON, comment="偏好学科")
    weak_subjects: Mapped[List[str]] = mapped_column(JSON, comment="薄弱学科")
    
    # 学习习惯
    preferred_study_time: Mapped[Optional[str]] = mapped_column(String(50), comment="偏好学习时间")
    average_session_duration: Mapped[int] = mapped_column(Integer, default=0, comment="平均学习时长(分钟)")
    study_frequency: Mapped[float] = mapped_column(DECIMAL(3, 2), default=0.0, comment="学习频率(次/天)")
    
    # 能力评估
    overall_ability: Mapped[float] = mapped_column(DECIMAL(3, 2), default=0.0, comment="整体能力评分")
    subject_abilities: Mapped[Dict[str, float]] = mapped_column(JSON, comment="学科能力评分")
    learning_speed: Mapped[float] = mapped_column(DECIMAL(3, 2), default=1.0, comment="学习速度系数")
    
    # 行为特征
    error_patterns: Mapped[Dict[str, Any]] = mapped_column(JSON, comment="错误模式分析")
    progress_patterns: Mapped[Dict[str, Any]] = mapped_column(JSON, comment="进步模式分析")
    engagement_level: Mapped[float] = mapped_column(DECIMAL(3, 2), default=0.0, comment="参与度")
    
    # 更新信息
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment="最后更新时间")
    analysis_count: Mapped[int] = mapped_column(Integer, default=0, comment="分析次数")


# Pydantic 模型
class LearningAnalysisCreate(BaseSchema):
    """创建学习分析模型"""
    user_id: int
    student_id: Optional[int] = None
    analysis_type: AnalysisType
    start_date: date
    end_date: date
    subject: Optional[Subject] = None


class LearningAnalysisResponse(BaseSchema):
    """学习分析响应模型"""
    id: int
    user_id: int
    student_id: Optional[int] = None
    analysis_type: AnalysisType
    start_date: date
    end_date: date
    subject: Optional[Subject] = None
    analysis_data: Dict[str, Any]
    summary: str
    insights: List[str]
    recommendations: List[Dict[str, Any]]
    is_auto_generated: bool
    generated_at: datetime
    created_at: datetime


class PerformanceMetricsResponse(BaseSchema):
    """表现指标响应模型"""
    id: int
    user_id: int
    subject: Subject
    date: date
    total_exercises: int
    correct_exercises: int
    accuracy_rate: float
    average_score: float
    study_duration: int
    average_response_time: float
    completed_knowledge_points: int
    mastered_knowledge_points: int
    progress_percentage: float
    performance_trend: PerformanceTrend
    improvement_rate: float
    created_at: datetime


class LearningBehaviorCreate(BaseSchema):
    """创建学习行为模型"""
    user_id: int
    session_id: str
    action_type: str
    subject: Optional[Subject] = None
    content_id: Optional[int] = None
    start_time: datetime
    behavior_data: Optional[Dict[str, Any]] = None
    device_type: Optional[str] = None
    platform: Optional[str] = None


class LearningBehaviorResponse(BaseSchema):
    """学习行为响应模型"""
    id: int
    user_id: int
    session_id: str
    action_type: str
    subject: Optional[Subject] = None
    content_id: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    behavior_data: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    device_type: Optional[str] = None
    platform: Optional[str] = None
    created_at: datetime


class PersonalizedRecommendationCreate(BaseSchema):
    """创建个性化推荐模型"""
    user_id: int
    recommendation_type: RecommendationType
    title: str
    description: str
    content_data: Dict[str, Any]
    reason: str
    confidence_score: float
    expires_at: Optional[datetime] = None


class PersonalizedRecommendationResponse(BaseSchema):
    """个性化推荐响应模型"""
    id: int
    user_id: int
    recommendation_type: RecommendationType
    title: str
    description: str
    content_data: Dict[str, Any]
    reason: str
    confidence_score: float
    is_active: bool
    is_viewed: bool
    is_accepted: Optional[bool] = None
    viewed_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime


class LearningProfileResponse(BaseSchema):
    """学习画像响应模型"""
    id: int
    user_id: int
    learning_style: LearningStyle
    preferred_subjects: List[str]
    weak_subjects: List[str]
    preferred_study_time: Optional[str] = None
    average_session_duration: int
    study_frequency: float
    overall_ability: float
    subject_abilities: Dict[str, float]
    learning_speed: float
    error_patterns: Dict[str, Any]
    progress_patterns: Dict[str, Any]
    engagement_level: float
    last_updated: datetime
    analysis_count: int
    created_at: datetime


class DashboardData(BaseSchema):
    """仪表板数据模型"""
    user_id: int
    overview: Dict[str, Any]
    recent_performance: List[PerformanceMetricsResponse]
    subject_statistics: Dict[str, Any]
    recommendations: List[PersonalizedRecommendationResponse]
    learning_trends: Dict[str, Any]
    achievements: List[Dict[str, Any]]
    study_calendar: Dict[str, Any]


class AnalysisRequest(BaseSchema):
    """分析请求模型"""
    user_id: int
    student_id: Optional[int] = None
    analysis_type: AnalysisType
    start_date: date
    end_date: date
    subjects: Optional[List[Subject]] = None
    include_recommendations: bool = True