from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
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

class CreateTicketRequest(BaseModel):
    """创建工单请求"""
    type: str = Field(..., description="问题类型")
    title: str = Field(..., description="问题标题")
    description: str = Field(..., description="详细描述")
    contact: Optional[str] = Field(None, description="联系方式")

class TicketResponse(BaseModel):
    """工单响应"""
    ticket_id: str
    message: str
    created_at: str

class NotificationSettingsRequest(BaseModel):
    """通知设置请求"""
    push_enabled: bool
    homework_notify: bool
    error_reminder: bool
    study_reminder: bool
    system_notify: bool
    quiet_start_time: str
    quiet_end_time: str

class MessageResponse(BaseModel):
    """消息响应"""
    id: int
    title: str
    content: str
    is_read: bool
    created_at: str

@router.post("/tickets", response_model=TicketResponse, summary="提交工单")
def create_support_ticket(
    ticket_request: CreateTicketRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交客服工单
    
    - **type**: 问题类型 (homework/account/payment/function/suggestion/other)
    - **title**: 问题标题
    - **description**: 详细描述
    - **contact**: 联系方式（可选）
    """
    # 生成工单ID
    ticket_id = f"T{int(time.time())}{random.randint(100, 999)}"
    
    # 在实际应用中，这里会将工单信息保存到数据库
    # 目前使用模拟响应
    ticket_data = {
        "ticket_id": ticket_id,
        "user_id": current_user.id,
        "type": ticket_request.type,
        "title": ticket_request.title,
        "description": ticket_request.description,
        "contact": ticket_request.contact,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    # 模拟保存工单到数据库的过程
    # 在真实场景中，这里会使用SQLAlchemy模型保存数据
    
    return TicketResponse(
        ticket_id=ticket_id,
        message="工单提交成功，我们将在1-2个工作日内处理",
        created_at=datetime.now().isoformat()
    )

@router.get("/tickets", summary="获取用户工单列表")
def get_user_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的工单列表"""
    # 模拟工单数据
    mock_tickets = [
        {
            "ticket_id": f"T{int(time.time()) - 86400}001",
            "type": "homework",
            "title": "作业批改结果不准确",
            "status": "processing",
            "created_at": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "ticket_id": f"T{int(time.time()) - 172800}002", 
            "type": "account",
            "title": "无法登录账号",
            "status": "resolved",
            "created_at": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": (datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    return {
        "tickets": mock_tickets,
        "total": len(mock_tickets)
    }

@router.post("/user/notification-settings", summary="保存通知设置")
def save_notification_settings(
    settings: NotificationSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    保存用户通知设置
    
    - **push_enabled**: 是否启用推送通知
    - **homework_notify**: 作业完成通知
    - **error_reminder**: 错题复习提醒
    - **study_reminder**: 学习计划提醒
    - **system_notify**: 系统通知
    - **quiet_start_time**: 免打扰开始时间
    - **quiet_end_time**: 免打扰结束时间
    """
    # 在实际应用中，这里会更新用户的通知设置
    settings_data = {
        "push_enabled": settings.push_enabled,
        "homework_notify": settings.homework_notify,
        "error_reminder": settings.error_reminder,
        "study_reminder": settings.study_reminder,
        "system_notify": settings.system_notify,
        "quiet_start_time": settings.quiet_start_time,
        "quiet_end_time": settings.quiet_end_time,
        "updated_at": datetime.now().isoformat()
    }
    
    return {
        "message": "通知设置保存成功",
        "settings": settings_data
    }

@router.get("/user/messages", response_model=List[MessageResponse], summary="获取用户消息")
def get_user_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户消息列表"""
    # 模拟消息数据
    mock_messages = [
        {
            "id": 1,
            "title": "数学作业批改完成",
            "content": "您的数学作业已批改完成，正确率85%",
            "is_read": True,
            "created_at": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        },
        {
            "id": 2,
            "title": "错题复习提醒",
            "content": "您有5道错题需要复习，建议今天完成",
            "is_read": False,
            "created_at": (datetime.now() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
        },
        {
            "id": 3,
            "title": "学习计划更新",
            "content": "本周学习计划已更新，请查看新的学习安排",
            "is_read": True,
            "created_at": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        },
        {
            "id": 4,
            "title": "系统升级通知",
            "content": "系统将在今晚进行升级维护，预计1小时",
            "is_read": True,
            "created_at": (datetime.now() - timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M")
        }
    ]
    
    return [MessageResponse(**msg) for msg in mock_messages]

@router.delete("/user/messages", summary="清空用户消息")
def clear_user_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清空用户所有消息"""
    # 在实际应用中，这里会删除用户的所有消息记录
    return {
        "message": "消息记录已清空",
        "cleared_at": datetime.now().isoformat()
    }

@router.get("/faq/{category}", summary="获取常见问题")
def get_faq_by_category(
    category: str,
    current_user: User = Depends(get_current_user)
):
    """根据分类获取常见问题"""
    faq_data = {
        "homework": {
            "title": "作业批改相关问题",
            "items": [
                {"question": "如何拍摄作业照片？", "answer": "请确保光线充足，作业完整清晰可见，避免阴影和反光。"},
                {"question": "批改结果不准确怎么办？", "answer": "请检查照片是否清晰，可以重新拍摄或联系客服反馈。"},
                {"question": "支持哪些学科的批改？", "answer": "目前支持小学和初中的数学、语文、英语等主要学科。"}
            ]
        },
        "account": {
            "title": "账号和登录问题", 
            "items": [
                {"question": "忘记登录密码怎么办？", "answer": "在登录页面点击忘记密码，输入手机号获取验证码重置。"},
                {"question": "如何更换绑定手机号？", "answer": "进入个人设置-账户安全-更换手机号完成验证。"},
                {"question": "可以同时登录多个设备吗？", "answer": "同一账号可以在3台设备上同时登录。"}
            ]
        }
    }
    
    if category not in faq_data:
        raise HTTPException(status_code=404, detail="分类不存在")
        
    return faq_data[category]