from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
import json
import time
import random
import os
import aiofiles
import uuid
from datetime import datetime, timedelta
from pathlib import Path

router = APIRouter()

class UserProfile(BaseModel):
    """用户资料"""
    id: int
    nickname: str
    avatar_url: Optional[str]
    role: str
    grade: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    is_vip: bool
    vip_expire_time: Optional[str]
    daily_quota: int
    total_used: int
    created_at: str
    settings: Optional[Dict[str, Any]]

class VIPStatus(BaseModel):
    """VIP状态"""
    is_vip: bool
    vip_type: Optional[str]
    expire_date: Optional[str]
    remaining_days: Optional[int]
    daily_quota: int
    monthly_quota: int
    total_used: int
    remaining_quota: int  # 剩余次数，VIP用户为-1表示无限

class UserSettings(BaseModel):
    """用户设置"""
    notifications: Dict[str, bool]
    privacy: Dict[str, bool]
    display: Dict[str, Any]

class AvatarUploadResponse(BaseModel):
    """头像上传响应"""
    avatar_url: str
    message: str
    uploaded_at: str

class DefaultAvatarRequest(BaseModel):
    """设置默认头像请求"""
    avatar_emoji: str

class DefaultAvatarResponse(BaseModel):
    """设置默认头像响应"""
    avatar_emoji: str
    message: str
    updated_at: str

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

class UpdateProfileRequest(BaseModel):
    """更新个人资料请求"""
    nickname: Optional[str] = None
    name: Optional[str] = None  # 家长用户姓名字段
    grade: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    class_name: Optional[str] = None
    school: Optional[str] = None

