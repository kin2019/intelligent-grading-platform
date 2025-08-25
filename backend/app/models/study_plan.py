from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from typing import Optional, List

class StudyPlan(Base):
    """学习计划模型"""
    __tablename__ = "study_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    title = Column(String(200), nullable=False, comment="计划标题")
    description = Column(Text, nullable=True, comment="计划描述")
    
    # 计划配置
    priority = Column(String(20), default="medium", comment="优先级: low/medium/high")
    duration_days = Column(Integer, default=7, comment="计划时长(天)")
    daily_time = Column(Integer, default=30, comment="每日学习时间(分钟)")
    subjects = Column(Text, nullable=False, comment="学科列表(JSON)")
    
    # 进度统计
    total_tasks = Column(Integer, default=0, comment="总任务数")
    completed_tasks = Column(Integer, default=0, comment="已完成任务数")
    estimated_time = Column(Integer, default=0, comment="预计总时间(分钟)")
    actual_time = Column(Integer, default=0, comment="实际用时(分钟)")
    
    # 状态
    status = Column(String(20), default="active", comment="状态: active/completed/paused/cancelled")
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    start_date = Column(DateTime, nullable=True, comment="开始时间")
    end_date = Column(DateTime, nullable=True, comment="结束时间")
    
    # 关联关系
    user = relationship("User", back_populates="study_plans")
    tasks = relationship("StudyTask", back_populates="study_plan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<StudyPlan(id={self.id}, title={self.title}, user_id={self.user_id})>"
    
    @property
    def progress(self) -> float:
        """计算进度百分比"""
        if self.total_tasks == 0:
            return 0.0
        return round(self.completed_tasks / self.total_tasks * 100, 1)
    
    @property
    def remaining_tasks(self) -> int:
        """剩余任务数"""
        return max(0, self.total_tasks - self.completed_tasks)
    
    def update_progress(self):
        """更新进度统计"""
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if session:
            # 重新计算任务统计
            total = len(self.tasks)
            completed = sum(1 for task in self.tasks if task.completed)
            
            self.total_tasks = total
            self.completed_tasks = completed
            self.estimated_time = sum(task.estimated_time for task in self.tasks)
            self.actual_time = sum(task.actual_time or 0 for task in self.tasks)
            
            # 如果所有任务完成，更新状态
            if total > 0 and completed == total and self.status == "active":
                self.status = "completed"
                self.end_date = func.now()


class StudyTask(Base):
    """学习任务模型"""
    __tablename__ = "study_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    study_plan_id = Column(Integer, ForeignKey("study_plans.id"), nullable=False, comment="学习计划ID")
    title = Column(String(200), nullable=False, comment="任务标题")
    description = Column(Text, nullable=True, comment="任务描述")
    subject = Column(String(50), nullable=False, comment="学科")
    
    # 任务配置
    estimated_time = Column(Integer, default=30, comment="预计用时(分钟)")
    actual_time = Column(Integer, nullable=True, comment="实际用时(分钟)")
    priority = Column(String(20), default="medium", comment="优先级: low/medium/high")
    difficulty = Column(String(20), default="medium", comment="难度: easy/medium/hard")
    
    # 任务状态
    completed = Column(Boolean, default=False, comment="是否完成")
    status = Column(String(20), default="pending", comment="状态: pending/in_progress/completed/skipped")
    
    # 时间安排
    due_date = Column(DateTime, nullable=True, comment="截止时间")
    due_time = Column(String(10), nullable=True, comment="截止时间(HH:MM)")
    scheduled_date = Column(DateTime, nullable=True, comment="计划日期")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    
    # 关联关系
    study_plan = relationship("StudyPlan", back_populates="tasks")
    
    def __repr__(self):
        return f"<StudyTask(id={self.id}, title={self.title}, subject={self.subject})>"
    
    def mark_completed(self):
        """标记任务为已完成"""
        self.completed = True
        self.status = "completed"
        self.completed_at = func.now()
        
        # 更新学习计划进度
        if self.study_plan:
            self.study_plan.update_progress()
    
    def mark_uncompleted(self):
        """取消完成状态"""
        self.completed = False
        self.status = "pending"
        self.completed_at = None
        
        # 更新学习计划进度
        if self.study_plan:
            self.study_plan.update_progress()


class StudyProgress(Base):
    """学习进度记录模型"""
    __tablename__ = "study_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    study_plan_id = Column(Integer, ForeignKey("study_plans.id"), nullable=False, comment="学习计划ID")
    date = Column(DateTime, default=func.current_date(), comment="记录日期")
    
    # 进度统计
    tasks_completed = Column(Integer, default=0, comment="当日完成任务数")
    time_spent = Column(Integer, default=0, comment="当日学习时间(分钟)")
    subjects_studied = Column(Text, nullable=True, comment="学习的学科(JSON)")
    
    # 评分和反馈
    difficulty_rating = Column(Float, nullable=True, comment="难度评分(1-5)")
    satisfaction_rating = Column(Float, nullable=True, comment="满意度评分(1-5)")
    notes = Column(Text, nullable=True, comment="学习笔记")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<StudyProgress(id={self.id}, user_id={self.user_id}, date={self.date})>"