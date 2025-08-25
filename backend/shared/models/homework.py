"""
作业批改相关数据模型
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from sqlalchemy import String, Boolean, DateTime, Text, Integer, ForeignKey, DECIMAL, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseTable, BaseSchema


class Subject(str, Enum):
    """学科枚举"""
    MATH = "math"            # 数学
    CHINESE = "chinese"      # 语文
    ENGLISH = "english"      # 英语
    PHYSICS = "physics"      # 物理
    CHEMISTRY = "chemistry"  # 化学
    BIOLOGY = "biology"      # 生物
    GEOGRAPHY = "geography"  # 地理
    HISTORY = "history"      # 历史


class HomeworkStatus(str, Enum):
    """作业状态枚举"""
    PENDING = "pending"      # 待处理
    PROCESSING = "processing" # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败


class QuestionType(str, Enum):
    """题目类型枚举"""
    ARITHMETIC = "arithmetic"        # 四则运算
    ALGEBRA = "algebra"             # 代数
    GEOMETRY = "geometry"           # 几何
    FUNCTION = "function"           # 函数
    STATISTICS = "statistics"       # 统计
    PINYIN = "pinyin"              # 拼音
    CHARACTER = "character"         # 汉字
    GRAMMAR = "grammar"            # 语法
    READING = "reading"            # 阅读理解
    ESSAY = "essay"                # 作文
    SPELLING = "spelling"          # 拼写
    VOCABULARY = "vocabulary"       # 词汇
    PRONUNCIATION = "pronunciation" # 发音
    TRANSLATION = "translation"     # 翻译


class DifficultyLevel(str, Enum):
    """难度等级枚举"""
    EASY = "easy"        # 简单
    MEDIUM = "medium"    # 中等
    HARD = "hard"        # 困难


# SQLAlchemy 模型
class Homework(BaseTable):
    """作业表"""
    __tablename__ = "homework"
    
    # 基本信息
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="用户ID")
    student_id: Mapped[Optional[int]] = mapped_column(ForeignKey("students.id"), comment="学生ID")
    
    # 图片信息
    original_image_url: Mapped[str] = mapped_column(String(255), comment="原图URL")
    processed_image_url: Mapped[Optional[str]] = mapped_column(String(255), comment="处理后图片URL")
    
    # 学科和状态
    subject: Mapped[Subject] = mapped_column(String(20), comment="学科")
    status: Mapped[HomeworkStatus] = mapped_column(String(20), default=HomeworkStatus.PENDING, comment="状态")
    
    # 识别和批改结果
    ocr_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, comment="OCR识别结果")
    correction_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, comment="批改结果")
    
    # 统计信息
    total_questions: Mapped[int] = mapped_column(Integer, default=0, comment="总题数")
    correct_questions: Mapped[int] = mapped_column(Integer, default=0, comment="正确题数")
    accuracy_rate: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), comment="正确率")
    
    # 批改时间
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="开始批改时间")
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="完成批改时间")
    
    # 关联关系
    user: Mapped["User"] = relationship("User", back_populates="homework")
    student: Mapped[Optional["Student"]] = relationship("Student", back_populates="homework")
    error_questions: Mapped[List["ErrorQuestion"]] = relationship("ErrorQuestion", back_populates="homework")


class ErrorQuestion(BaseTable):
    """错题表"""
    __tablename__ = "error_questions"
    
    # 关联信息
    homework_id: Mapped[int] = mapped_column(ForeignKey("homework.id"), comment="作业ID")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="用户ID")
    
    # 题目信息
    question_text: Mapped[str] = mapped_column(Text, comment="题目内容")
    question_type: Mapped[QuestionType] = mapped_column(String(30), comment="题目类型")
    difficulty_level: Mapped[DifficultyLevel] = mapped_column(String(10), comment="难度等级")
    
    # 答案信息
    user_answer: Mapped[str] = mapped_column(Text, comment="用户答案")
    correct_answer: Mapped[str] = mapped_column(Text, comment="正确答案")
    
    # 分析和讲解
    error_type: Mapped[Optional[str]] = mapped_column(String(50), comment="错误类型")
    explanation: Mapped[Optional[str]] = mapped_column(Text, comment="错误解析")
    hint: Mapped[Optional[str]] = mapped_column(Text, comment="提示")
    solution_steps: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, comment="解题步骤")
    
    # 多媒体资源
    audio_url: Mapped[Optional[str]] = mapped_column(String(255), comment="语音讲解URL")
    video_url: Mapped[Optional[str]] = mapped_column(String(255), comment="视频讲解URL")
    
    # 练习信息
    practiced_count: Mapped[int] = mapped_column(Integer, default=0, comment="练习次数")
    mastered: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否掌握")
    last_practiced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="最后练习时间")
    
    # 关联关系
    homework: Mapped["Homework"] = relationship("Homework", back_populates="error_questions")
    user: Mapped["User"] = relationship("User", back_populates="error_questions")
    similar_questions: Mapped[List["SimilarQuestion"]] = relationship("SimilarQuestion", back_populates="error_question")


class SimilarQuestion(BaseTable):
    """相似题目表"""
    __tablename__ = "similar_questions"
    
    # 关联信息
    error_question_id: Mapped[int] = mapped_column(ForeignKey("error_questions.id"), comment="错题ID")
    
    # 题目信息
    question_text: Mapped[str] = mapped_column(Text, comment="题目内容")
    question_type: Mapped[QuestionType] = mapped_column(String(30), comment="题目类型")
    difficulty_level: Mapped[DifficultyLevel] = mapped_column(String(10), comment="难度等级")
    
    # 答案和解析
    correct_answer: Mapped[str] = mapped_column(Text, comment="正确答案")
    explanation: Mapped[Optional[str]] = mapped_column(Text, comment="解题思路")
    solution_steps: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, comment="解题步骤")
    
    # 相似度
    similarity_score: Mapped[float] = mapped_column(DECIMAL(3, 2), comment="相似度分数")
    
    # 练习统计
    attempted_count: Mapped[int] = mapped_column(Integer, default=0, comment="尝试次数")
    correct_count: Mapped[int] = mapped_column(Integer, default=0, comment="正确次数")
    
    # 关联关系
    error_question: Mapped["ErrorQuestion"] = relationship("ErrorQuestion", back_populates="similar_questions")


# Pydantic 模型
class HomeworkBase(BaseSchema):
    """作业基础模型"""
    subject: Subject
    original_image_url: str


class HomeworkCreate(HomeworkBase):
    """创建作业模型"""
    user_id: int
    student_id: Optional[int] = None


class HomeworkUpdate(BaseSchema):
    """更新作业模型"""
    status: Optional[HomeworkStatus] = None
    processed_image_url: Optional[str] = None
    ocr_result: Optional[Dict[str, Any]] = None
    correction_result: Optional[Dict[str, Any]] = None
    total_questions: Optional[int] = None
    correct_questions: Optional[int] = None
    accuracy_rate: Optional[float] = None


class HomeworkResponse(HomeworkBase):
    """作业响应模型"""
    id: int
    user_id: int
    student_id: Optional[int] = None
    status: HomeworkStatus
    processed_image_url: Optional[str] = None
    ocr_result: Optional[Dict[str, Any]] = None
    correction_result: Optional[Dict[str, Any]] = None
    total_questions: int
    correct_questions: int
    accuracy_rate: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


class ErrorQuestionBase(BaseSchema):
    """错题基础模型"""
    question_text: str
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    user_answer: str
    correct_answer: str


class ErrorQuestionCreate(ErrorQuestionBase):
    """创建错题模型"""
    homework_id: int
    user_id: int
    error_type: Optional[str] = None
    explanation: Optional[str] = None
    hint: Optional[str] = None
    solution_steps: Optional[Dict[str, Any]] = None


class ErrorQuestionUpdate(BaseSchema):
    """更新错题模型"""
    explanation: Optional[str] = None
    hint: Optional[str] = None
    solution_steps: Optional[Dict[str, Any]] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    practiced_count: Optional[int] = None
    mastered: Optional[bool] = None


class ErrorQuestionResponse(ErrorQuestionBase):
    """错题响应模型"""
    id: int
    homework_id: int
    user_id: int
    error_type: Optional[str] = None
    explanation: Optional[str] = None
    hint: Optional[str] = None
    solution_steps: Optional[Dict[str, Any]] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    practiced_count: int
    mastered: bool
    last_practiced_at: Optional[datetime] = None
    created_at: datetime


class SimilarQuestionBase(BaseSchema):
    """相似题目基础模型"""
    question_text: str
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    correct_answer: str
    similarity_score: float


class SimilarQuestionCreate(SimilarQuestionBase):
    """创建相似题目模型"""
    error_question_id: int
    explanation: Optional[str] = None
    solution_steps: Optional[Dict[str, Any]] = None


class SimilarQuestionResponse(SimilarQuestionBase):
    """相似题目响应模型"""
    id: int
    error_question_id: int
    explanation: Optional[str] = None
    solution_steps: Optional[Dict[str, Any]] = None
    attempted_count: int
    correct_count: int
    created_at: datetime


class HomeworkSubmitRequest(BaseSchema):
    """提交作业请求模型"""
    subject: Subject
    image_base64: str
    student_id: Optional[int] = None


class HomeworkSubmitResponse(BaseSchema):
    """提交作业响应模型"""
    homework_id: int
    status: HomeworkStatus
    message: str


class CorrectionResult(BaseSchema):
    """批改结果模型"""
    total_questions: int
    correct_questions: int
    accuracy_rate: float
    error_questions: List[ErrorQuestionResponse]
    suggestions: List[str]
    next_practice: Optional[List[SimilarQuestionResponse]] = None