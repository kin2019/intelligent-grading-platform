"""
用户管理API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from ....shared.models.user import (
    UserResponse, UserUpdate, UserCreate,
    UserRole, UserStatus, VIPType
)
from ....shared.models.base import ResponseModel, PaginatedResponseModel, PaginationModel
from ....shared.utils.database import get_db, paginate
from ....shared.utils.auth import get_current_user, require_admin, require_roles
from ..repositories.user_repository import UserRepository

router = APIRouter()


def get_user_from_header(request: Request) -> dict:
    """从请求头获取用户信息"""
    return {
        "id": int(request.headers.get("X-User-ID")),
        "role": request.headers.get("X-User-Role"),
        "openid": request.headers.get("X-User-OpenID"),
        "vip_type": request.headers.get("X-User-VIP-Type")
    }


@router.get("/me", response_model=UserResponse)
async def get_my_profile(request: Request, db: Session = Depends(get_db)):
    """获取当前用户信息"""
    current_user = get_user_from_header(request)
    user_id = current_user["id"]
    
    user_repo = UserRepository()
    user = user_repo.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    request: Request,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    current_user = get_user_from_header(request)
    user_id = current_user["id"]
    
    user_repo = UserRepository()
    user = user_repo.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查手机号是否已被使用
    if user_update.phone and user_update.phone != user.phone:
        existing_user = user_repo.get_by_phone(db, user_update.phone)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被使用"
            )
    
    # 检查邮箱是否已被使用
    if user_update.email and user_update.email != user.email:
        existing_user = user_repo.get_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
    
    # 更新用户信息
    updated_user = user_repo.update(db, user, **user_update.model_dump(exclude_unset=True))
    
    return UserResponse.model_validate(updated_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """根据ID获取用户信息"""
    current_user = get_user_from_header(request)
    
    # 检查权限：只有管理员或用户本人可以查看
    if current_user["role"] != UserRole.ADMIN.value and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user_repo = UserRepository()
    user = user_repo.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserResponse.model_validate(user)


@router.get("/", response_model=PaginatedResponseModel)
async def get_users(
    request: Request,
    role: Optional[UserRole] = Query(None, description="用户角色"),
    vip_type: Optional[VIPType] = Query(None, description="VIP类型"),
    status: Optional[UserStatus] = Query(None, description="用户状态"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取用户列表（仅管理员）"""
    current_user = get_user_from_header(request)
    
    # 检查管理员权限
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user_repo = UserRepository()
    
    if keyword:
        # 搜索用户
        users = user_repo.search_users(db, keyword, role, (page - 1) * size, size)
        # 获取总数（简化处理，实际应该实现搜索计数）
        total = len(users)
    else:
        # 获取所有用户
        if role:
            users = user_repo.get_users_by_role(db, role, (page - 1) * size, size)
        elif vip_type:
            users = user_repo.get_vip_users(db, vip_type, (page - 1) * size, size)
        else:
            users = user_repo.get_multi(db, (page - 1) * size, size)
        
        total = user_repo.count(db)
    
    # 转换为响应模型
    user_responses = [UserResponse.model_validate(user) for user in users]
    
    pagination = PaginationModel(
        page=page,
        size=size,
        total=total,
        pages=(total + size - 1) // size if total > 0 else 0,
        has_next=page * size < total,
        has_prev=page > 1
    )
    
    return PaginatedResponseModel(
        code=200,
        message="获取用户列表成功",
        data=user_responses,
        pagination=pagination
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """更新用户信息（管理员或用户本人）"""
    current_user = get_user_from_header(request)
    
    # 检查权限
    if current_user["role"] != UserRole.ADMIN.value and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user_repo = UserRepository()
    user = user_repo.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新用户信息
    updated_user = user_repo.update(db, user, **user_update.model_dump(exclude_unset=True))
    
    return UserResponse.model_validate(updated_user)


@router.delete("/{user_id}", response_model=ResponseModel)
async def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """删除用户（仅管理员）"""
    current_user = get_user_from_header(request)
    
    # 检查管理员权限
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user_repo = UserRepository()
    user = user_repo.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 软删除：更新状态为已删除
    user_repo.update(db, user, status=UserStatus.BANNED)
    
    return ResponseModel(
        code=200,
        message="用户删除成功"
    )


@router.post("/{user_id}/upgrade-vip", response_model=UserResponse)
async def upgrade_user_vip(
    user_id: int,
    vip_type: VIPType,
    days: int = Query(30, ge=1, description="VIP天数"),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """升级用户VIP（仅管理员）"""
    current_user = get_user_from_header(request)
    
    # 检查管理员权限
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user_repo = UserRepository()
    user = user_repo.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 计算过期时间
    from datetime import datetime, timedelta
    expire_time = datetime.now() + timedelta(days=days)
    
    # 更新VIP状态
    updated_user = user_repo.update_vip_status(db, user_id, vip_type, expire_time)
    
    return UserResponse.model_validate(updated_user)


@router.get("/{user_id}/statistics", response_model=ResponseModel)
async def get_user_statistics(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """获取用户统计信息"""
    current_user = get_user_from_header(request)
    
    # 检查权限
    if current_user["role"] != UserRole.ADMIN.value and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user_repo = UserRepository()
    user = user_repo.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 构建统计信息
    statistics = {
        "user_id": user.id,
        "total_corrections": user.total_corrections,
        "total_questions": user.total_questions,
        "accuracy_rate": float(user.accuracy_rate) if user.accuracy_rate else 0.0,
        "daily_quota": user.daily_quota,
        "daily_used": user.daily_used,
        "vip_type": user.vip_type.value,
        "vip_expire_time": user.vip_expire_time.isoformat() if user.vip_expire_time else None,
        "member_since": user.created_at.isoformat()
    }
    
    return ResponseModel(
        code=200,
        message="获取用户统计信息成功",
        data=statistics
    )


@router.post("/reset-daily-quota", response_model=ResponseModel)
async def reset_daily_quota(request: Request, db: Session = Depends(get_db)):
    """重置所有用户每日配额（仅管理员）"""
    current_user = get_user_from_header(request)
    
    # 检查管理员权限
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user_repo = UserRepository()
    affected_rows = user_repo.reset_daily_quota(db)
    
    return ResponseModel(
        code=200,
        message=f"重置每日配额成功，影响用户数: {affected_rows}"
    )