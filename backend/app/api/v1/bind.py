from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.parent_child import ParentChild, BindInvite, InviteStatus
import secrets
import string
from datetime import datetime, timedelta

router = APIRouter()

class CreateInviteRequest(BaseModel):
    """创建绑定邀请请求"""
    invitee_phone: Optional[str] = Field(None, description="被邀请人手机号（可选）")
    invite_message: Optional[str] = Field(None, max_length=200, description="邀请留言")
    relationship_type: str = Field("parent", description="关系类型")
    expires_days: int = Field(7, ge=1, le=30, description="邀请有效期（天）")

class InviteResponse(BaseModel):
    """邀请响应"""
    invite_code: str
    expires_at: str
    message: str

class AcceptInviteRequest(BaseModel):
    """接受邀请请求"""
    invite_code: str = Field(..., description="邀请码")
    nickname: Optional[str] = Field(None, max_length=50, description="给对方设置的昵称")

class BindingInfo(BaseModel):
    """绑定关系信息"""
    id: int
    parent_info: Dict[str, Any]
    child_info: Dict[str, Any]
    relationship_type: str
    nickname: Optional[str]
    is_active: bool
    can_view_homework: bool
    can_view_reports: bool
    can_set_limits: bool
    daily_homework_limit: int
    daily_time_limit: int
    created_at: str

def generate_invite_code() -> str:
    """生成唯一邀请码"""
    chars = string.ascii_uppercase + string.digits
    # 生成8位邀请码，去除易混淆字符
    chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    return ''.join(secrets.choice(chars) for _ in range(8))

