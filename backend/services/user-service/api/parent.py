"""
家长管理API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from ....shared.models.user import (
    UserResponse, StudentResponse, UserRole
)
from ....shared.models.base import ResponseModel
from ....shared.utils.database import get_db
from ..repositories.user_repository import UserRepository, StudentRepository

router = APIRouter()


def get_user_from_header(request: Request) -> dict:
    """从请求头获取用户信息"""
    return {
        "id": int(request.headers.get("X-User-ID")),
        "role": request.headers.get("X-User-Role"),
        "openid": request.headers.get("X-User-OpenID"),
        "vip_type": request.headers.get("X-User-VIP-Type")
    }


@router.get("/my-children", response_model=List[StudentResponse])
async def get_my_children(request: Request, db: Session = Depends(get_db)):
    """获取我的孩子列表"""
    current_user = get_user_from_header(request)
    
    # 检查权限：只有家长可以访问
    if current_user["role"] != UserRole.PARENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    student_repo = StudentRepository()
    students = student_repo.get_by_parent_id(db, current_user["id"])
    
    return [StudentResponse.model_validate(student) for student in students]


@router.get("/child/{student_id}/progress", response_model=ResponseModel)
async def get_child_progress(
    student_id: int,
    request: Request,
    days: int = Query(30, ge=1, le=365, description="查询天数"),
    db: Session = Depends(get_db)
):
    """获取孩子的学习进度"""
    current_user = get_user_from_header(request)
    
    # 检查权限：只有家长可以访问
    if current_user["role"] != UserRole.PARENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    student_repo = StudentRepository()
    student = student_repo.get_by_id(db, student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )
    
    # 检查是否是自己的孩子
    if student.parent_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 这里可以添加更详细的进度分析逻辑
    # 目前返回基础统计信息
    from datetime import datetime, timedelta
    
    progress_data = {
        "student_id": student.id,
        "student_name": student.name,
        "period_days": days,
        "total_homework": student.total_homework,
        "completed_homework": student.completed_homework,
        "completion_rate": (student.completed_homework / student.total_homework * 100) if student.total_homework > 0 else 0,
        "average_score": float(student.average_score) if student.average_score else 0.0,
        "grade": student.grade.value,
        "school": student.school,
        "class_name": student.class_name,
        "recent_activity": {
            "last_updated": student.updated_at.isoformat(),
            "streak_days": 0,  # 这里可以计算连续学习天数
            "weekly_hours": 0,  # 这里可以计算每周学习时长
        },
        "subjects_performance": {
            "math": {"score": 85, "trend": "improving"},
            "chinese": {"score": 78, "trend": "stable"},
            "english": {"score": 82, "trend": "improving"}
        },
        "recommendations": [
            "建议加强语文阅读理解练习",
            "数学计算准确率有所提升，继续保持",
            "英语词汇量需要进一步扩充"
        ]
    }
    
    return ResponseModel(
        code=200,
        message="获取学习进度成功",
        data=progress_data
    )


@router.get("/child/{student_id}/error-analysis", response_model=ResponseModel)
async def get_child_error_analysis(
    student_id: int,
    request: Request,
    subject: Optional[str] = Query(None, description="学科筛选"),
    days: int = Query(7, ge=1, le=30, description="查询天数"),
    db: Session = Depends(get_db)
):
    """获取孩子的错题分析"""
    current_user = get_user_from_header(request)
    
    # 检查权限
    if current_user["role"] != UserRole.PARENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    student_repo = StudentRepository()
    student = student_repo.get_by_id(db, student_id)
    
    if not student or student.parent_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在或权限不足"
        )
    
    # 这里应该查询真实的错题数据
    # 目前返回模拟数据
    error_analysis = {
        "student_id": student.id,
        "student_name": student.name,
        "analysis_period": f"近{days}天",
        "subject_filter": subject,
        "error_summary": {
            "total_errors": 15,
            "error_rate": 18.5,
            "improvement_rate": 12.3,
            "common_error_types": [
                {"type": "计算错误", "count": 8, "percentage": 53.3},
                {"type": "理解错误", "count": 4, "percentage": 26.7},
                {"type": "粗心错误", "count": 3, "percentage": 20.0}
            ]
        },
        "subject_breakdown": {
            "math": {
                "errors": 8,
                "weak_points": ["分数运算", "应用题理解"],
                "improvement_suggestions": ["加强基础计算练习", "多做应用题分析"]
            },
            "chinese": {
                "errors": 4,
                "weak_points": ["拼音识别", "词语理解"],
                "improvement_suggestions": ["多读多练拼音", "扩大词汇量"]
            },
            "english": {
                "errors": 3,
                "weak_points": ["单词拼写", "语法运用"],
                "improvement_suggestions": ["背诵常用单词", "语法专项练习"]
            }
        },
        "learning_suggestions": [
            "建议每天安排30分钟基础练习",
            "重点关注计算准确性",
            "适当增加阅读量提高理解能力"
        ]
    }
    
    return ResponseModel(
        code=200,
        message="获取错题分析成功",
        data=error_analysis
    )


@router.get("/child/{student_id}/study-plan", response_model=ResponseModel)
async def get_child_study_plan(
    student_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """获取孩子的学习计划"""
    current_user = get_user_from_header(request)
    
    # 检查权限
    if current_user["role"] != UserRole.PARENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    student_repo = StudentRepository()
    student = student_repo.get_by_id(db, student_id)
    
    if not student or student.parent_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在或权限不足"
        )
    
    # 这里应该根据学生的学习情况生成个性化学习计划
    # 目前返回模拟数据
    study_plan = {
        "student_id": student.id,
        "student_name": student.name,
        "plan_period": "本周学习计划",
        "daily_schedule": {
            "monday": {
                "subjects": ["数学", "语文"],
                "tasks": ["口算练习20题", "古诗背诵1首"],
                "estimated_time": "45分钟"
            },
            "tuesday": {
                "subjects": ["英语", "数学"],
                "tasks": ["单词练习10个", "应用题练习5道"],
                "estimated_time": "40分钟"
            },
            "wednesday": {
                "subjects": ["语文", "英语"],
                "tasks": ["阅读理解1篇", "英语对话练习"],
                "estimated_time": "50分钟"
            },
            "thursday": {
                "subjects": ["数学", "语文"],
                "tasks": ["几何题练习", "作文片段练习"],
                "estimated_time": "45分钟"
            },
            "friday": {
                "subjects": ["英语", "复习"],
                "tasks": ["英语听力练习", "本周错题复习"],
                "estimated_time": "40分钟"
            },
            "saturday": {
                "subjects": ["综合练习"],
                "tasks": ["模拟测试", "弱项专项练习"],
                "estimated_time": "60分钟"
            },
            "sunday": {
                "subjects": ["休息调整"],
                "tasks": ["轻松阅读", "知识点梳理"],
                "estimated_time": "30分钟"
            }
        },
        "weekly_goals": [
            "提高数学计算准确率到90%以上",
            "掌握本周新学语文生词",
            "熟练运用英语基础语法"
        ],
        "parent_guidance": [
            "每天监督完成作业，及时鼓励",
            "与孩子一起复习错题，分析原因",
            "营造良好的学习环境，减少干扰"
        ]
    }
    
    return ResponseModel(
        code=200,
        message="获取学习计划成功",
        data=study_plan
    )


@router.post("/child/{student_id}/feedback", response_model=ResponseModel)
async def submit_child_feedback(
    student_id: int,
    feedback_content: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """提交孩子学习反馈"""
    current_user = get_user_from_header(request)
    
    # 检查权限
    if current_user["role"] != UserRole.PARENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    student_repo = StudentRepository()
    student = student_repo.get_by_id(db, student_id)
    
    if not student or student.parent_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在或权限不足"
        )
    
    # 这里应该保存反馈到数据库
    # 目前只返回成功消息
    from datetime import datetime
    
    # 可以创建一个反馈表来存储这些数据
    feedback_data = {
        "student_id": student_id,
        "parent_id": current_user["id"],
        "content": feedback_content,
        "submitted_at": datetime.now().isoformat(),
        "status": "submitted"
    }
    
    return ResponseModel(
        code=200,
        message="反馈提交成功，我们将认真处理您的建议",
        data=feedback_data
    )


@router.get("/dashboard", response_model=ResponseModel)
async def get_parent_dashboard(request: Request, db: Session = Depends(get_db)):
    """获取家长仪表板数据"""
    current_user = get_user_from_header(request)
    
    # 检查权限
    if current_user["role"] != UserRole.PARENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取家长的所有孩子
    student_repo = StudentRepository()
    students = student_repo.get_by_parent_id(db, current_user["id"])
    
    # 构建仪表板数据
    dashboard_data = {
        "parent_id": current_user["id"],
        "children_count": len(students),
        "children": [],  # 添加完整的children数据供前端使用
        "children_summary": [],
        "overall_stats": {
            "total_homework": 0,
            "completed_homework": 0,
            "average_score": 0.0,
            "active_children": 0
        },
        "recent_activities": [],
        "alerts": [],
        "quick_actions": [
            {"title": "查看作业进度", "action": "view_homework"},
            {"title": "错题分析", "action": "error_analysis"},
            {"title": "学习计划", "action": "study_plan"},
            {"title": "联系老师", "action": "contact_teacher"}
        ]
    }
    
    total_homework = 0
    total_completed = 0
    total_score = 0.0
    score_count = 0
    
    for student in students:
        # 构建完整的学生数据（包含头像等前端需要的信息）
        student_data = {
            "id": student.id,
            "name": student.name,
            "avatar": student.avatar,  # 包含头像信息
            "grade": student.grade.value,
            "school": student.school,
            "class_name": student.class_name,
            "total_homework": student.total_homework,
            "completed_homework": student.completed_homework,
            "average_score": float(student.average_score) if student.average_score else 0.0,
            "todayScore": float(student.average_score) if student.average_score else 0,  # 前端需要的今日分数
            "status": "已完成" if student.completed_homework > 0 else "未开始"  # 前端需要的状态
        }
        dashboard_data["children"].append(student_data)
        
        # 兼容性：保持原有的children_summary结构
        student_summary = {
            "student_id": student.id,
            "name": student.name,
            "grade": student.grade.value,
            "homework_progress": {
                "total": student.total_homework,
                "completed": student.completed_homework,
                "completion_rate": (student.completed_homework / student.total_homework * 100) if student.total_homework > 0 else 0
            },
            "average_score": float(student.average_score) if student.average_score else 0.0,
            "last_activity": student.updated_at.isoformat()
        }
        dashboard_data["children_summary"].append(student_summary)
        
        total_homework += student.total_homework
        total_completed += student.completed_homework
        if student.average_score:
            total_score += float(student.average_score)
            score_count += 1
        
        if student.updated_at and (datetime.now() - student.updated_at).days <= 7:
            dashboard_data["overall_stats"]["active_children"] += 1
    
    # 计算总体统计
    dashboard_data["overall_stats"]["total_homework"] = total_homework
    dashboard_data["overall_stats"]["completed_homework"] = total_completed
    if score_count > 0:
        dashboard_data["overall_stats"]["average_score"] = total_score / score_count
    
    # 添加一些模拟的最近活动和提醒
    dashboard_data["recent_activities"] = [
        {"time": "2小时前", "activity": "孩子完成了数学作业", "student": "小明"},
        {"time": "昨天", "activity": "语文测试成绩：85分", "student": "小红"},
        {"time": "2天前", "activity": "英语单词练习完成", "student": "小明"}
    ]
    
    dashboard_data["alerts"] = [
        {"type": "reminder", "message": "小明今天还没有完成作业"},
        {"type": "achievement", "message": "小红连续一周保持高分！"},
        {"type": "suggestion", "message": "建议增加数学练习时间"}
    ]
    
    return ResponseModel(
        code=200,
        message="获取仪表板数据成功",
        data=dashboard_data
    )


from datetime import datetime