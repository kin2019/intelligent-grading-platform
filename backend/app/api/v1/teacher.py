from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
import json
import time
import random
from datetime import datetime, timedelta

router = APIRouter()

class ClassInfo(BaseModel):
    """班级信息"""
    id: int
    name: str
    grade: str
    student_count: int
    subject: str
    created_at: str

class TeacherDashboardResponse(BaseModel):
    """教师端仪表板响应"""
    teacher_info: Dict[str, Any]
    classes: List[ClassInfo]
    statistics: Dict[str, Any]
    recent_activities: List[Dict[str, Any]]
    pending_tasks: List[Dict[str, Any]]

class ClassReportResponse(BaseModel):
    """班级报告响应"""
    class_info: ClassInfo
    student_stats: List[Dict[str, Any]]
    subject_analysis: Dict[str, Any]
    homework_summary: Dict[str, Any]
    recommendations: List[str]

@router.get("/dashboard", response_model=TeacherDashboardResponse, summary="获取教师端仪表板")
def get_teacher_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取教师端仪表板数据
    
    包括：
    - 教师基本信息
    - 管理的班级列表
    - 教学统计数据
    - 最近活动
    - 待处理任务
    """
    # 教师信息
    teacher_info = {
        "id": current_user.id,
        "name": current_user.nickname,
        "title": "数学老师",
        "school": "实验小学",
        "teaching_years": random.randint(3, 15),
        "subjects": ["数学", "科学"],
        "total_students": random.randint(80, 150)
    }
    
    # 管理的班级
    classes = [
        {
            "id": 1,
            "name": "三年级1班",
            "grade": "三年级",
            "student_count": random.randint(25, 40),
            "subject": "数学",
            "created_at": (datetime.now() - timedelta(days=90)).isoformat()
        },
        {
            "id": 2,
            "name": "三年级2班",
            "grade": "三年级",
            "student_count": random.randint(25, 40),
            "subject": "数学",
            "created_at": (datetime.now() - timedelta(days=90)).isoformat()
        }
    ]
    
    # 统计数据
    statistics = {
        "total_assignments": random.randint(50, 120),
        "graded_assignments": random.randint(45, 115),
        "average_class_score": round(random.uniform(75, 90), 1),
        "improvement_rate": round(random.uniform(0.05, 0.25), 2),
        "active_students_today": random.randint(60, 120),
        "common_errors": [
            {"error_type": "计算错误", "frequency": random.randint(20, 50)},
            {"error_type": "概念理解", "frequency": random.randint(15, 35)},
            {"error_type": "应用题解答", "frequency": random.randint(10, 30)}
        ]
    }
    
    # 最近活动
    recent_activities = [
        {
            "id": i + 1,
            "type": random.choice(["homework_submitted", "assignment_created", "error_pattern_detected"]),
            "description": f"学生提交了{random.choice(['数学', '科学'])}作业",
            "class_name": random.choice(["三年级1班", "三年级2班"]),
            "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
        }
        for i in range(8)
    ]
    
    # 待处理任务
    pending_tasks = [
        {
            "id": 1,
            "type": "review_assignments",
            "title": "批改三年级1班数学作业",
            "count": random.randint(5, 20),
            "priority": "high",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat()
        },
        {
            "id": 2,
            "type": "analyze_errors", 
            "title": "分析错题模式",
            "count": random.randint(10, 30),
            "priority": "medium",
            "due_date": (datetime.now() + timedelta(days=3)).isoformat()
        }
    ]
    
    return {
        "teacher_info": teacher_info,
        "classes": classes,
        "statistics": statistics,
        "recent_activities": recent_activities,
        "pending_tasks": pending_tasks
    }

@router.get("/classes/{class_id}/report", response_model=ClassReportResponse, summary="获取班级报告")
def get_class_report(
    class_id: int,
    period: str = Query(default="week", description="报告周期"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定班级的详细教学报告
    
    - **class_id**: 班级ID
    - **period**: 报告周期 (week/month/semester)
    """
    # 班级信息
    class_info = {
        "id": class_id,
        "name": "三年级1班",
        "grade": "三年级",
        "student_count": 35,
        "subject": "数学",
        "created_at": (datetime.now() - timedelta(days=90)).isoformat()
    }
    
    # 学生统计
    student_stats = []
    for i in range(10):  # 显示前10名学生
        student = {
            "student_id": i + 1,
            "name": f"学生{i+1}",
            "homework_count": random.randint(8, 15),
            "average_score": random.randint(70, 100),
            "accuracy_rate": round(random.uniform(0.7, 0.98), 2),
            "improvement": round(random.uniform(-0.1, 0.3), 2),
            "ranking": i + 1,
            "weak_subjects": random.sample(["计算", "应用题", "几何"], random.randint(0, 2))
        }
        student_stats.append(student)
    
    # 学科分析
    subject_analysis = {
        "subject": "数学",
        "total_topics": 12,
        "mastered_topics": random.randint(8, 11),
        "difficult_topics": [
            {"topic": "分数计算", "error_rate": round(random.uniform(0.2, 0.5), 2)},
            {"topic": "应用题", "error_rate": round(random.uniform(0.1, 0.4), 2)},
            {"topic": "几何图形", "error_rate": round(random.uniform(0.15, 0.35), 2)}
        ],
        "progress_trend": random.choice(["improving", "stable", "declining"]),
        "class_average": round(random.uniform(75, 90), 1)
    }
    
    # 作业总结
    homework_summary = {
        "period": period,
        "total_assignments": random.randint(15, 30),
        "submitted_count": random.randint(300, 800),
        "average_completion_time": random.randint(25, 45),  # 分钟
        "common_errors": [
            {"error": "计算粗心", "frequency": random.randint(30, 60)},
            {"error": "题意理解错误", "frequency": random.randint(20, 40)},
            {"error": "公式运用错误", "frequency": random.randint(15, 35)}
        ],
        "improvement_suggestions": [
            "加强基础计算训练",
            "提高阅读理解能力",
            "巩固公式记忆"
        ]
    }
    
    # 教学建议
    recommendations = [
        "建议增加分数计算的专项练习",
        "应用题解答需要加强步骤分解训练",
        "几何图形识别能力需要提升",
        "整体表现良好，继续保持现有教学方法",
        "可以适当增加趣味性练习提高学习兴趣"
    ]
    
    return {
        "class_info": class_info,
        "student_stats": student_stats,
        "subject_analysis": subject_analysis,
        "homework_summary": homework_summary,
        "recommendations": recommendations
    }

