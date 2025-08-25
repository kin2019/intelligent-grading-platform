"""
学科相关数据模型
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from sqlalchemy import String, Boolean, DateTime, Text, Integer, ForeignKey, DECIMAL, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseTable, BaseSchema
from .homework import Subject, QuestionType, DifficultyLevel


class KnowledgePointStatus(str, Enum):
    """知识点掌握状态"""
    NOT_STARTED = "not_started"    # 未开始
    LEARNING = "learning"          # 学习中
    MASTERED = "mastered"          # 已掌握
    NEEDS_REVIEW = "needs_review"  # 需要复习


class ExerciseType(str, Enum):
    """练习题类型"""
    ORIGINAL = "original"          # 原题
    SIMILAR = "similar"            # 相似题
    GENERATED = "generated"        # 生成题
    RECOMMENDED = "recommended"    # 推荐题


# SQLAlchemy 模型
class KnowledgePoint(BaseTable):
    """知识点表"""
    __tablename__ = "knowledge_points"
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(100), comment="知识点名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, comment="知识点编码")
    subject: Mapped[Subject] = mapped_column(String(20), comment="所属学科")
    grade: Mapped[str] = mapped_column(String(20), comment="适用年级")
    
    # 层级关系
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("knowledge_points.id"), comment="父知识点ID")
    level: Mapped[int] = mapped_column(Integer, default=1, comment="层级深度")
    order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    
    # 内容描述
    description: Mapped[Optional[str]] = mapped_column(Text, comment="知识点描述")
    learning_objectives: Mapped[Optional[str]] = mapped_column(Text, comment="学习目标")
    key_concepts: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, comment="核心概念")
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    difficulty_weight: Mapped[float] = mapped_column(DECIMAL(3, 2), default=1.0, comment="难度权重")


class UserKnowledgeProgress(BaseTable):
    """用户知识点进度表"""
    __tablename__ = "user_knowledge_progress"
    
    # 关联信息
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="用户ID")
    knowledge_point_id: Mapped[int] = mapped_column(ForeignKey("knowledge_points.id"), comment="知识点ID")
    
    # 进度信息
    status: Mapped[KnowledgePointStatus] = mapped_column(
        String(20), default=KnowledgePointStatus.NOT_STARTED, comment="掌握状态"
    )
    mastery_level: Mapped[float] = mapped_column(DECIMAL(3, 2), default=0.0, comment="掌握程度(0-1)")
    
    # 练习统计
    total_exercises: Mapped[int] = mapped_column(Integer, default=0, comment="总练习次数")
    correct_exercises: Mapped[int] = mapped_column(Integer, default=0, comment="正确次数")
    last_exercise_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="最后练习时间")
    
    # 时间统计
    total_study_time: Mapped[int] = mapped_column(Integer, default=0, comment="总学习时间(分钟)")
    first_learned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="首次学习时间")
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="最后复习时间")


class Exercise(BaseTable):
    """练习题表"""
    __tablename__ = "exercises"
    
    # 基本信息
    title: Mapped[str] = mapped_column(String(200), comment="题目标题")
    content: Mapped[str] = mapped_column(Text, comment="题目内容")
    question_type: Mapped[QuestionType] = mapped_column(String(30), comment="题目类型")
    difficulty_level: Mapped[DifficultyLevel] = mapped_column(String(10), comment="难度等级")
    
    # 学科信息
    subject: Mapped[Subject] = mapped_column(String(20), comment="所属学科")
    grade: Mapped[str] = mapped_column(String(20), comment="适用年级")
    knowledge_point_ids: Mapped[List[int]] = mapped_column(JSON, comment="关联知识点ID列表")
    
    # 答案和解析
    correct_answer: Mapped[str] = mapped_column(Text, comment="正确答案")
    answer_analysis: Mapped[Optional[str]] = mapped_column(Text, comment="答案解析")
    solution_steps: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, comment="解题步骤")
    
    # 题目属性
    exercise_type: Mapped[ExerciseType] = mapped_column(String(20), default=ExerciseType.ORIGINAL, comment="题目类型")
    source: Mapped[Optional[str]] = mapped_column(String(100), comment="题目来源")
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, comment="标签列表")
    
    # 多媒体资源
    images: Mapped[Optional[List[str]]] = mapped_column(JSON, comment="图片URL列表")
    audio_url: Mapped[Optional[str]] = mapped_column(String(255), comment="音频URL")
    video_url: Mapped[Optional[str]] = mapped_column(String(255), comment="视频URL")
    
    # 统计信息
    total_attempts: Mapped[int] = mapped_column(Integer, default=0, comment="总尝试次数")
    correct_attempts: Mapped[int] = mapped_column(Integer, default=0, comment="正确次数")
    average_time: Mapped[Optional[float]] = mapped_column(DECIMAL(6, 2), comment="平均用时(秒)")
    
    # 状态信息
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否公开")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已验证")
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), comment="创建者ID")


class UserExerciseRecord(BaseTable):
    """用户练习记录表"""
    __tablename__ = "user_exercise_records"
    
    # 关联信息
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="用户ID")
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), comment="练习题ID")
    
    # 作答信息
    user_answer: Mapped[str] = mapped_column(Text, comment="用户答案")
    is_correct: Mapped[bool] = mapped_column(Boolean, comment="是否正确")
    score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), comment="得分")
    
    # 时间信息
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment="开始时间")
    submit_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment="提交时间")
    time_spent: Mapped[int] = mapped_column(Integer, comment="用时(秒)")
    
    # 分析信息
    error_type: Mapped[Optional[str]] = mapped_column(String(50), comment="错误类型")
    feedback: Mapped[Optional[str]] = mapped_column(Text, comment="反馈信息")
    hint_used: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否使用提示")


# Pydantic 模型
class KnowledgePointBase(BaseSchema):
    """知识点基础模型"""
    name: str
    code: str
    subject: Subject
    grade: str
    description: Optional[str] = None
    learning_objectives: Optional[str] = None


class KnowledgePointCreate(KnowledgePointBase):
    """创建知识点模型"""
    parent_id: Optional[int] = None
    level: int = 1
    order: int = 0
    difficulty_weight: float = 1.0


class KnowledgePointUpdate(BaseSchema):
    """更新知识点模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    learning_objectives: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None
    difficulty_weight: Optional[float] = None


