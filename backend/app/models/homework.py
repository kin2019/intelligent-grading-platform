from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Homework(Base):
    """作业记录模型"""
    __tablename__ = "homework"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    
    # 图片信息
    original_image_url = Column(String(500), nullable=False, comment="原始图片URL")
    processed_image_url = Column(String(500), nullable=True, comment="处理后图片URL")
    
    # 学科和类型
    subject = Column(String(50), nullable=False, comment="学科: math/chinese/english/physics/chemistry")
    subject_type = Column(String(50), nullable=True, comment="具体类型: arithmetic/algebra/geometry等")
    grade_level = Column(String(20), nullable=True, comment="年级水平")
    
    # OCR识别结果
    ocr_result = Column(JSON, nullable=True, comment="OCR识别原始结果")
    ocr_text = Column(Text, nullable=True, comment="识别出的文本内容")
    
    # 批改结果
    correction_result = Column(JSON, nullable=False, comment="批改结果详情")
    total_questions = Column(Integer, default=0, comment="总题目数")
    correct_count = Column(Integer, default=0, comment="正确题目数")
    wrong_count = Column(Integer, default=0, comment="错误题目数")
    accuracy_rate = Column(Float, default=0.0, comment="正确率")
    
    # 处理状态
    status = Column(String(20), default="pending", comment="处理状态: pending/processing/completed/failed")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 时间消耗
    processing_time = Column(Float, nullable=True, comment="处理耗时(秒)")
    ocr_time = Column(Float, nullable=True, comment="OCR识别耗时")
    correction_time = Column(Float, nullable=True, comment="批改耗时")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    def __repr__(self):
        return f"<Homework(id={self.id}, subject={self.subject}, accuracy={self.accuracy_rate})>"
    
    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == "completed"
    
    @property
    def is_failed(self) -> bool:
        """是否处理失败"""
        return self.status == "failed"

class ErrorQuestion(Base):
    """错题记录模型"""
    __tablename__ = "error_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homework.id"), nullable=False, comment="作业ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    
    # 题目内容
    question_text = Column(Text, nullable=False, comment="题目内容")
    user_answer = Column(String(200), nullable=True, comment="用户答案")
    correct_answer = Column(String(200), nullable=False, comment="正确答案")
    
    # 错误分析
    error_type = Column(String(50), nullable=True, comment="错误类型")
    error_reason = Column(Text, nullable=True, comment="错误原因")
    explanation = Column(Text, nullable=True, comment="详细解释")
    
    # 知识点
    knowledge_points = Column(JSON, nullable=True, comment="涉及知识点")
    difficulty_level = Column(Integer, default=1, comment="难度等级1-10")
    
    # 复习状态
    is_reviewed = Column(Boolean, default=False, comment="是否已复习")
    review_count = Column(Integer, default=0, comment="复习次数") 
    last_review_at = Column(DateTime, nullable=True, comment="最后复习时间")
    
    # 语音讲解
    audio_url = Column(String(500), nullable=True, comment="语音讲解URL")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<ErrorQuestion(id={self.id}, question={self.question_text[:20]}...)>"