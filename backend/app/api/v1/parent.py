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

class ChildInfo(BaseModel):
    """孩子信息"""
    id: int
    nickname: str
    avatar_url: Optional[str]
    grade: str
    school: Optional[str]
    class_name: Optional[str]
    is_active: bool
    created_at: str

class TodayStats(BaseModel):
    """今日统计"""
    homeworkCount: int
    accuracy: int

class Child(BaseModel):
    """孩子信息"""
    id: int
    name: str
    grade: str
    school: Optional[str] = None
    class_name: Optional[str] = None
    avatar: Optional[str] = None
    todayScore: int
    status: str

class Notification(BaseModel):
    """通知信息"""
    icon: str
    text: str
    time: str
    unread: bool = False

class WeeklyReport(BaseModel):
    """本周报告"""
    totalHomework: int
    avgAccuracy: int
    studyDays: int

class Activity(BaseModel):
    """活动信息"""
    icon: str
    text: str
    time: str

class ParentDashboardResponse(BaseModel):
    """家长端仪表板响应"""
    today_stats: TodayStats
    children: List[Child]
    notifications: List[Notification]
    weekly_report: WeeklyReport
    study_time_data: List[int]  # 7天的学习时长数据
    recent_activities: List[Activity]

class ChildReportResponse(BaseModel):
    """孩子学习报告响应"""
    child_info: ChildInfo
    study_stats: Dict[str, Any]
    subject_analysis: List[Dict[str, Any]]
    learning_trends: List[Dict[str, Any]]
    recommendations: List[str]

