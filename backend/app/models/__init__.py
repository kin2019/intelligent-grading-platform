# 模型包初始化

from .user import User
from .homework import *  # 现有的作业相关模型
from .study_plan import StudyPlan, StudyTask, StudyProgress
from .parent_child import ParentChild, BindInvite, InviteStatus
from .exercise import (
    ExerciseGeneration,
    GeneratedExercise,
    ExerciseTemplate,
    ExerciseDownload,
    ExerciseUsageStats
)

__all__ = [
    "User",
    "StudyPlan", 
    "StudyTask",
    "StudyProgress",
    "ParentChild",
    "BindInvite",
    "InviteStatus",
    "ExerciseGeneration",
    "GeneratedExercise", 
    "ExerciseTemplate",
    "ExerciseDownload",
    "ExerciseUsageStats"
]