@router.post("/invite", response_model=InviteResponse, summary="创建绑定邀请")
def create_bind_invite(
    request: CreateInviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建家长-孩子绑定邀请
    
    支持两种邀请方式：
    1. 生成邀请码，让对方输入邀请码加入
    2. 通过手机号邀请（如果提供了手机号）
    """
    
    # 生成唯一邀请码
    max_attempts = 10
    for _ in range(max_attempts):
        invite_code = generate_invite_code()
        existing = db.query(BindInvite).filter(BindInvite.invite_code == invite_code).first()
        if not existing:
            break
    else:
        raise HTTPException(status_code=500, detail="生成邀请码失败，请重试")
    
    # 计算过期时间
    expires_at = datetime.now() + timedelta(days=request.expires_days)
    
    # 确定邀请人类型
    inviter_type = current_user.role if current_user.role in ["parent", "student"] else "parent"
    
    # 创建邀请记录
    invite = BindInvite(
        invite_code=invite_code,
        inviter_id=current_user.id,
        inviter_type=inviter_type,
        invitee_phone=request.invitee_phone,
        invite_message=request.invite_message,
        relationship_type=request.relationship_type,
        expires_at=expires_at,
        status=InviteStatus.PENDING
    )
    
    db.add(invite)
    db.commit()
    db.refresh(invite)
    
    return InviteResponse(
        invite_code=invite_code,
        expires_at=expires_at.isoformat(),
        message=f"邀请已创建，有效期{request.expires_days}天"
    )

@router.post("/accept", summary="接受绑定邀请")
def accept_bind_invite(
    request: AcceptInviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    接受家长-孩子绑定邀请
    """
    
    # 查找邀请记录
    invite = db.query(BindInvite).filter(
        BindInvite.invite_code == request.invite_code.upper()
    ).first()
    
    if not invite:
        raise HTTPException(status_code=404, detail="邀请码不存在或已失效")
    
    if not invite.can_accept():
        if invite.is_expired():
            raise HTTPException(status_code=400, detail="邀请码已过期")
        else:
            raise HTTPException(status_code=400, detail="邀请码已被使用或已失效")
    
    # 检查是否是邀请人本人
    if invite.inviter_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能接受自己发出的邀请")
    
    # 检查手机号匹配（如果邀请指定了手机号）
    if invite.invitee_phone and invite.invitee_phone != current_user.phone:
        raise HTTPException(status_code=400, detail="手机号不匹配，此邀请不是发给您的")
    
    # 确定家长和孩子角色
    inviter = db.query(User).filter(User.id == invite.inviter_id).first()
    if not inviter:
        raise HTTPException(status_code=404, detail="邀请人不存在")
    
    # 根据邀请人类型确定角色分配
    if invite.inviter_type == "parent":
        parent_id = invite.inviter_id
        child_id = current_user.id
        # 如果当前用户不是学生，将其角色更新为学生
        if current_user.role != "student":
            current_user.role = "student"
    else:  # 邀请人是学生
        parent_id = current_user.id
        child_id = invite.inviter_id
        # 如果当前用户不是家长，将其角色更新为家长
        if current_user.role != "parent":
            current_user.role = "parent"
    
    # 检查是否已经存在绑定关系
    existing_binding = db.query(ParentChild).filter(
        ParentChild.parent_id == parent_id,
        ParentChild.child_id == child_id
    ).first()
    
    if existing_binding:
        raise HTTPException(status_code=400, detail="绑定关系已存在")
    
    # 创建绑定关系
    binding = ParentChild(
        parent_id=parent_id,
        child_id=child_id,
        relationship_type=invite.relationship_type,
        nickname=request.nickname,
        is_active=True,
        can_view_homework=True,
        can_view_reports=True,
        can_set_limits=True
    )
    
    db.add(binding)
    
    # 更新邀请状态
    invite.status = InviteStatus.ACCEPTED
    invite.invitee_id = current_user.id
    invite.accepted_at = datetime.now()
    
    db.commit()
    
    return {
        "message": "绑定成功",
        "binding_id": binding.id,
        "parent_name": inviter.nickname if invite.inviter_type == "parent" else current_user.nickname,
        "child_name": current_user.nickname if invite.inviter_type == "parent" else inviter.nickname,
        "created_at": datetime.now().isoformat()
    }

@router.get("/list", response_model=List[BindingInfo], summary="获取绑定关系列表")
def get_binding_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有绑定关系
    
    - 如果是家长：返回所有孩子的绑定关系
    - 如果是学生：返回所有家长的绑定关系
    """
    
    bindings = []
    
    if current_user.role == "parent":
        # 家长查看绑定的孩子
        query_bindings = db.query(ParentChild).filter(
            ParentChild.parent_id == current_user.id,
            ParentChild.is_active == True
        ).all()
        
        for binding in query_bindings:
            child = db.query(User).filter(User.id == binding.child_id).first()
            bindings.append(BindingInfo(
                id=binding.id,
                parent_info={
                    "id": current_user.id,
                    "nickname": current_user.nickname,
                    "avatar_url": current_user.avatar_url
                },
                child_info={
                    "id": child.id,
                    "nickname": child.nickname,
                    "avatar_url": child.avatar_url,
                    "grade": child.grade
                },
                relationship_type=binding.relationship_type,
                nickname=binding.nickname,
                is_active=binding.is_active,
                can_view_homework=binding.can_view_homework,
                can_view_reports=binding.can_view_reports,
                can_set_limits=binding.can_set_limits,
                daily_homework_limit=binding.daily_homework_limit,
                daily_time_limit=binding.daily_time_limit,
                created_at=binding.created_at.isoformat()
            ))
    
    else:
        # 学生查看绑定的家长
        query_bindings = db.query(ParentChild).filter(
            ParentChild.child_id == current_user.id,
            ParentChild.is_active == True
        ).all()
        
        for binding in query_bindings:
            parent = db.query(User).filter(User.id == binding.parent_id).first()
            bindings.append(BindingInfo(
                id=binding.id,
                parent_info={
                    "id": parent.id,
                    "nickname": parent.nickname,
                    "avatar_url": parent.avatar_url
                },
                child_info={
                    "id": current_user.id,
                    "nickname": current_user.nickname,
                    "avatar_url": current_user.avatar_url,
                    "grade": current_user.grade
                },
                relationship_type=binding.relationship_type,
                nickname=binding.nickname,
                is_active=binding.is_active,
                can_view_homework=binding.can_view_homework,
                can_view_reports=binding.can_view_reports,
                can_set_limits=binding.can_set_limits,
                daily_homework_limit=binding.daily_homework_limit,
                daily_time_limit=binding.daily_time_limit,
                created_at=binding.created_at.isoformat()
            ))
    
    return bindings

class UpdateBindingSettingsRequest(BaseModel):
    """更新绑定设置请求"""
    daily_homework_limit: Optional[int] = Field(None, ge=1, le=50, description="每日作业额度")
    daily_time_limit: Optional[int] = Field(None, ge=30, le=480, description="每日学习时间限制(分钟)")
    bedtime_reminder: Optional[str] = Field(None, pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", description="睡觉提醒时间")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    can_view_homework: Optional[bool] = Field(None, description="可以查看作业")
    can_view_reports: Optional[bool] = Field(None, description="可以查看报告")

@router.put("/settings/{binding_id}", summary="更新绑定设置")
def update_binding_settings(
    binding_id: int,
    request: UpdateBindingSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新绑定关系的设置
    
    只有家长可以更新设置
    """
    
    # 查找绑定关系
    binding = db.query(ParentChild).filter(
        ParentChild.id == binding_id,
        ParentChild.parent_id == current_user.id,
        ParentChild.is_active == True
    ).first()
    
    if not binding:
        raise HTTPException(status_code=404, detail="绑定关系不存在或无权限操作")
    
    # 更新设置
    update_fields = {}
    if request.daily_homework_limit is not None:
        binding.daily_homework_limit = request.daily_homework_limit
        update_fields["daily_homework_limit"] = request.daily_homework_limit
    
    if request.daily_time_limit is not None:
        binding.daily_time_limit = request.daily_time_limit
        update_fields["daily_time_limit"] = request.daily_time_limit
    
    if request.bedtime_reminder is not None:
        binding.bedtime_reminder = request.bedtime_reminder
        update_fields["bedtime_reminder"] = request.bedtime_reminder
        
    if request.nickname is not None:
        binding.nickname = request.nickname
        update_fields["nickname"] = request.nickname
    
    if request.can_view_homework is not None:
        binding.can_view_homework = request.can_view_homework
        update_fields["can_view_homework"] = request.can_view_homework
    
    if request.can_view_reports is not None:
        binding.can_view_reports = request.can_view_reports
        update_fields["can_view_reports"] = request.can_view_reports
    
    db.commit()
    
    return {
        "message": "设置更新成功",
        "binding_id": binding_id,
        "updated_fields": update_fields,
        "updated_at": datetime.now().isoformat()
    }

@router.delete("/unbind/{binding_id}", summary="解除绑定关系")
def unbind_relationship(
    binding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    解除家长-孩子绑定关系
    
    家长和孩子都可以主动解除绑定
    """
    
    # 查找绑定关系
    binding = db.query(ParentChild).filter(
        ParentChild.id == binding_id,
        or_(
            ParentChild.parent_id == current_user.id,
            ParentChild.child_id == current_user.id
        ),
        ParentChild.is_active == True
    ).first()
    
    if not binding:
        raise HTTPException(status_code=404, detail="绑定关系不存在或无权限操作")
    
    # 软删除（设为不活跃）
    binding.is_active = False
    db.commit()
    
    return {
        "message": "绑定关系已解除",
        "binding_id": binding_id,
        "unbound_at": datetime.now().isoformat()
    }

class QuickBindRequest(BaseModel):
    """快速绑定请求"""
    target_phone: str = Field(..., description="目标用户手机号")
    my_nickname: Optional[str] = Field(None, max_length=50, description="我的昵称")
    method: str = Field("phone", description="绑定方式")

class QRCodeRequest(BaseModel):
    """二维码生成请求"""
    method: str = Field("qr", description="绑定方式")
    expires_minutes: Optional[int] = Field(30, ge=5, le=120, description="二维码有效期(分钟)")

@router.post("/quick-bind", summary="手机号快速绑定")
def quick_bind_by_phone(
    request: QuickBindRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    通过手机号快速绑定
    
    直接通过手机号查找用户并创建绑定关系，跳过邀请码步骤
    """
    # 查找目标用户
    target_user = db.query(User).filter(User.phone == request.target_phone).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="该手机号用户不存在，请确认手机号是否正确")
    
    # 检查是否是自己
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能绑定自己")
    
    # 确定家长和孩子角色
    if current_user.role == "parent":
        parent_id = current_user.id
        child_id = target_user.id
        # 如果目标用户不是学生，更新其角色
        if target_user.role != "student":
            target_user.role = "student"
    elif current_user.role == "student":
        parent_id = target_user.id
        child_id = current_user.id
        # 如果目标用户不是家长，更新其角色
        if target_user.role != "parent":
            target_user.role = "parent"
    else:
        # 如果当前用户角色未定，根据年龄或其他规则判断
        if current_user.grade:  # 有年级信息，可能是学生
            parent_id = target_user.id
            child_id = current_user.id
            current_user.role = "student"
            target_user.role = "parent"
        else:  # 默认当前用户为家长
            parent_id = current_user.id
            child_id = target_user.id
            current_user.role = "parent"
            target_user.role = "student"
    
    # 检查是否已经存在绑定关系
    existing_binding = db.query(ParentChild).filter(
        ParentChild.parent_id == parent_id,
        ParentChild.child_id == child_id,
        ParentChild.is_active == True
    ).first()
    
    if existing_binding:
        raise HTTPException(status_code=400, detail="绑定关系已存在")
    
    # 创建绑定关系
    binding = ParentChild(
        parent_id=parent_id,
        child_id=child_id,
        relationship_type="parent",
        nickname=request.my_nickname,
        is_active=True,
        can_view_homework=True,
        can_view_reports=True,
        can_set_limits=True
    )
    
    db.add(binding)
    db.commit()
    db.refresh(binding)
    
    parent = db.query(User).filter(User.id == parent_id).first()
    child = db.query(User).filter(User.id == child_id).first()
    
    return {
        "message": "快速绑定成功",
        "binding_id": binding.id,
        "parent_name": parent.nickname,
        "child_name": child.nickname,
        "relationship": "已建立家长-孩子绑定关系",
        "created_at": binding.created_at.isoformat()
    }

@router.post("/qr-code", summary="生成绑定二维码")
def generate_qr_code(
    request: QRCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成用于绑定的二维码
    
    返回二维码数据，前端可用于生成二维码图片
    """
    # 生成临时绑定码
    bind_code = generate_invite_code()
    
    # 计算过期时间
    expires_at = datetime.now() + timedelta(minutes=request.expires_minutes)
    
    # 创建临时邀请记录用于二维码扫描
    invite = BindInvite(
        invite_code=bind_code,
        inviter_id=current_user.id,
        inviter_type=current_user.role if current_user.role in ["parent", "student"] else "parent",
        relationship_type="parent",
        expires_at=expires_at,
        status=InviteStatus.PENDING
    )
    
    db.add(invite)
    db.commit()
    
    # 构造二维码数据
    qr_data = f"ZYJC_BIND:{bind_code}:{current_user.id}"
    
    return {
        "qr_code": bind_code,
        "qr_data": qr_data,
        "expires_at": expires_at.isoformat(),
        "expires_in_minutes": request.expires_minutes,
        "message": f"二维码已生成，有效期{request.expires_minutes}分钟"
    }

@router.get("/invites", summary="获取邀请记录")
def get_invites(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的邀请记录
    
    - 发出的邀请
    - 收到的邀请
    """
    
    query_filter = [BindInvite.inviter_id == current_user.id]
    if current_user.phone:
        query_filter.append(BindInvite.invitee_phone == current_user.phone)
    if current_user.id:
        query_filter.append(BindInvite.invitee_id == current_user.id)
    
    query = db.query(BindInvite).filter(or_(*query_filter))
    
    if status:
        try:
            status_enum = InviteStatus(status)
            query = query.filter(BindInvite.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的状态参数")
    
    invites = query.order_by(BindInvite.created_at.desc()).all()
    
    result = []
    for invite in invites:
        # 获取邀请人信息
        inviter = db.query(User).filter(User.id == invite.inviter_id).first()
        
        # 获取被邀请人信息（如果已接受）
        invitee = None
        if invite.invitee_id:
            invitee = db.query(User).filter(User.id == invite.invitee_id).first()
        
        result.append({
            "id": invite.id,
            "invite_code": invite.invite_code,
            "inviter_info": {
                "id": inviter.id,
                "nickname": inviter.nickname,
                "avatar_url": inviter.avatar_url
            } if inviter else None,
            "invitee_info": {
                "id": invitee.id,
                "nickname": invitee.nickname,
                "avatar_url": invitee.avatar_url
            } if invitee else None,
            "invitee_phone": invite.invitee_phone,
            "invite_message": invite.invite_message,
            "relationship_type": invite.relationship_type,
            "status": invite.status.value,
            "is_my_invite": invite.inviter_id == current_user.id,
            "expires_at": invite.expires_at.isoformat(),
            "accepted_at": invite.accepted_at.isoformat() if invite.accepted_at else None,
            "created_at": invite.created_at.isoformat()
        })
    
    return result