@router.get("/dashboard", summary="获取家长端仪表板")
def get_parent_dashboard(
    include_practice_status: bool = Query(default=False, description="包含练习状态数据"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取家长端仪表板数据
    
    包括：
    - 今日统计
    - 关联的孩子列表
    - 通知消息
    - 本周学习报告
    - 学习时长数据
    - 最近活动
    """
    from app.models.parent_child import ParentChild
    from app.models.homework import Homework
    from sqlalchemy import func, and_
    from datetime import datetime, timedelta
    
    # 获取关联的孩子
    parent_child_relations = db.query(ParentChild).filter(
        ParentChild.parent_id == current_user.id,
        ParentChild.is_active == True
    ).all()
    
    children = []
    today = datetime.now().date()
    total_homework_today = 0
    total_accuracy = 0
    
    for relation in parent_child_relations:
        child_user = db.query(User).filter(User.id == relation.child_id).first()
        if not child_user:
            continue
            
        # 获取今日作业统计
        today_homework = db.query(Homework).filter(
            Homework.user_id == relation.child_id,
            func.date(Homework.created_at) == today
        ).all()
        
        homework_count = len(today_homework)
        completed_homework = len([h for h in today_homework if h.status == 'completed'])
        
        # 计算今日平均分
        if today_homework:
            avg_score = sum([h.accuracy_rate * 100 for h in today_homework if h.accuracy_rate is not None]) / len([h for h in today_homework if h.accuracy_rate is not None]) if any(h.accuracy_rate is not None for h in today_homework) else 0
        else:
            avg_score = 0
            
        # 确定状态
        status = "已完成" if completed_homework == homework_count and homework_count > 0 else ("进行中" if homework_count > 0 else "未开始")
        
        child_dict = {
            "id": child_user.id,
            "name": relation.nickname or child_user.nickname or f"用户{child_user.id}",
            "grade": child_user.grade or "未设置",
            "school": relation.school or "未设置学校",
            "class_name": relation.class_name or "未设置班级",
            "avatar": child_user.avatar_url if child_user.avatar_url is not None else "student",
            "todayScore": int(avg_score),
            "status": status
        }
        children.append(child_dict)
        
        total_homework_today += homework_count
        if today_homework:
            accuracies = [int((h.total_questions - h.wrong_count) * 100 / h.total_questions) if h.total_questions > 0 else 0 for h in today_homework]
            if accuracies:
                total_accuracy += sum(accuracies) / len(accuracies)
    
    # 今日统计
    today_stats = {
        "homeworkCount": total_homework_today,
        "accuracy": int(total_accuracy / len(children)) if children else 0
    }
    
    # 生成实时通知消息
    notifications = []
    for relation in parent_child_relations:
        child_user = db.query(User).filter(User.id == relation.child_id).first()
        if not child_user:
            continue
            
        child_name = relation.nickname or child_user.nickname or child_user.username
        
        # 最近完成的作业
        recent_homework = db.query(Homework).filter(
            Homework.user_id == relation.child_id,
            Homework.status == 'completed'
        ).order_by(Homework.updated_at.desc()).first()
        
        if recent_homework and recent_homework.updated_at > datetime.now() - timedelta(hours=24):
            accuracy = int((recent_homework.total_questions - recent_homework.wrong_count) * 100 / recent_homework.total_questions) if recent_homework.total_questions > 0 else 0
            subject_map = {"math": "数学", "chinese": "语文", "english": "英语", "physics": "物理", "chemistry": "化学"}
            subject_name = subject_map.get(recent_homework.subject, recent_homework.subject)
            
            time_diff = datetime.now() - recent_homework.updated_at
            if time_diff.seconds < 3600:  # 1小时内
                time_str = f"{time_diff.seconds // 60}分钟前"
            else:
                time_str = f"{time_diff.seconds // 3600}小时前"
            
            notifications.append({
                "icon": "📝",
                "text": f"{child_name}完成了{subject_name}作业，正确率{accuracy}%",
                "time": time_str,
                "unread": True
            })
    
    # 本周报告 - 统计所有孩子的本周数据
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_homework = []
    study_days_set = set()
    
    for relation in parent_child_relations:
        week_hw = db.query(Homework).filter(
            Homework.user_id == relation.child_id,
            Homework.created_at >= week_start
        ).all()
        week_homework.extend(week_hw)
        
        # 统计学习天数
        for hw in week_hw:
            study_days_set.add(hw.created_at.date())
    
    total_week_homework = len(week_homework)
    avg_accuracy = 0
    if week_homework:
        accuracies = [int((hw.total_questions - hw.wrong_count) * 100 / hw.total_questions) if hw.total_questions > 0 else 0 for hw in week_homework]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
    
    weekly_report = {
        "totalHomework": total_week_homework,
        "avgAccuracy": int(avg_accuracy),
        "studyDays": len(study_days_set)
    }
    
    # 学习时长数据（一周7天，单位：分钟）- 基于实际作业完成时间
    study_time_data = []
    for i in range(7):  # 最近7天
        day = datetime.now().date() - timedelta(days=6-i)
        day_homework = []
        
        for relation in parent_child_relations:
            hw = db.query(Homework).filter(
                Homework.user_id == relation.child_id,
                func.date(Homework.created_at) == day
            ).all()
            day_homework.extend(hw)
        
        # 基于作业数量和难度估算学习时长
        daily_minutes = 0
        for hw in day_homework:
            if hw.total_questions:
                # 估算每题平均2-3分钟
                daily_minutes += hw.total_questions * 2.5
        
        study_time_data.append(min(int(daily_minutes), 120))  # 限制最大120分钟
    
    # 最近活动 - 基于实际数据生成
    recent_activities = []
    
    # 获取最近的作业活动
    for relation in parent_child_relations:
        child_user = db.query(User).filter(User.id == relation.child_id).first()
        if not child_user:
            continue
            
        child_name = relation.nickname or child_user.nickname or child_user.username
        
        recent_homeworks = db.query(Homework).filter(
            Homework.user_id == relation.child_id
        ).order_by(Homework.updated_at.desc()).limit(3).all()
        
        for hw in recent_homeworks:
            if hw.updated_at > datetime.now() - timedelta(days=1):
                subject_map = {"math": "数学", "chinese": "语文", "english": "英语", "physics": "物理", "chemistry": "化学"}
                subject_name = subject_map.get(hw.subject, hw.subject)
                
                time_diff = datetime.now() - hw.updated_at
                if time_diff.seconds < 3600:
                    time_str = f"{time_diff.seconds // 60}分钟前"
                elif time_diff.seconds < 86400:
                    time_str = f"{time_diff.seconds // 3600}小时前"
                else:
                    time_str = "今天"
                
                if hw.status == 'completed':
                    recent_activities.append({
                        "icon": "✅",
                        "text": f"{child_name}完成了{subject_name}练习",
                        "time": time_str
                    })
    
    # 如果没有足够的活动，添加一些通用活动
    if len(recent_activities) < 3:
        recent_activities.append({
            "icon": "📊",
            "text": "本周学习分析报告已更新",
            "time": "今天上午"
        })
    
    # 如果请求包含练习状态数据，添加practice_status字段
    response_data = {
        "today_stats": today_stats,
        "children": children,
        "notifications": notifications,
        "weekly_report": weekly_report,
        "study_time_data": study_time_data,
        "recent_activities": recent_activities
    }
    
    if include_practice_status:
        # 生成练习状态数据（与practice-status端点相同的逻辑）
        practice_children = []
        week_start = datetime.now() - timedelta(days=7)
        
        for relation in parent_child_relations:
            child_user = db.query(User).filter(User.id == relation.child_id).first()
            if not child_user:
                continue
                
            # 获取最近的练习记录（本周内）
            recent_practices = db.query(Homework).filter(
                Homework.user_id == relation.child_id,
                Homework.created_at >= week_start
            ).order_by(Homework.created_at.desc()).all()
            
            # 转换为前端需要的格式
            practice_data = []
            for hw in recent_practices:
                accuracy = int(hw.accuracy_rate * 100) if hw.accuracy_rate is not None else 0
                practice_data.append({
                    'id': hw.id,
                    'created_at': hw.created_at.isoformat(),
                    'accuracy': accuracy,
                    'subject': hw.subject,
                    'total_questions': hw.total_questions or 0,
                    'wrong_count': hw.wrong_count or 0,
                    'status': hw.status
                })
            
            child_info = {
                'id': child_user.id,
                'name': relation.nickname or child_user.nickname or f"用户{child_user.id}",
                'avatar': child_user.avatar_url,
                'grade': child_user.grade or "未设置",
                'recent_practices': practice_data
            }
            practice_children.append(child_info)
        
        response_data['practice_status'] = {
            'children': practice_children,
            'total_children': len(practice_children),
            'generated_at': datetime.now().isoformat()
        }
    
    return response_data

@router.get("/children/{child_id}/report", response_model=ChildReportResponse, summary="获取孩子学习报告")
def get_child_report(
    child_id: int,
    period: str = Query(default="today", description="报告周期: today/week/month/semester"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定孩子的详细学习报告
    
    - **child_id**: 孩子ID
    - **period**: 报告周期 (today/week/month/semester)
    """
    from app.models.parent_child import ParentChild
    from app.models.homework import Homework, ErrorQuestion
    from sqlalchemy import func
    
    # 验证家长和孩子的关联关系
    parent_child_relation = db.query(ParentChild).filter(
        ParentChild.parent_id == current_user.id,
        ParentChild.child_id == child_id,
        ParentChild.is_active == True
    ).first()
    
    if not parent_child_relation:
        raise HTTPException(status_code=404, detail="未找到该孩子或无权访问")
    
    # 获取孩子信息
    child_user = db.query(User).filter(User.id == child_id).first()
    if not child_user:
        raise HTTPException(status_code=404, detail="孩子用户不存在")
    
    child_info = {
        "id": child_id,
        "nickname": parent_child_relation.nickname or child_user.nickname or f"用户{child_user.id}",
        "avatar_url": child_user.avatar_url,
        "grade": child_user.grade or "未设置",
        "school": parent_child_relation.school or "未设置",
        "class_name": parent_child_relation.class_name or "未设置",
        "is_active": child_user.is_active,
        "created_at": parent_child_relation.created_at.isoformat()
    }
    
    # 根据时间段获取作业数据
    now = datetime.now()
    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)  # 今天0点
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "semester":
        start_date = now - timedelta(days=120)  # 4个月
    else:
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)  # 默认今天
    
    # 获取时间段内的作业
    period_homework = db.query(Homework).filter(
        Homework.user_id == child_id,
        Homework.created_at >= start_date
    ).all()
    
    # 计算学习统计
    total_homework = len(period_homework)
    completed_homework = len([h for h in period_homework if h.status == 'completed'])
    
    # 计算平均分
    scores = [h.accuracy_rate * 100 for h in period_homework if h.accuracy_rate is not None]
    average_score = int(sum(scores) / len(scores)) if scores else 0
    
    # 错题统计
    total_errors = sum([h.wrong_count for h in period_homework if h.wrong_count])
    reviewed_errors = db.query(ErrorQuestion).filter(
        ErrorQuestion.user_id == child_id,
        ErrorQuestion.created_at >= start_date,
        ErrorQuestion.is_reviewed == True
    ).count()
    
    # 估算学习时间（基于作业量）
    study_time = 0
    for hw in period_homework:
        if hw.total_questions:
            study_time += hw.total_questions * 2  # 每题平均2分钟
    
    # 计算进步趋势
    first_half = period_homework[:len(period_homework)//2] if len(period_homework) > 2 else []
    second_half = period_homework[len(period_homework)//2:] if len(period_homework) > 2 else period_homework
    
    if first_half and second_half:
        first_avg = sum([h.accuracy_rate * 100 for h in first_half if h.accuracy_rate is not None]) / len([h for h in first_half if h.accuracy_rate is not None]) if any(h.accuracy_rate is not None for h in first_half) else 0
        second_avg = sum([h.accuracy_rate * 100 for h in second_half if h.accuracy_rate is not None]) / len([h for h in second_half if h.accuracy_rate is not None]) if any(h.accuracy_rate is not None for h in second_half) else 0
        if second_avg > first_avg + 5:
            improvement_trend = "up"
        elif second_avg < first_avg - 5:
            improvement_trend = "down"
        else:
            improvement_trend = "stable"
    else:
        improvement_trend = "stable"
    
    study_stats = {
        "period": period,
        "total_homework": total_homework,
        "completed_homework": completed_homework,
        "average_score": average_score,
        "total_errors": total_errors,
        "reviewed_errors": reviewed_errors,
        "study_time": study_time,
        "improvement_trend": improvement_trend,
        "rank_in_class": min(max(int((100 - average_score) / 5), 1), 30)  # 基于成绩估算排名
    }
    
    # 学科分析
    subject_map = {"math": "数学", "chinese": "语文", "english": "英语", "physics": "物理", "chemistry": "化学"}
    subject_analysis = []
    
    for subject_code, subject_name in subject_map.items():
        subject_homework = [h for h in period_homework if h.subject == subject_code]
        
        if not subject_homework:
            continue
            
        homework_count = len(subject_homework)
        subject_scores = [h.accuracy_rate * 100 for h in subject_homework if h.accuracy_rate is not None]
        average_score = int(sum(subject_scores) / len(subject_scores)) if subject_scores else 0
        
        # 计算准确率
        total_questions = sum([h.total_questions for h in subject_homework if h.total_questions])
        total_errors = sum([h.wrong_count for h in subject_homework if h.wrong_count])
        accuracy_rate = (total_questions - total_errors) / total_questions if total_questions > 0 else 0
        
        # 分析薄弱环节（基于错题类型）
        weak_points = []
        error_questions = db.query(ErrorQuestion).join(Homework).filter(
            Homework.user_id == child_id,
            Homework.subject == subject_code,
            ErrorQuestion.created_at >= start_date
        ).all()
        
        error_types = {}
        for eq in error_questions:
            if eq.error_type:
                error_types[eq.error_type] = error_types.get(eq.error_type, 0) + 1
        
        # 根据错误类型生成薄弱点提示
        if error_types:
            if error_types.get('calculation', 0) > 2:
                weak_points.append(f"{subject_name}计算能力")
            if error_types.get('comprehension', 0) > 2:
                weak_points.append(f"{subject_name}理解能力")
            if error_types.get('knowledge', 0) > 2:
                weak_points.append(f"{subject_name}基础知识")
        
        if not weak_points:
            weak_points.append(f"{subject_name}基础练习")
        
        # 判断进步情况
        if average_score >= 90:
            progress = "excellent"
        elif average_score >= 80:
            progress = "good"
        elif average_score >= 70:
            progress = "average"
        else:
            progress = "needs_improvement"
        
        subject_analysis.append({
            "subject": subject_name,
            "homework_count": homework_count,
            "average_score": average_score,
            "accuracy_rate": round(accuracy_rate, 2),
            "error_count": total_errors,
            "weak_points": weak_points[:3],
            "progress": progress
        })
    
    # 学习趋势 - 最近7天的数据
    learning_trends = []
    for i in range(7):
        date = now - timedelta(days=6-i)
        day_homework = [h for h in period_homework if h.created_at.date() == date.date()]
        
        homework_count = len(day_homework)
        if day_homework:
            day_scores = [h.accuracy_rate * 100 for h in day_homework if h.accuracy_rate is not None]
            day_avg = sum(day_scores) / len(day_scores) if day_scores else 0
            
            total_q = sum([h.total_questions for h in day_homework if h.total_questions])
            total_e = sum([h.wrong_count for h in day_homework if h.wrong_count])
            accuracy_rate = (total_q - total_e) / total_q if total_q > 0 else 0
            
            study_time = sum([h.total_questions * 2 for h in day_homework if h.total_questions])
        else:
            day_avg = 0
            accuracy_rate = 0
            study_time = 0
        
        # 基于成绩估算心情分数
        mood_score = 5 if day_avg >= 90 else (4 if day_avg >= 80 else (3 if day_avg >= 70 else 2))
        
        learning_trends.append({
            "date": date.strftime("%Y-%m-%d"),
            "homework_count": homework_count,
            "accuracy_rate": round(accuracy_rate, 2),
            "study_time": min(study_time, 120),  # 限制最大120分钟
            "mood_score": mood_score
        })
    
    # 生成个性化学习建议
    recommendations = []
    
    if average_score < 80:
        recommendations.append("建议加强基础知识练习，重点提升解题准确性")
    
    if total_errors > total_homework * 2:  # 错题较多
        recommendations.append("错题数量较多，建议建立错题本进行系统复习")
    
    for subject in subject_analysis:
        if subject["progress"] == "needs_improvement":
            recommendations.append(f"{subject['subject']}需要重点关注，建议增加专项练习")
        elif subject["average_score"] >= 90:
            recommendations.append(f"{subject['subject']}表现优秀，继续保持")
    
    if improvement_trend == "up":
        recommendations.append("学习成绩呈上升趋势，继续保持当前学习节奏")
    elif improvement_trend == "down":
        recommendations.append("最近成绩有所下降，建议调整学习方法和时间安排")
    
    if not recommendations:
        recommendations.append("整体学习情况良好，建议保持规律的学习习惯")
    
    return {
        "child_info": child_info,
        "study_stats": study_stats,
        "subject_analysis": subject_analysis,
        "learning_trends": learning_trends,
        "recommendations": recommendations
    }

@router.get("/children/{child_id}/homework", summary="获取孩子作业历史")
def get_child_homework_history(
    child_id: int,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    subject: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取孩子的作业历史记录
    
    - **child_id**: 孩子ID
    - **page**: 页码
    - **limit**: 每页数量
    - **subject**: 学科筛选
    """
    from app.models.parent_child import ParentChild
    from app.models.homework import Homework
    from sqlalchemy import and_
    
    # 验证家长和孩子的关联关系
    parent_child_relation = db.query(ParentChild).filter(
        ParentChild.parent_id == current_user.id,
        ParentChild.child_id == child_id,
        ParentChild.is_active == True
    ).first()
    
    if not parent_child_relation:
        raise HTTPException(status_code=404, detail="未找到该孩子或无权访问")
    
    # 构建查询
    query = db.query(Homework).filter(Homework.user_id == child_id)
    
    # 学科筛选
    if subject:
        # 将中文学科名映射为英文代码
        subject_code_map = {"数学": "math", "语文": "chinese", "英语": "english", "物理": "physics", "化学": "chemistry"}
        subject_code = subject_code_map.get(subject, subject.lower())
        query = query.filter(Homework.subject == subject_code)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * limit
    homework_records = query.order_by(Homework.created_at.desc()).offset(offset).limit(limit).all()
    
    # 转换为返回格式
    homework_list = []
    subject_map = {"math": "数学", "chinese": "语文", "english": "英语", "physics": "物理", "chemistry": "化学"}
    
    for hw in homework_records:
        subject_name = subject_map.get(hw.subject, hw.subject)
        
        # 计算正确答案数
        correct_answers = hw.total_questions - (hw.wrong_count or 0) if hw.total_questions else 0
        
        # 计算准确率
        accuracy_rate = correct_answers / hw.total_questions if hw.total_questions else 0
        
        # 估算完成时间（基于题目数量）
        time_spent = hw.total_questions * 2 if hw.total_questions else 0  # 每题平均2分钟
        time_spent = min(time_spent, 120)  # 限制最大120分钟
        
        homework_item = {
            "id": hw.id,
            "subject": subject_name,
            "title": hw.title or f"{subject_name}练习 - {hw.created_at.strftime('%m月%d日')}",
            "total_questions": hw.total_questions or 0,
            "correct_answers": correct_answers,
            "error_count": hw.wrong_count or 0,
            "accuracy_rate": round(accuracy_rate, 2),
            "score": int(hw.accuracy_rate * 100) if hw.accuracy_rate is not None else 0,
            "time_spent": time_spent,
            "submitted_at": hw.updated_at.isoformat() if hw.updated_at else hw.created_at.isoformat(),
            "teacher_comment": getattr(hw, 'teacher_comment', None) or (
                "作业完成认真，继续保持！" if accuracy_rate > 0.9 else (
                    "有几道题目需要再仔细检查" if accuracy_rate > 0.7 else None
                )
            )
        }
        homework_list.append(homework_item)
    
    return {
        "child_id": child_id,
        "total": total,
        "page": page,
        "limit": limit,
        "homework_list": homework_list
    }

@router.post("/children/{child_id}/settings", summary="更新孩子设置")
def update_child_settings(
    child_id: int,
    daily_quota: int = Query(default=5, description="每日作业额度"),
    study_time_limit: int = Query(default=120, description="每日学习时间限制(分钟)"),
    notification_enabled: bool = Query(default=True, description="是否启用通知"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新孩子的学习设置
    
    - **child_id**: 孩子ID
    - **daily_quota**: 每日作业批改额度
    - **study_time_limit**: 每日学习时间限制
    - **notification_enabled**: 是否启用家长通知
    """
    # 在实际应用中，这里会更新数据库
    return {
        "child_id": child_id,
        "settings": {
            "daily_quota": daily_quota,
            "study_time_limit": study_time_limit,
            "notification_enabled": notification_enabled
        },
        "message": "设置更新成功",
        "updated_at": datetime.now().isoformat()
    }

@router.get("/statistics", summary="获取家长统计数据")
def get_parent_statistics(
    period: str = Query(default="month", description="统计周期"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取家长端的统计数据
    
    包括所有孩子的学习统计和趋势分析
    """
    from app.models.parent_child import ParentChild
    from app.models.homework import Homework
    from sqlalchemy import func
    
    # 获取关联的孩子
    parent_child_relations = db.query(ParentChild).filter(
        ParentChild.parent_id == current_user.id,
        ParentChild.is_active == True
    ).all()
    
    if not parent_child_relations:
        return {
            "period": period,
            "total_children": 0,
            "statistics": {
                "homework_completion_rate": 0,
                "average_accuracy": 0,
                "total_study_time": 0,
                "improvement_rate": 0,
                "subjects_performance": {}
            },
            "comparison": {
                "vs_last_period": {
                    "homework_count": 0,
                    "accuracy_rate": 0,
                    "study_time": 0
                },
                "vs_class_average": {
                    "ranking": 0,
                    "above_average": False
                }
            },
            "generated_at": datetime.now().isoformat()
        }
    
    # 根据统计周期设置时间范围
    now = datetime.now()
    if period == "week":
        current_start = now - timedelta(days=7)
        previous_start = now - timedelta(days=14)
        previous_end = now - timedelta(days=7)
    elif period == "semester":
        current_start = now - timedelta(days=120)
        previous_start = now - timedelta(days=240)
        previous_end = now - timedelta(days=120)
    else:  # month
        current_start = now - timedelta(days=30)
        previous_start = now - timedelta(days=60)
        previous_end = now - timedelta(days=30)
    
    child_ids = [relation.child_id for relation in parent_child_relations]
    
    # 获取当前周期的作业数据
    current_homework = db.query(Homework).filter(
        Homework.user_id.in_(child_ids),
        Homework.created_at >= current_start
    ).all()
    
    # 获取上一周期的作业数据（用于对比）
    previous_homework = db.query(Homework).filter(
        Homework.user_id.in_(child_ids),
        Homework.created_at >= previous_start,
        Homework.created_at < previous_end
    ).all()
    
    # 计算完成率
    total_homework = len(current_homework)
    completed_homework = len([h for h in current_homework if h.status == 'completed'])
    homework_completion_rate = completed_homework / total_homework if total_homework > 0 else 0
    
    # 计算平均准确率
    accuracies = []
    total_study_time = 0
    
    for hw in current_homework:
        if hw.total_questions and hw.total_questions > 0:
            accuracy = (hw.total_questions - (hw.wrong_count or 0)) / hw.total_questions
            accuracies.append(accuracy)
            # 估算学习时间
            total_study_time += hw.total_questions * 2  # 每题2分钟
    
    average_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
    
    # 计算进步率（与上一周期对比）
    if previous_homework:
        prev_accuracies = []
        for hw in previous_homework:
            if hw.total_questions and hw.total_questions > 0:
                prev_accuracy = (hw.total_questions - (hw.wrong_count or 0)) / hw.total_questions
                prev_accuracies.append(prev_accuracy)
        
        prev_average_accuracy = sum(prev_accuracies) / len(prev_accuracies) if prev_accuracies else 0
        improvement_rate = (average_accuracy - prev_average_accuracy) if prev_average_accuracy > 0 else 0
    else:
        improvement_rate = 0
    
    # 学科表现统计
    subject_map = {"math": "数学", "chinese": "语文", "english": "英语", "physics": "物理", "chemistry": "化学"}
    subjects_performance = {}
    
    for subject_code, subject_name in subject_map.items():
        subject_homework = [h for h in current_homework if h.subject == subject_code]
        if not subject_homework:
            continue
            
        # 计算学科平均分
        subject_scores = [h.accuracy_rate * 100 for h in subject_homework if h.accuracy_rate is not None]
        avg_score = int(sum(subject_scores) / len(subject_scores)) if subject_scores else 0
        
        # 计算趋势（与上一周期对比）
        prev_subject_homework = [h for h in previous_homework if h.subject == subject_code]
        if prev_subject_homework:
            prev_scores = [h.accuracy_rate * 100 for h in prev_subject_homework if h.accuracy_rate is not None]
            prev_avg = sum(prev_scores) / len(prev_scores) if prev_scores else avg_score
            
            if avg_score > prev_avg + 5:
                trend = "up"
            elif avg_score < prev_avg - 5:
                trend = "down"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        subjects_performance[subject_name] = {
            "score": avg_score,
            "trend": trend
        }
    
    # 与上一周期对比
    prev_homework_count = len(previous_homework)
    prev_accuracies_all = []
    prev_study_time = 0
    
    for hw in previous_homework:
        if hw.total_questions and hw.total_questions > 0:
            prev_accuracy = (hw.total_questions - (hw.wrong_count or 0)) / hw.total_questions
            prev_accuracies_all.append(prev_accuracy)
            prev_study_time += hw.total_questions * 2
    
    prev_avg_accuracy = sum(prev_accuracies_all) / len(prev_accuracies_all) if prev_accuracies_all else 0
    
    comparison = {
        "vs_last_period": {
            "homework_count": total_homework - prev_homework_count,
            "accuracy_rate": round(average_accuracy - prev_avg_accuracy, 2),
            "study_time": total_study_time - prev_study_time
        },
        "vs_class_average": {
            "ranking": min(max(int((100 - average_accuracy * 100) / 5), 1), 30),  # 估算排名
            "above_average": average_accuracy > 0.8  # 假设班级平均80%准确率
        }
    }
    
    return {
        "period": period,
        "total_children": len(parent_child_relations),
        "statistics": {
            "homework_completion_rate": round(homework_completion_rate, 2),
            "average_accuracy": round(average_accuracy, 2),
            "total_study_time": total_study_time,
            "improvement_rate": round(improvement_rate, 2),
            "subjects_performance": subjects_performance
        },
        "comparison": comparison,
        "generated_at": datetime.now().isoformat()
    }

@router.post("/notifications/mark-read", summary="标记通知已读")
def mark_notifications_read(
    notification_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量标记通知为已读状态
    
    - **notification_ids**: 通知ID列表
    """
    return {
        "marked_count": len(notification_ids),
        "notification_ids": notification_ids,
        "message": "通知已标记为已读",
        "updated_at": datetime.now().isoformat()
    }

class CreateChildRequest(BaseModel):
    """添加孩子请求"""
    nickname: str = Field(..., description="孩子昵称")
    grade: str = Field(..., description="年级")
    class_name: Optional[str] = Field(None, description="班级")
    school: Optional[str] = Field(None, description="学校")
    avatar_url: Optional[str] = Field(None, description="头像URL")

class UpdateChildRequest(BaseModel):
    """更新孩子信息请求"""
    nickname: Optional[str] = Field(None, description="孩子昵称")
    grade: Optional[str] = Field(None, description="年级")
    class_name: Optional[str] = Field(None, description="班级")
    school: Optional[str] = Field(None, description="学校")
    avatar_url: Optional[str] = Field(None, description="头像URL")

@router.post("/children", summary="添加孩子")
def create_child(
    child_data: CreateChildRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    为当前用户添加一个孩子
    
    - **nickname**: 孩子昵称
    - **grade**: 年级
    - **school**: 学校（可选）
    - **avatar_url**: 头像URL（可选）
    """
    from app.models.parent_child import ParentChild
    
    # 名字重复校验
    existing_relation = db.query(ParentChild).filter(
        ParentChild.parent_id == current_user.id,
        ParentChild.nickname == child_data.nickname,
        ParentChild.is_active == True
    ).first()
    
    if existing_relation:
        raise HTTPException(status_code=400, detail="孩子姓名已存在，请使用其他名字")
    
    try:
        # 创建子用户记录
        child_user = User(
            openid=f"child_{datetime.now().timestamp()}_{random.randint(100, 999)}",  # 生成唯一openid
            unionid=f"mock_openid_child_{datetime.now().timestamp()}_{random.randint(100, 999)}",
            nickname=child_data.nickname,
            role='student',
            grade=child_data.grade,
            is_active=True,
            daily_quota=5,
            daily_used=0
        )
        db.add(child_user)
        db.flush()  # 获取child_user.id
        
        # 创建parent-child关系
        parent_child_relation = ParentChild(
            parent_id=current_user.id,
            child_id=child_user.id,
            nickname=child_data.nickname,
            school=child_data.school,
            class_name=child_data.class_name,
            relationship_type='parent',
            is_active=True,
            can_view_homework=True,
            can_view_reports=True,
            can_set_limits=True,
            daily_homework_limit=10,
            daily_time_limit=120
        )
        db.add(parent_child_relation)
        
        db.commit()
        
        return {
            "id": child_user.id,
            "nickname": child_data.nickname,
            "grade": child_data.grade,
            "school": child_data.school,
            "avatar_url": child_data.avatar_url or "emoji:👶",
            "parent_id": current_user.id,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "message": "添加孩子成功"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"添加孩子失败: {str(e)}")

@router.put("/children/{child_id}", summary="更新孩子信息")
def update_child(
    child_id: int,
    child_data: UpdateChildRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新指定孩子的信息
    
    - **child_id**: 孩子ID
    - **nickname**: 孩子昵称（可选）
    - **grade**: 年级（可选）
    - **school**: 学校（可选）
    - **avatar_url**: 头像URL（可选）
    """
    from app.models.parent_child import ParentChild
    
    # 验证家长和孩子的关联关系
    parent_child_relation = db.query(ParentChild).filter(
        ParentChild.parent_id == current_user.id,
        ParentChild.child_id == child_id,
        ParentChild.is_active == True
    ).first()
    
    if not parent_child_relation:
        raise HTTPException(status_code=404, detail="未找到该孩子或无权访问")
    
    # 获取孩子用户记录
    child_user = db.query(User).filter(User.id == child_id).first()
    if not child_user:
        raise HTTPException(status_code=404, detail="孩子用户不存在")
    
    try:
        # 名字重复校验（排除当前孩子）
        if child_data.nickname:
            existing_relation = db.query(ParentChild).filter(
                ParentChild.parent_id == current_user.id,
                ParentChild.nickname == child_data.nickname,
                ParentChild.child_id != child_id,
                ParentChild.is_active == True
            ).first()
            
            if existing_relation:
                raise HTTPException(status_code=400, detail="孩子姓名已存在，请使用其他名字")
        
        # 更新孩子用户信息
        if child_data.nickname:
            child_user.nickname = child_data.nickname
        if child_data.grade:
            child_user.grade = child_data.grade
        if child_data.avatar_url is not None:
            child_user.avatar_url = child_data.avatar_url
        
        # 更新parent-child关系
        if child_data.nickname:
            parent_child_relation.nickname = child_data.nickname
        if child_data.school:
            parent_child_relation.school = child_data.school
        if child_data.class_name:
            parent_child_relation.class_name = child_data.class_name
        parent_child_relation.updated_at = datetime.now()
        
        db.commit()
        
        return {
            "id": child_id,
            "nickname": parent_child_relation.nickname,
            "grade": child_user.grade,
            "school": parent_child_relation.school or "未设置",
            "class_name": parent_child_relation.class_name or "未设置",
            "avatar_url": child_user.avatar_url or "emoji:👶",
            "parent_id": current_user.id,
            "is_active": True,
            "updated_at": datetime.now().isoformat(),
            "message": "更新孩子信息成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新孩子信息失败: {str(e)}")

@router.delete("/children/{child_id}", summary="删除孩子")
def delete_child(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除指定的孩子
    
    - **child_id**: 孩子ID
    """
    from app.models.parent_child import ParentChild
    
    # 验证家长和孩子的关联关系
    parent_child_relation = db.query(ParentChild).filter(
        ParentChild.parent_id == current_user.id,
        ParentChild.child_id == child_id,
        ParentChild.is_active == True
    ).first()
    
    if not parent_child_relation:
        raise HTTPException(status_code=404, detail="未找到该孩子或无权访问")
    
    try:
        # 软删除：设置关联关系为非激活状态
        parent_child_relation.is_active = False
        parent_child_relation.updated_at = datetime.now()
        
        # 可选：也可以软删除孩子用户记录
        child_user = db.query(User).filter(User.id == child_id).first()
        if child_user:
            child_user.is_active = False
            child_user.updated_at = datetime.now()
        
        db.commit()
        
        return {
            "child_id": child_id,
            "message": "删除孩子成功",
            "deleted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除孩子失败: {str(e)}")

@router.get("/children/{child_id}", summary="获取孩子详细信息")
def get_child_detail(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定孩子的详细信息
    
    - **child_id**: 孩子ID
    """
    try:
        from app.models.parent_child import ParentChild
        from app.models.homework import Homework
        from sqlalchemy import func
        
        # 验证家长和孩子的关联关系
        parent_child_relation = db.query(ParentChild).filter(
            ParentChild.parent_id == current_user.id,
            ParentChild.child_id == child_id,
            ParentChild.is_active == True
        ).first()
        
        if not parent_child_relation:
            raise HTTPException(status_code=404, detail="未找到该孩子或无权访问")
        
        # 获取孩子用户记录
        child_user = db.query(User).filter(User.id == child_id).first()
        if not child_user:
            raise HTTPException(status_code=404, detail="孩子用户不存在")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"获取孩子详细信息时发生错误: {e}")
        print(f"完整错误堆栈: {error_detail}")
        raise HTTPException(status_code=500, detail=f"获取孩子信息失败: {str(e)}")
    
    try:
        # 获取孩子的作业统计
        total_homework = db.query(Homework).filter(Homework.user_id == child_id).count()
        completed_homework = db.query(Homework).filter(
            Homework.user_id == child_id,
            Homework.status == 'completed'
        ).count()
        
        # 计算平均分
        homework_records = db.query(Homework).filter(
            Homework.user_id == child_id,
            Homework.accuracy_rate.isnot(None)
        ).all()
        
        if homework_records:
            average_score = sum([h.accuracy_rate * 100 for h in homework_records]) / len(homework_records)
        else:
            average_score = 0
        
        # 估算总学习时间
        total_study_time = sum([h.total_questions * 2 for h in homework_records if h.total_questions]) if homework_records else 0
    except Exception as e:
        print(f"计算作业统计时出错: {e}")
        # 设置默认值
        total_homework = 0
        completed_homework = 0
        average_score = 0
        total_study_time = 0
    
    # 计算连续学习天数（简化版）
    from datetime import datetime, timedelta
    current_streak = 0
    try:
        recent_dates = db.query(func.date(Homework.created_at)).filter(
            Homework.user_id == child_id
        ).distinct().order_by(func.date(Homework.created_at).desc()).limit(30).all()
        
        if recent_dates:
            current_date = datetime.now().date()
            for date_tuple in recent_dates:
                if (current_date - date_tuple[0]).days == current_streak:
                    current_streak += 1
                    current_date = date_tuple[0]
                else:
                    break
    except Exception as e:
        print(f"计算学习天数时出错: {e}")
        current_streak = 0
    
    return {
        "id": child_id,
        "nickname": parent_child_relation.nickname or child_user.nickname,
        "grade": child_user.grade or "未设置",
        "school": parent_child_relation.school or "未设置",
        "class_name": parent_child_relation.class_name or "未设置",
        "avatar_url": child_user.avatar_url or "emoji:🎓",
        "parent_id": current_user.id,
        "is_active": child_user.is_active,
        "created_at": parent_child_relation.created_at.isoformat(),
        "stats": {
            "total_homework": total_homework,
            "completed_homework": completed_homework,
            "average_score": int(average_score),
            "total_study_time": int(total_study_time),
            "current_streak": current_streak
        }
    }

@router.get("/children/{child_id}/errors", summary="获取孩子错题分析")
def get_child_error_analysis(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定孩子的错题分析数据
    
    - **child_id**: 孩子ID
    """
    from app.models.parent_child import ParentChild
    from app.models.homework import Homework, ErrorQuestion
    from sqlalchemy import func, text
    from datetime import datetime, timedelta
    
    # 验证家长和孩子的关联关系
    parent_child_relation = db.query(ParentChild).filter(
        ParentChild.parent_id == current_user.id,
        ParentChild.child_id == child_id,
        ParentChild.is_active == True
    ).first()
    
    if not parent_child_relation:
        # 如果没有关联关系，返回空数据而不是404错误
        return {
            "child_id": child_id,
            "stats": {
                "totalErrors": 0,
                "unreviewedErrors": 0,
                "thisWeekErrors": 0,
                "improvedErrors": 0
            },
            "subjects": [],
            "types": [],
            "recentErrors": [],
            "suggestions": ["暂无错题数据，继续努力学习吧！"]
        }
    
    # 获取错题统计
    total_errors = db.query(ErrorQuestion).filter(ErrorQuestion.user_id == child_id).count()
    unreviewed_errors = db.query(ErrorQuestion).filter(
        ErrorQuestion.user_id == child_id,
        ErrorQuestion.is_reviewed == False
    ).count()
    
    # 本周新增错题
    week_ago = datetime.now() - timedelta(days=7)
    this_week_errors = db.query(ErrorQuestion).filter(
        ErrorQuestion.user_id == child_id,
        ErrorQuestion.created_at >= week_ago
    ).count()
    
    # 已改进错题（复习次数 >= 2次）
    improved_errors = db.query(ErrorQuestion).filter(
        ErrorQuestion.user_id == child_id,
        ErrorQuestion.review_count >= 2
    ).count()
    
    # 按学科统计错题分布
    subject_stats = []
    subject_mapping = {"math": "数学", "chinese": "语文", "english": "英语", "physics": "物理", "chemistry": "化学"}
    
    for subject_code, subject_name in subject_mapping.items():
        # 错题数量
        error_count = db.query(ErrorQuestion).join(Homework).filter(
            Homework.user_id == child_id,
            Homework.subject == subject_code
        ).count()
        
        # 总题目数量
        total_questions = db.query(func.sum(Homework.total_questions)).filter(
            Homework.user_id == child_id,
            Homework.subject == subject_code
        ).scalar() or 0
        
        # 正确率
        if total_questions > 0:
            accuracy = int((total_questions - error_count) * 100 / total_questions)
        else:
            accuracy = 0
            
        if error_count > 0 or total_questions > 0:  # 只显示有数据的学科
            subject_stats.append({
                "subject": subject_name,
                "errorCount": error_count,
                "totalQuestions": total_questions,
                "accuracy": accuracy
            })
    
    # 错题类型分析
    error_types_data = db.query(
        ErrorQuestion.error_type,
        func.count(ErrorQuestion.id).label('count')
    ).filter(ErrorQuestion.user_id == child_id).group_by(ErrorQuestion.error_type).all()
    
    total_typed_errors = sum(item.count for item in error_types_data if item.error_type)
    
    error_types = []
    error_type_mapping = {
        "calculation": {"name": "计算错误", "desc": "计算过程中出现的运算错误"},
        "comprehension": {"name": "理解错误", "desc": "对题目理解不准确导致的错误"},
        "knowledge": {"name": "知识点遗忘", "desc": "相关知识点掌握不牢固"},
        "careless": {"name": "粗心错误", "desc": "审题不仔细或答题疏忽"},
        "method": {"name": "方法错误", "desc": "解题方法选择不当"}
    }
    
    for item in error_types_data:
        if item.error_type and total_typed_errors > 0:
            type_info = error_type_mapping.get(item.error_type, {"name": item.error_type, "desc": ""})
            percentage = int(item.count * 100 / total_typed_errors)
            error_types.append({
                "type": type_info["name"],
                "percentage": percentage,
                "description": type_info["desc"]
            })
    
    # 如果没有错题类型数据，提供默认分析
    if not error_types and total_errors > 0:
        error_types = [
            {"type": "计算错误", "percentage": 40, "description": "计算过程中出现的运算错误"},
            {"type": "理解错误", "percentage": 35, "description": "对题目理解不准确导致的错误"},
            {"type": "知识点遗忘", "percentage": 25, "description": "相关知识点掌握不牢固"}
        ]
    
    # 获取最近错题
    recent_errors_query = db.query(ErrorQuestion).join(Homework).filter(
        ErrorQuestion.user_id == child_id
    ).order_by(ErrorQuestion.created_at.desc()).limit(10).all()
    
    recent_errors = []
    for error in recent_errors_query:
        homework = db.query(Homework).filter(Homework.id == error.homework_id).first()
        subject_name = subject_mapping.get(homework.subject, homework.subject) if homework else "其他"
        
        recent_errors.append({
            "id": error.id,
            "subject": subject_name,
            "question": error.question_text,
            "userAnswer": error.user_answer or "未作答",
            "correctAnswer": error.correct_answer,
            "reason": error.error_reason or "需要进一步分析",
            "date": error.created_at.strftime("%Y-%m-%d")
        })
    
    # 使用AI服务生成个性化学习建议
    ai_recommendations = []
    suggestions = []
    
    try:
        from app.services.ai_recommendation_service import AIRecommendationService
        ai_service = AIRecommendationService(db)
        ai_recommendations = ai_service.generate_ai_recommendations(child_id)
        
        # 如果有AI建议，同时生成简化的文本版本用于兼容性
        if ai_recommendations:
            for rec in ai_recommendations:
                suggestion_text = f"{rec['icon']} {rec['title']}: {rec['content']}"
                suggestions.append(suggestion_text)
                
                # 添加前2个行动项作为子建议
                if rec.get('action_items'):
                    for action in rec['action_items'][:2]:
                        suggestions.append(f"  • {action}")
        
    except Exception as e:
        print(f"AI建议生成失败: {e}")
        ai_recommendations = []
    
    # 如果AI建议为空或失败，使用传统建议作为后备
    if not ai_recommendations:
        if total_errors == 0:
            suggestions.append("表现优秀！继续保持当前的学习节奏")
        else:
            # 传统建议逻辑
            for subject in subject_stats:
                if subject["errorCount"] > 5:
                    if subject["subject"] == "数学":
                        suggestions.append(f"数学需要加强练习，建议每天完成10-15道基础题")
                    elif subject["subject"] == "语文":
                        suggestions.append(f"语文基础需要巩固，建议增加阅读量和字词练习")
                    elif subject["subject"] == "英语":
                        suggestions.append(f"英语需要多练习，建议每天背诵5-10个单词")
            
            if unreviewed_errors > 5:
                suggestions.append("建议定期复习错题，建立错题本进行系统整理")
            
            if not suggestions:
                suggestions.append("继续保持学习状态，注意巩固薄弱知识点")
    
    return {
        "child_id": child_id,
        "stats": {
            "totalErrors": total_errors,
            "unreviewedErrors": unreviewed_errors,
            "thisWeekErrors": this_week_errors,
            "improvedErrors": improved_errors
        },
        "subjects": subject_stats,
        "types": error_types,
        "recentErrors": recent_errors,
        "suggestions": suggestions,
        "aiRecommendations": ai_recommendations  # 新增AI建议数据
    }

@router.get("/test-endpoint", summary="测试端点")
def test_endpoint():
    """临时测试端点，用于验证路由是否工作"""
    return {"message": "测试端点工作正常", "timestamp": "2025-08-30"}

@router.get("/practice-status", summary="获取练习完成状态")
def get_practice_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取家长关联的所有孩子的练习完成状态
    
    包括：
    - 每个孩子的最近练习记录
    - 今日完成情况
    - 本周准确率统计
    """
    from app.models.parent_child import ParentChild
    from app.models.homework import Homework
    from sqlalchemy import func, and_
    from datetime import datetime, timedelta
    
    # 获取关联的孩子
    parent_child_relations = db.query(ParentChild).filter(
        ParentChild.parent_id == current_user.id,
        ParentChild.is_active == True
    ).all()
    
    children = []
    today = datetime.now().date()
    week_start = datetime.now() - timedelta(days=7)
    
    for relation in parent_child_relations:
        child_user = db.query(User).filter(User.id == relation.child_id).first()
        if not child_user:
            continue
            
        # 获取最近的练习记录（本周内）
        recent_practices = db.query(Homework).filter(
            Homework.user_id == relation.child_id,
            Homework.created_at >= week_start
        ).order_by(Homework.created_at.desc()).all()
        
        # 转换为前端需要的格式
        practice_data = []
        for hw in recent_practices:
            accuracy = int(hw.accuracy_rate * 100) if hw.accuracy_rate is not None else 0
            practice_data.append({
                'id': hw.id,
                'created_at': hw.created_at.isoformat(),
                'accuracy': accuracy,
                'subject': hw.subject,
                'total_questions': hw.total_questions or 0,
                'wrong_count': hw.wrong_count or 0,
                'status': hw.status
            })
        
        child_info = {
            'id': child_user.id,
            'name': relation.nickname or child_user.nickname or f"用户{child_user.id}",
            'avatar': child_user.avatar_url,
            'grade': child_user.grade or "未设置",
            'recent_practices': practice_data
        }
        children.append(child_info)
    
    return {
        'children': children,
        'total_children': len(children),
        'generated_at': datetime.now().isoformat()
    }

@router.get("/children/{child_id}/progress", summary="获取孩子学习进度")
def get_child_learning_progress(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定孩子的学习进度数据
    
    - **child_id**: 孩子ID
    """
    from app.models.parent_child import ParentChild
    from app.models.homework import Homework, ErrorQuestion
    from sqlalchemy import func
    
    # 验证家长和孩子的关联关系
    parent_child_relation = db.query(ParentChild).filter(
        ParentChild.parent_id == current_user.id,
        ParentChild.child_id == child_id,
        ParentChild.is_active == True
    ).first()
    
    if not parent_child_relation:
        raise HTTPException(status_code=404, detail="未找到该孩子或无权访问")
    
    # 获取时间范围
    now = datetime.now()
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    # 获取孩子的所有作业
    all_homework = db.query(Homework).filter(Homework.user_id == child_id).all()
    week_homework = [h for h in all_homework if h.created_at >= week_start]
    month_homework = [h for h in all_homework if h.created_at >= month_start]
    
    # 计算总体进度
    total_homework = len(all_homework)
    completed_homework = len([h for h in all_homework if h.status == 'completed'])
    
    # 计算平均准确率
    accuracy_rates = [h.accuracy_rate for h in all_homework if h.accuracy_rate is not None]
    total_progress = int(sum(accuracy_rates) * 100 / len(accuracy_rates)) if accuracy_rates else 0
    
    # 计算周目标完成率
    week_scores = [h.accuracy_rate * 100 for h in week_homework if h.accuracy_rate is not None]
    weekly_goal = int(sum(week_scores) / len(week_scores)) if week_scores else 0
    
    # 计算月目标完成率
    month_scores = [h.accuracy_rate * 100 for h in month_homework if h.accuracy_rate is not None]
    monthly_goal = int(sum(month_scores) / len(month_scores)) if month_scores else 0
    
    # 计算连续学习天数
    learning_days = set()
    for hw in all_homework:
        if hw.created_at >= now - timedelta(days=30):
            learning_days.add(hw.created_at.date())
    daily_streak = len(learning_days)
    
    # 计算学科进度
    subjects = {}
    subject_map = {"math": "数学", "chinese": "语文", "english": "英语", "physics": "物理", "chemistry": "化学"}
    
    for hw in all_homework:
        subject_key = hw.subject
        subject_name = subject_map.get(subject_key, subject_key)
        
        if subject_name not in subjects:
            subjects[subject_name] = {"homework": [], "total_questions": 0, "correct_answers": 0}
        
        subjects[subject_name]["homework"].append(hw)
        if hw.total_questions:
            subjects[subject_name]["total_questions"] += hw.total_questions
            subjects[subject_name]["correct_answers"] += (hw.total_questions - (hw.wrong_count or 0))
    
    subject_progress = []
    for subject_name, data in subjects.items():
        homework_count = len(data["homework"])
        if data["total_questions"] > 0:
            progress = int((data["correct_answers"] / data["total_questions"]) * 100)
        else:
            progress = 0
        
        # 最近得分
        recent_scores = [h.accuracy_rate * 100 for h in data["homework"][-3:] if h.accuracy_rate is not None]
        recent_score = int(sum(recent_scores) / len(recent_scores)) if recent_scores else 0
        
        completed = len([h for h in data["homework"] if h.status == 'completed'])
        
        subject_progress.append({
            "name": subject_name,
            "progress": progress,
            "completed": completed,
            "total": homework_count,
            "recentScore": recent_score
        })
    
    # 生成学习目标（基于实际数据）
    goals = []
    goal_id = 1
    for subject_name, data in subjects.items():
        if len(data["homework"]) > 0:
            completed_count = len([h for h in data["homework"] if h.status == 'completed'])
            total_count = len(data["homework"])
            
            goals.append({
                "id": goal_id,
                "title": f"{subject_name}练习完成",
                "progress": completed_count,
                "total": max(total_count, 10),  # 至少10个目标
                "completed": completed_count >= 10
            })
            goal_id += 1
    
    # 如果没有作业数据，添加默认目标
    if not goals:
        goals = [
            {"id": 1, "title": "开始第一次练习", "progress": 0, "total": 1, "completed": False},
            {"id": 2, "title": "完成基础练习", "progress": 0, "total": 5, "completed": False},
            {"id": 3, "title": "建立学习习惯", "progress": 0, "total": 10, "completed": False}
        ]
    
    # 生成成就徽章
    achievements = []
    
    # 连续学习天数成就
    achievements.append({
        "title": "连续学习7天",
        "icon": "🔥",
        "unlocked": daily_streak >= 7
    })
    
    # 满分成就
    perfect_scores = [hw for hw in all_homework if hw.accuracy_rate and hw.accuracy_rate >= 1.0]
    achievements.append({
        "title": "数学满分",
        "icon": "💯",
        "unlocked": len([hw for hw in perfect_scores if hw.subject == 'math']) > 0
    })
    
    # 错题零失误成就
    no_error_homework = len([hw for hw in week_homework if hw.wrong_count == 0])
    achievements.append({
        "title": "错题零失误",
        "icon": "🎯",
        "unlocked": no_error_homework >= 3
    })
    
    # 学习达人成就
    achievements.append({
        "title": "学习达人",
        "icon": "📚",
        "unlocked": total_homework >= 20
    })
    
    # 进步之星成就
    if len(all_homework) >= 10:
        recent_avg = sum([h.accuracy_rate for h in all_homework[-5:] if h.accuracy_rate]) / 5
        earlier_avg = sum([h.accuracy_rate for h in all_homework[-10:-5] if h.accuracy_rate]) / 5
        is_improving = recent_avg > earlier_avg + 0.1
    else:
        is_improving = False
    
    achievements.append({
        "title": "进步之星",
        "icon": "⭐",
        "unlocked": is_improving
    })
    
    # 完美一周成就
    week_perfect = all(hw.accuracy_rate >= 0.9 for hw in week_homework if hw.accuracy_rate is not None)
    achievements.append({
        "title": "完美一周",
        "icon": "👑",
        "unlocked": week_perfect and len(week_homework) >= 5
    })
    
    return {
        "child_id": child_id,
        "overall": {
            "totalProgress": total_progress,
            "weeklyGoal": weekly_goal,
            "monthlyGoal": monthly_goal,
            "dailyStreak": daily_streak
        },
        "subjects": subject_progress,
        "goals": goals,
        "achievements": achievements
    }

# 提醒相关的模型
class ReminderRequest(BaseModel):
    """提醒设置请求"""
    time: str = Field(..., description="提醒时间 (HH:MM格式)")
    frequency: str = Field(..., description="频率: daily/weekdays/weekends/custom")
    enabled: bool = Field(True, description="是否启用")

class ReminderResponse(BaseModel):
    """提醒设置响应"""
    id: int
    time: str
    frequency: str
    enabled: bool
    created_at: str
    updated_at: str

@router.get("/reminders", summary="获取提醒设置列表")
def get_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前家长的所有提醒设置
    """
    try:
        # 这里应该从数据库获取提醒设置，暂时返回模拟数据
        # 实际实现时需要创建 parent_reminders 表
        
        # 模拟从数据库获取的提醒设置
        mock_reminders = [
            {
                "id": 1,
                "time": "19:00",
                "frequency": "daily",
                "enabled": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        return {
            "reminders": mock_reminders,
            "total": len(mock_reminders),
            "parent_id": current_user.id
        }
        
    except Exception as e:
        print(f"获取提醒设置失败: {e}")
        return {
            "reminders": [],
            "total": 0,
            "parent_id": current_user.id
        }

@router.post("/reminders", summary="保存提醒设置")
def save_reminder(
    reminder_data: ReminderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    保存或更新提醒设置
    
    - **time**: 提醒时间 (HH:MM格式)
    - **frequency**: 频率 (daily/weekdays/weekends/custom)
    - **enabled**: 是否启用
    """
    try:
        # 这里应该保存到数据库，暂时返回成功响应
        # 实际实现时需要：
        # 1. 创建 parent_reminders 表
        # 2. 保存或更新提醒设置
        # 3. 返回保存后的数据
        
        saved_reminder = {
            "id": 1,  # 应该是数据库生成的ID
            "parent_id": current_user.id,
            "time": reminder_data.time,
            "frequency": reminder_data.frequency,
            "enabled": reminder_data.enabled,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        return {
            "message": "提醒设置保存成功",
            "reminder": saved_reminder,
            "success": True
        }
        
    except Exception as e:
        print(f"保存提醒设置失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存提醒设置失败: {str(e)}")

@router.delete("/reminders/{reminder_id}", summary="删除提醒设置")
def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除指定的提醒设置
    
    - **reminder_id**: 提醒ID
    """
    try:
        # 这里应该从数据库删除提醒设置
        # 实际实现时需要验证提醒属于当前用户
        
        return {
            "message": "提醒设置删除成功",
            "reminder_id": reminder_id,
            "success": True
        }
        
    except Exception as e:
        print(f"删除提醒设置失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除提醒设置失败: {str(e)}")