@router.get("/classes/{class_id}/students", summary="获取班级学生列表")
def get_class_students(
    class_id: int,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="name", description="排序字段"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取班级的学生列表
    
    - **class_id**: 班级ID
    - **page**: 页码
    - **limit**: 每页数量
    - **sort_by**: 排序字段 (name/score/recent_activity)
    """
    # 模拟学生列表
    students = []
    for i in range(limit):
        student = {
            "id": i + 1,
            "name": f"学生{i+1}",
            "student_number": f"2024{i+1:03d}",
            "avatar_url": f"https://example.com/student{i+1}.jpg",
            "homework_count": random.randint(10, 25),
            "average_score": random.randint(65, 100),
            "accuracy_rate": round(random.uniform(0.65, 0.98), 2),
            "last_active": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
            "status": random.choice(["active", "inactive", "needs_attention"]),
            "parent_contact": f"parent{i+1}@example.com"
        }
        students.append(student)
    
    return {
        "class_id": class_id,
        "total": len(students),
        "page": page,
        "limit": limit,
        "sort_by": sort_by,
        "students": students
    }

@router.post("/assignments", summary="创建作业")
def create_assignment(
    title: str,
    description: str,
    subject: str,
    grade: str,
    class_ids: List[int],
    due_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新的作业任务
    
    - **title**: 作业标题
    - **description**: 作业描述
    - **subject**: 学科
    - **grade**: 年级
    - **class_ids**: 目标班级ID列表
    - **due_date**: 截止日期 (可选)
    """
    assignment_id = random.randint(1000, 9999)
    
    return {
        "assignment_id": assignment_id,
        "title": title,
        "description": description,
        "subject": subject,
        "grade": grade,
        "class_ids": class_ids,
        "due_date": due_date,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "estimated_students": sum([random.randint(25, 40) for _ in class_ids])
    }

@router.get("/assignments", summary="获取作业列表")
def get_assignments(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None, description="作业状态筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取教师创建的作业列表
    
    - **page**: 页码
    - **limit**: 每页数量
    - **status**: 状态筛选 (active/completed/overdue)
    """
    assignments = []
    for i in range(limit):
        assignment = {
            "id": i + 1,
            "title": f"数学作业 - 第{i+1}次",
            "subject": random.choice(["数学", "科学"]),
            "grade": "三年级",
            "class_count": random.randint(1, 3),
            "student_count": random.randint(25, 100),
            "submitted_count": random.randint(20, 95),
            "status": random.choice(["active", "completed", "overdue"]),
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "due_date": (datetime.now() + timedelta(days=random.randint(1, 7))).isoformat()
        }
        
        if status and assignment["status"] != status:
            continue
            
        assignments.append(assignment)
    
    return {
        "total": len(assignments),
        "page": page,
        "limit": limit,
        "status_filter": status,
        "assignments": assignments
    }

@router.get("/analytics", summary="获取教学分析数据")
def get_teaching_analytics(
    period: str = Query(default="month", description="分析周期"),
    class_id: Optional[int] = Query(default=None, description="班级筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取教学分析数据
    
    包括错题模式、学习趋势、教学效果等
    """
    return {
        "period": period,
        "class_id": class_id,
        "overview": {
            "total_students": random.randint(70, 150),
            "active_students": random.randint(65, 145),
            "average_improvement": round(random.uniform(0.1, 0.3), 2),
            "completion_rate": round(random.uniform(0.85, 0.98), 2)
        },
        "error_patterns": [
            {
                "pattern": "计算错误",
                "frequency": random.randint(40, 80),
                "trend": random.choice(["increasing", "decreasing", "stable"]),
                "affected_students": random.randint(20, 50)
            },
            {
                "pattern": "概念理解",
                "frequency": random.randint(25, 60),
                "trend": random.choice(["increasing", "decreasing", "stable"]),
                "affected_students": random.randint(15, 40)
            }
        ],
        "learning_trends": [
            {
                "week": f"第{i+1}周",
                "average_score": random.randint(70, 90),
                "completion_rate": round(random.uniform(0.8, 0.98), 2),
                "improvement": round(random.uniform(-0.05, 0.15), 2)
            }
            for i in range(4)
        ],
        "recommendations": [
            "建议加强基础计算能力训练",
            "可以引入更多实际应用场景",
            "适当增加小组合作学习",
            "关注学习困难的学生群体"
        ],
        "generated_at": datetime.now().isoformat()
    }