@router.post("/upload-avatar", response_model=AvatarUploadResponse, summary="上传头像")
async def upload_avatar(
    avatar_file: UploadFile = File(..., description="头像文件"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传用户头像
    
    - **avatar_file**: 头像文件 (支持JPG、PNG格式，最大5MB)
    """
    print("=== 开始上传头像 ===")
    print(f"接收到文件: {avatar_file.filename}")
    print(f"文件类型: {avatar_file.content_type}")
    print(f"文件大小: {avatar_file.size}")
    print(f"当前用户ID: {current_user.id}")
    print(f"当前用户昵称: {current_user.nickname}")
    
    # 验证文件类型
    if not avatar_file.content_type or not avatar_file.content_type.startswith('image/'):
        print(f"文件类型验证失败: {avatar_file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持图片文件"
        )
    
    # 验证文件格式
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
    if avatar_file.content_type not in allowed_types:
        print(f"文件格式验证失败: {avatar_file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持JPG、PNG格式的图片"
        )
    
    # 验证文件大小 (5MB)
    if avatar_file.size and avatar_file.size > 5 * 1024 * 1024:
        print(f"文件大小验证失败: {avatar_file.size}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片文件不能超过5MB"
        )
    
    print("所有验证通过，开始保存文件")
    
    try:
        # 创建上传目录
        upload_dir = Path("uploads/avatars")
        upload_dir.mkdir(parents=True, exist_ok=True)
        print(f"上传目录: {upload_dir.absolute()}")
        
        # 生成唯一文件名
        file_extension = Path(avatar_file.filename).suffix if avatar_file.filename else '.jpg'
        unique_filename = f"{current_user.id}_{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        print(f"文件将保存到: {file_path.absolute()}")
        
        # 保存文件
        print("开始写入文件...")
        async with aiofiles.open(file_path, 'wb') as f:
            content = await avatar_file.read()
            await f.write(content)
        print(f"文件保存完成，大小: {len(content)} bytes")
        
        # 生成访问URL - 使用相对路径，兼容不同端口
        avatar_url = f"/uploads/avatars/{unique_filename}"
        print(f"生成的访问URL: {avatar_url}")
        
        # 更新用户头像信息到数据库
        print("开始更新数据库...")
        print(f"更新前用户头像URL: {current_user.avatar_url}")
        print(f"更新前用户对象: {current_user}")
        
        current_user.avatar_url = avatar_url
        print(f"设置新URL后: {current_user.avatar_url}")
        
        # 确保对象被追踪
        db.add(current_user)
        print("已添加用户到会话")
        
        # 提交事务
        db.commit()
        print("数据库提交完成")
        
        # 刷新对象以获取最新数据
        db.refresh(current_user)
        print("数据库刷新完成")
        
        print(f"更新后用户头像URL: {current_user.avatar_url}")
        print(f"用户ID: {current_user.id}, 新头像URL: {avatar_url}")
        
        # 验证数据库中的数据
        updated_user = db.query(User).filter(User.id == current_user.id).first()
        print(f"数据库验证 - 用户ID: {updated_user.id}, 头像URL: {updated_user.avatar_url}")
        
        result = {
            "avatar_url": avatar_url,
            "message": "头像上传成功",
            "uploaded_at": datetime.now().isoformat()
        }
        print(f"返回结果: {result}")
        print("=== 头像上传完成 ===")
        
        return result
        
    except Exception as e:
        print(f"上传头像时发生异常: {str(e)}")
        print(f"异常类型: {type(e)}")
        import traceback
        print(f"异常堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"头像上传失败: {str(e)}"
        )

@router.post("/set-default-avatar", response_model=DefaultAvatarResponse, summary="设置默认头像")
def set_default_avatar(
    request: DefaultAvatarRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    设置默认头像（表情符号）
    
    - **avatar_emoji**: 表情符号头像
    """
    print("=== 开始设置默认头像 ===")
    print(f"接收到表情符号: {request.avatar_emoji}")
    print(f"当前用户ID: {current_user.id}")
    print(f"当前用户昵称: {current_user.nickname}")
    
    # 验证表情符号
    if not request.avatar_emoji or len(request.avatar_emoji.strip()) == 0:
        print("表情符号验证失败: 空值")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请选择一个头像表情"
        )
    
    # 验证表情符号长度（防止恶意输入）
    if len(request.avatar_emoji) > 10:
        print(f"表情符号长度验证失败: {len(request.avatar_emoji)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="头像表情格式不正确"
        )
    
    print("表情符号验证通过")
    
    try:
        # 更新数据库中的用户头像信息
        # 对于默认头像，我们将表情符号存储在avatar_url中，使用特殊前缀标识
        emoji_avatar_url = f"emoji:{request.avatar_emoji}"
        print(f"生成的emoji URL: {emoji_avatar_url}")
        
        print("开始更新数据库...")
        print(f"更新前用户头像URL: {current_user.avatar_url}")
        print(f"更新前用户对象: {current_user}")
        
        current_user.avatar_url = emoji_avatar_url
        print(f"设置新emoji URL后: {current_user.avatar_url}")
        
        # 确保对象被追踪
        db.add(current_user)
        print("已添加用户到会话")
        
        # 提交事务
        db.commit()
        print("数据库提交完成")
        
        # 刷新对象以获取最新数据
        db.refresh(current_user)
        print("数据库刷新完成")
        
        print(f"更新后用户头像URL: {current_user.avatar_url}")
        print(f"用户ID: {current_user.id}, 新表情头像: {emoji_avatar_url}")
        
        # 验证数据库中的数据
        updated_user = db.query(User).filter(User.id == current_user.id).first()
        print(f"数据库验证 - 用户ID: {updated_user.id}, 头像URL: {updated_user.avatar_url}")
        
        result = {
            "avatar_emoji": request.avatar_emoji,
            "message": "头像设置成功",
            "updated_at": datetime.now().isoformat()
        }
        print(f"返回结果: {result}")
        print("=== 默认头像设置完成 ===")
        
        return result
        
    except Exception as e:
        print(f"设置默认头像时发生异常: {str(e)}")
        print(f"异常类型: {type(e)}")
        import traceback
        print(f"异常堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"头像设置失败: {str(e)}"
        )

@router.get("/test-parent", summary="测试家长用户认证")
def test_parent_auth(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """临时测试端点，用于调试家长用户认证问题"""
    return {
        "message": "家长认证成功",
        "user_id": current_user.id,
        "user_role": current_user.role,
        "user_nickname": current_user.nickname
    }

@router.get("/profile", summary="获取用户资料")
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的详细资料 - 简化版本以修复家长用户错误
    """
    # 解析用户settings字段以获取class_name和school
    current_settings = {}
    if current_user.settings:
        try:
            current_settings = json.loads(current_user.settings)
        except:
            current_settings = {}
    
    # 简化的响应，避免复杂的错误
    return {
        "id": current_user.id,
        "nickname": current_user.nickname or "测试用户",
        "avatar_url": current_user.avatar_url or "emoji:👤",
        "role": current_user.role or "student",
        "grade": current_user.grade,
        "phone": current_user.phone,
        "email": current_user.email,
        "is_vip": current_user.is_vip or False,
        "vip_expire_time": current_user.vip_expire_time.isoformat() if current_user.vip_expire_time else None,
        "daily_quota": current_user.daily_quota or 5,
        "total_used": current_user.total_used or 0,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else datetime.now().isoformat(),
        "settings": {
            "notifications": {
                "homework_reminder": True,
                "error_summary": True,
                "study_report": True
            },
            "privacy": {
                "show_stats": True,
                "allow_comparison": False
            },
            "display": {
                "theme": "light",
                "language": "zh"
            },
            "class_name": current_settings.get('class_name'),
            "school": current_settings.get('school')
        }
    }

@router.put("/profile", summary="更新用户资料")
def update_user_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户资料
    
    - **nickname**: 用户昵称
    - **grade**: 年级
    - **phone**: 手机号码
    - **email**: 邮箱地址
    """
    print(f"!!! USER.PY PROFILE UPDATE CALLED !!!")
    print(f"=== 开始更新用户资料 ===")
    print(f"用户ID: {current_user.id}")
    print(f"更新数据: {request}")
    
    try:
        # 更新数据库中的用户信息
        # 处理name字段（家长用户使用name字段作为姓名，映射到nickname）
        if request.name is not None:
            current_user.nickname = request.name
            print(f"更新姓名(name->nickname): {request.name}")
        
        if request.nickname is not None:
            current_user.nickname = request.nickname
            print(f"更新昵称: {request.nickname}")
        
        if request.grade is not None:
            current_user.grade = request.grade  
            print(f"更新年级: {request.grade}")
        
        if request.phone is not None:
            current_user.phone = request.phone
            print(f"更新手机号: {request.phone}")
        
        if request.email is not None:
            current_user.email = request.email
            print(f"更新邮箱: {request.email}")
        
        # 新增：处理班级和学校字段
        if request.class_name is not None:
            # 由于User模型中没有class_name字段，我们需要使用settings字段存储
            import json
            current_settings = {}
            if current_user.settings:
                try:
                    current_settings = json.loads(current_user.settings)
                except:
                    current_settings = {}
            current_settings['class_name'] = request.class_name
            current_user.settings = json.dumps(current_settings, ensure_ascii=False)
            print(f"更新班级: {request.class_name}")
        
        if request.school is not None:
            # 由于User模型中没有school字段，我们需要使用settings字段存储
            import json
            current_settings = {}
            if current_user.settings:
                try:
                    current_settings = json.loads(current_user.settings)
                except:
                    current_settings = {}
            current_settings['school'] = request.school
            current_user.settings = json.dumps(current_settings, ensure_ascii=False)
            print(f"更新学校: {request.school}")
        
        # 提交到数据库
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        # 解析更新后的settings以获取class_name和school
        current_settings = {}
        if current_user.settings:
            try:
                current_settings = json.loads(current_user.settings)
            except:
                current_settings = {}
        
        print(f"数据库更新完成")
        print(f"更新后用户信息: nickname={current_user.nickname}, grade={current_user.grade}, phone={current_user.phone}, email={current_user.email}")
        print(f"settings中的额外信息: class_name={current_settings.get('class_name')}, school={current_settings.get('school')}")
        
        return {
            "message": "用户资料更新成功",
            "user": {
                "nickname": current_user.nickname,
                "grade": current_user.grade,
                "phone": current_user.phone,
                "email": current_user.email,
                "class_name": current_settings.get('class_name'),
                "school": current_settings.get('school')
            },
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"更新用户资料失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"用户资料更新失败: {str(e)}"
        )

@router.get("/vip-status", response_model=VIPStatus, summary="获取VIP状态")
def get_vip_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的VIP状态详情
    """
    # 获取用户真实VIP状态
    is_vip = getattr(current_user, 'is_vip', False)
    vip_expire_time = getattr(current_user, 'vip_expire_time', None)
    daily_quota = getattr(current_user, 'daily_quota', 3)
    total_used = getattr(current_user, 'total_used', 0)
    daily_used = getattr(current_user, 'daily_used', 0)
    
    # 检查VIP是否过期
    if is_vip and vip_expire_time:
        if datetime.now() > vip_expire_time:
            # VIP已过期，更新用户状态
            current_user.is_vip = False
            db.add(current_user)
            db.commit()
            db.refresh(current_user)
            is_vip = False
    
    # 计算剩余天数和VIP类型
    if is_vip and vip_expire_time:
        remaining_days = (vip_expire_time - datetime.now()).days
        # 根据剩余天数推断VIP类型
        if remaining_days <= 31:
            vip_type = "monthly"
        elif remaining_days <= 93:
            vip_type = "quarterly"  
        else:
            vip_type = "yearly"
            
        # VIP用户享有更高的每日额度
        if daily_quota <= 5:  # 如果还是免费额度，给予VIP额度
            daily_quota = 50 if vip_type == "monthly" else (80 if vip_type == "quarterly" else 120)
    else:
        remaining_days = 0
        vip_type = "free"
        # 非VIP用户的免费额度
        if daily_quota > 5:
            daily_quota = 3
    
    # 计算剩余次数（VIP用户无限制，显示为-1表示无限）
    if is_vip:
        remaining_quota = -1  # VIP用户无限制
    else:
        remaining_quota = max(0, daily_quota - daily_used) if daily_used is not None else daily_quota
    
    return {
        "is_vip": is_vip,
        "vip_type": vip_type,
        "expire_date": vip_expire_time.isoformat() if vip_expire_time else None,
        "remaining_days": remaining_days if is_vip else 0,
        "daily_quota": daily_quota,
        "monthly_quota": daily_quota * 30 if not is_vip else -1,  # VIP无限制
        "total_used": total_used,
        "remaining_quota": remaining_quota
    }

@router.get("/settings", response_model=UserSettings, summary="获取用户设置")
def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的个性化设置
    """
    # 模拟用户设置
    return {
        "notifications": {
            "homework_reminder": True,
            "error_summary": True,
            "study_report": True,
            "weekly_summary": False,
            "achievement_unlock": True
        },
        "privacy": {
            "show_stats": True,
            "allow_comparison": False,
            "public_profile": False,
            "share_achievements": True
        },
        "display": {
            "theme": "light",
            "language": "zh",
            "font_size": "medium",
            "animations": True,
            "sound_effects": True
        }
    }

@router.put("/settings", summary="更新用户设置")
def update_user_settings(
    settings: str = Form(..., description="设置JSON字符串"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户的个性化设置
    
    - **settings**: JSON格式的设置数据
    """
    try:
        settings_data = json.loads(settings)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="设置数据格式错误"
        )
    
    # 在实际应用中，这里会验证设置数据并保存到数据库
    return {
        "message": "用户设置更新成功",
        "settings": settings_data,
        "updated_at": datetime.now().isoformat()
    }

@router.get("/achievements", summary="获取用户成就")
def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的学习成就和徽章
    """
    # 模拟成就数据
    achievements = [
        {
            "id": "first_homework",
            "name": "初出茅庐",
            "description": "完成第一份作业",
            "icon": "🎯",
            "unlocked": True,
            "unlocked_at": datetime.now().isoformat(),
            "progress": 100,
            "total": 100
        },
        {
            "id": "accuracy_master",
            "name": "准确率大师",
            "description": "连续7天准确率超过90%",
            "icon": "🎯",
            "unlocked": True,
            "unlocked_at": (datetime.now() - timedelta(days=5)).isoformat(),
            "progress": 100,
            "total": 100
        },
        {
            "id": "study_streak",
            "name": "学习达人",
            "description": "连续学习30天",
            "icon": "🔥",
            "unlocked": False,
            "unlocked_at": None,
            "progress": 15,
            "total": 30
        },
        {
            "id": "error_conqueror",
            "name": "错题终结者",
            "description": "复习100道错题",
            "icon": "⚔️",
            "unlocked": False,
            "unlocked_at": None,
            "progress": 67,
            "total": 100
        }
    ]
    
    return {
        "total_achievements": len(achievements),
        "unlocked_count": len([a for a in achievements if a["unlocked"]]),
        "achievements": achievements,
        "next_milestone": {
            "name": "学习达人",
            "progress": 15,
            "total": 30,
            "days_remaining": 15
        }
    }

@router.post("/notification-settings", summary="保存通知设置")
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

@router.get("/messages", response_model=List[MessageResponse], summary="获取用户消息")
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

@router.delete("/messages", summary="清空用户消息")
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

@router.delete("/account", summary="注销账户")
def delete_account(
    confirmation: str = Form(..., description="确认文本"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    注销用户账户
    
    - **confirmation**: 必须输入 "DELETE" 确认删除
    """
    if confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入 'DELETE' 确认删除账户"
        )
    
    # 在实际应用中，这里会软删除用户数据或进行数据清理
    return {
        "message": "账户注销申请已提交，将在7天后生效",
        "scheduled_deletion": (datetime.now() + timedelta(days=7)).isoformat(),
        "contact_support": "如需取消，请联系客服"
    }

@router.get("/statistics", summary="获取用户统计")
def get_user_statistics(
    period: str = "month",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的学习统计数据
    
    - **period**: 统计周期 (week/month/year)
    """
    # 模拟统计数据
    total_homework = random.randint(50, 200)
    period_homework = random.randint(10, total_homework)
    
    return {
        "period": period,
        "overview": {
            "total_homework": total_homework,
            "period_homework": period_homework,
            "average_accuracy": round(random.uniform(75, 95), 1),
            "study_days": random.randint(20, 60),
            "total_time_minutes": random.randint(1200, 3600)
        },
        "subjects": [
            {
                "subject": "数学",
                "homework_count": random.randint(10, 50),
                "accuracy": round(random.uniform(70, 95), 1),
                "improvement": round(random.uniform(-5, 15), 1)
            },
            {
                "subject": "语文",
                "homework_count": random.randint(5, 30),
                "accuracy": round(random.uniform(75, 90), 1),
                "improvement": round(random.uniform(-3, 10), 1)
            }
        ],
        "trends": [
            {
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "homework_count": random.randint(0, 5),
                "accuracy": round(random.uniform(70, 100), 1),
                "time_minutes": random.randint(0, 120)
            }
            for i in range(7)
        ],
        "generated_at": datetime.now().isoformat()
    }