class KnowledgePointResponse(KnowledgePointBase):
    """知识点响应模型"""
    id: int
    parent_id: Optional[int] = None
    level: int
    order: int
    key_concepts: Optional[Dict[str, Any]] = None
    is_active: bool
    difficulty_weight: float
    created_at: datetime


class UserKnowledgeProgressResponse(BaseSchema):
    """用户知识点进度响应模型"""
    id: int
    user_id: int
    knowledge_point_id: int
    knowledge_point: KnowledgePointResponse
    status: KnowledgePointStatus
    mastery_level: float
    total_exercises: int
    correct_exercises: int
    accuracy_rate: Optional[float] = None
    last_exercise_at: Optional[datetime] = None
    total_study_time: int
    created_at: datetime


class ExerciseBase(BaseSchema):
    """练习题基础模型"""
    title: str
    content: str
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    subject: Subject
    grade: str
    correct_answer: str


class ExerciseCreate(ExerciseBase):
    """创建练习题模型"""
    knowledge_point_ids: List[int]
    answer_analysis: Optional[str] = None
    solution_steps: Optional[Dict[str, Any]] = None
    exercise_type: ExerciseType = ExerciseType.ORIGINAL
    source: Optional[str] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None


class ExerciseUpdate(BaseSchema):
    """更新练习题模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    correct_answer: Optional[str] = None
    answer_analysis: Optional[str] = None
    solution_steps: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_verified: Optional[bool] = None


class ExerciseResponse(ExerciseBase):
    """练习题响应模型"""
    id: int
    knowledge_point_ids: List[int]
    answer_analysis: Optional[str] = None
    solution_steps: Optional[Dict[str, Any]] = None
    exercise_type: ExerciseType
    source: Optional[str] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    total_attempts: int
    correct_attempts: int
    accuracy_rate: Optional[float] = None
    average_time: Optional[float] = None
    is_public: bool
    is_verified: bool
    created_at: datetime


class UserExerciseRecordCreate(BaseSchema):
    """创建练习记录模型"""
    exercise_id: int
    user_answer: str
    start_time: datetime
    submit_time: datetime
    hint_used: bool = False


class UserExerciseRecordResponse(BaseSchema):
    """练习记录响应模型"""
    id: int
    user_id: int
    exercise_id: int
    exercise: Optional[ExerciseResponse] = None
    user_answer: str
    is_correct: bool
    score: Optional[float] = None
    time_spent: int
    error_type: Optional[str] = None
    feedback: Optional[str] = None
    hint_used: bool
    created_at: datetime


class SubjectStatistics(BaseSchema):
    """学科统计模型"""
    subject: Subject
    total_exercises: int
    completed_exercises: int
    correct_exercises: int
    accuracy_rate: float
    average_score: float
    total_study_time: int
    mastered_knowledge_points: int
    total_knowledge_points: int
    progress_percentage: float
    weak_areas: List[str]
    strong_areas: List[str]