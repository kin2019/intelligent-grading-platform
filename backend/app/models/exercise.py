"""
智能出题相关数据模型
包含题目生成记录、题目模板、下载记录等
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


class ExerciseGeneration(Base):
    """题目生成记录表"""
    __tablename__ = "exercise_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    
    # 基本配置信息
    subject = Column(String(50), nullable=False, comment="学科")
    grade = Column(String(20), nullable=False, comment="年级")
    title = Column(String(200), nullable=False, comment="题目集标题")
    description = Column(Text, nullable=True, comment="题目集描述")
    
    # 生成配置
    question_count = Column(Integer, nullable=False, comment="题目数量")
    difficulty_level = Column(String(20), nullable=False, comment="难度等级: easier/same/harder/mixed")
    question_types = Column(Text, nullable=True, comment="题目类型配置(JSON)")
    generation_config = Column(Text, nullable=True, comment="生成配置详情(JSON)")
    
    # 生成结果
    status = Column(String(20), default="pending", comment="生成状态: pending/generating/completed/failed")
    total_questions = Column(Integer, default=0, comment="实际生成题目数")
    generation_time = Column(Float, nullable=True, comment="生成耗时(秒)")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 使用统计
    view_count = Column(Integer, default=0, comment="查看次数")
    download_count = Column(Integer, default=0, comment="下载次数")
    share_count = Column(Integer, default=0, comment="分享次数")
    
    # 状态标记
    is_favorite = Column(Boolean, default=False, comment="是否收藏")
    is_public = Column(Boolean, default=False, comment="是否公开")
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    generated_at = Column(DateTime, nullable=True, comment="生成完成时间")
    
    # 关联关系
    user = relationship("User", back_populates="exercise_generations")
    exercises = relationship("GeneratedExercise", back_populates="generation", cascade="all, delete-orphan")
    downloads = relationship("ExerciseDownload", back_populates="generation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ExerciseGeneration(id={self.id}, subject={self.subject}, grade={self.grade}, user_id={self.user_id})>"
    
    @property
    def progress_percent(self) -> float:
        """生成进度百分比"""
        if self.status == "completed":
            return 100.0
        elif self.status == "failed":
            return 0.0
        elif self.status == "generating":
            return min(90.0, (self.total_questions / max(1, self.question_count)) * 80.0)
        else:
            return 0.0
    
    @property
    def config_dict(self) -> Dict[str, Any]:
        """获取生成配置字典"""
        try:
            return json.loads(self.generation_config) if self.generation_config else {}
        except:
            return {}
    
    def set_config(self, config: Dict[str, Any]):
        """设置生成配置"""
        self.generation_config = json.dumps(config, ensure_ascii=False)
    
    def mark_completed(self, total_questions: int, generation_time: float):
        """标记生成完成"""
        self.status = "completed"
        self.total_questions = total_questions
        self.generation_time = generation_time
        self.generated_at = func.now()
    
    def mark_failed(self, error_message: str):
        """标记生成失败"""
        self.status = "failed"
        self.error_message = error_message


class GeneratedExercise(Base):
    """生成的题目详情表"""
    __tablename__ = "generated_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey("exercise_generations.id"), nullable=False, comment="生成记录ID")
    
    # 题目基本信息
    number = Column(Integer, nullable=False, comment="题目序号")
    subject = Column(String(50), nullable=False, comment="学科")
    question_text = Column(Text, nullable=False, comment="题目内容")
    question_type = Column(String(50), nullable=False, comment="题目类型")
    
    # 答案和解析
    correct_answer = Column(Text, nullable=False, comment="正确答案")
    analysis = Column(Text, nullable=True, comment="解题分析")
    solution_steps = Column(Text, nullable=True, comment="解题步骤(JSON)")
    
    # 题目属性
    difficulty = Column(String(20), nullable=False, comment="难度等级")
    knowledge_points = Column(Text, nullable=True, comment="知识点列表(JSON)")
    estimated_time = Column(Integer, nullable=True, comment="预计用时(分钟)")
    
    # 生成信息
    generation_source = Column(String(50), default="ai", comment="生成来源: ai/template/manual")
    generation_prompt = Column(Text, nullable=True, comment="生成提示词")
    template_id = Column(Integer, nullable=True, comment="模板ID(如果基于模板)")
    
    # 质量评估
    quality_score = Column(Float, nullable=True, comment="题目质量评分(0-10)")
    is_validated = Column(Boolean, default=False, comment="是否已验证")
    validation_notes = Column(Text, nullable=True, comment="验证备注")
    
    # 使用统计
    view_count = Column(Integer, default=0, comment="查看次数")
    correct_rate = Column(Float, nullable=True, comment="正确率(如果有答题记录)")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    generation = relationship("ExerciseGeneration", back_populates="exercises")
    
    def __repr__(self):
        return f"<GeneratedExercise(id={self.id}, number={self.number}, subject={self.subject})>"
    
    @property
    def knowledge_points_list(self) -> List[str]:
        """获取知识点列表"""
        try:
            return json.loads(self.knowledge_points) if self.knowledge_points else []
        except:
            return []
    
    def set_knowledge_points(self, points: List[str]):
        """设置知识点列表"""
        self.knowledge_points = json.dumps(points, ensure_ascii=False)
    
    @property
    def solution_steps_list(self) -> List[Dict[str, Any]]:
        """获取解题步骤列表"""
        try:
            return json.loads(self.solution_steps) if self.solution_steps else []
        except:
            return []
    
    def set_solution_steps(self, steps: List[Dict[str, Any]]):
        """设置解题步骤"""
        self.solution_steps = json.dumps(steps, ensure_ascii=False)


class ExerciseTemplate(Base):
    """题目模板表"""
    __tablename__ = "exercise_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基本信息
    name = Column(String(100), nullable=False, comment="模板名称")
    subject = Column(String(50), nullable=False, comment="学科")
    grade_range = Column(String(50), nullable=False, comment="适用年级范围")
    topic = Column(String(100), nullable=False, comment="知识点/主题")
    
    # 模板内容
    template_content = Column(Text, nullable=False, comment="模板内容")
    answer_pattern = Column(String(200), nullable=True, comment="答案模式")
    variations = Column(Text, nullable=True, comment="变化参数(JSON)")
    
    # 模板属性
    difficulty_level = Column(String(20), nullable=False, comment="难度等级")
    question_type = Column(String(50), nullable=False, comment="题目类型")
    estimated_time = Column(Integer, nullable=True, comment="预计用时(分钟)")
    
    # 使用统计
    usage_count = Column(Integer, default=0, comment="使用次数")
    success_rate = Column(Float, default=0.0, comment="成功率")
    avg_quality_score = Column(Float, nullable=True, comment="平均质量评分")
    
    # 状态和权限
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_public = Column(Boolean, default=False, comment="是否公开")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者ID")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<ExerciseTemplate(id={self.id}, name={self.name}, subject={self.subject})>"
    
    @property
    def variations_dict(self) -> Dict[str, Any]:
        """获取变化参数字典"""
        try:
            return json.loads(self.variations) if self.variations else {}
        except:
            return {}
    
    def set_variations(self, variations: Dict[str, Any]):
        """设置变化参数"""
        self.variations = json.dumps(variations, ensure_ascii=False)


class ExerciseDownload(Base):
    """题目下载记录表"""
    __tablename__ = "exercise_downloads"
    
    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey("exercise_generations.id"), nullable=False, comment="生成记录ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="下载用户ID")
    
    # 下载信息
    download_format = Column(String(20), nullable=False, comment="下载格式: word/pdf/text")
    file_name = Column(String(200), nullable=False, comment="文件名")
    file_path = Column(String(500), nullable=True, comment="文件路径")
    file_size = Column(Integer, nullable=True, comment="文件大小(字节)")
    
    # 下载配置
    include_answers = Column(Boolean, default=True, comment="是否包含答案")
    include_analysis = Column(Boolean, default=True, comment="是否包含解析")
    custom_header = Column(String(200), nullable=True, comment="自定义页眉")
    paper_size = Column(String(10), default="A4", comment="纸张大小")
    
    # 状态信息
    status = Column(String(20), default="pending", comment="状态: pending/processing/completed/failed")
    download_url = Column(String(500), nullable=True, comment="下载链接")
    expires_at = Column(DateTime, nullable=True, comment="链接过期时间")
    
    # 处理信息
    processing_time = Column(Float, nullable=True, comment="处理耗时(秒)")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    downloaded_at = Column(DateTime, nullable=True, comment="下载时间")
    
    # 关联关系
    generation = relationship("ExerciseGeneration", back_populates="downloads")
    user = relationship("User")
    
    def __repr__(self):
        return f"<ExerciseDownload(id={self.id}, format={self.download_format}, status={self.status})>"
    
    def mark_completed(self, file_path: str, file_size: int, download_url: str, processing_time: float):
        """标记下载完成"""
        self.status = "completed"
        self.file_path = file_path
        self.file_size = file_size
        self.download_url = download_url
        self.processing_time = processing_time
        
        # 设置过期时间（24小时后）
        from datetime import timedelta
        self.expires_at = datetime.now() + timedelta(days=1)
    
    def mark_failed(self, error_message: str):
        """标记下载失败"""
        self.status = "failed"
        self.error_message = error_message
    
    @property
    def is_expired(self) -> bool:
        """检查是否已过期"""
        if not self.expires_at:
            return True
        return datetime.now() > self.expires_at


class ExerciseUsageStats(Base):
    """题目使用统计表"""
    __tablename__ = "exercise_usage_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, comment="统计日期")
    
    # 用户统计
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="用户ID(为空表示全站统计)")
    subject = Column(String(50), nullable=True, comment="学科(为空表示全学科)")
    grade = Column(String(20), nullable=True, comment="年级(为空表示全年级)")
    
    # 统计数据
    generation_count = Column(Integer, default=0, comment="生成次数")
    total_questions = Column(Integer, default=0, comment="生成题目总数")
    download_count = Column(Integer, default=0, comment="下载次数")
    view_count = Column(Integer, default=0, comment="查看次数")
    share_count = Column(Integer, default=0, comment="分享次数")
    
    # 质量统计
    avg_generation_time = Column(Float, nullable=True, comment="平均生成时间")
    success_rate = Column(Float, nullable=True, comment="生成成功率")
    avg_quality_score = Column(Float, nullable=True, comment="平均质量评分")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<ExerciseUsageStats(id={self.id}, date={self.date}, user_id={self.user_id})>"