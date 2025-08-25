"""
教师管理API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from ....shared.models.user import (
    TeacherResponse, TeacherCreate, TeacherUpdate, StudentResponse,
    UserRole, GradeLevel
)
from ....shared.models.base import ResponseModel, PaginatedResponseModel, PaginationModel
from ....shared.utils.database import get_db
from ..repositories.user_repository import TeacherRepository, StudentRepository, UserRepository

router = APIRouter()


def get_user_from_header(request: Request) -> dict:
    """从请求头获取用户信息"""
    return {
        "id": int(request.headers.get("X-User-ID")),
        "role": request.headers.get("X-User-Role"),
        "openid": request.headers.get("X-User-OpenID"),
        "vip_type": request.headers.get("X-User-VIP-Type")
    }


@router.post("/register", response_model=TeacherResponse)
async def register_teacher(
    teacher_data: TeacherCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """教师注册申请"""
    current_user = get_user_from_header(request)
    
    # 检查用户是否已是教师
    teacher_repo = TeacherRepository()
    existing_teacher = teacher_repo.get_by_user_id(db, current_user["id"])
    if existing_teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经是注册教师"
        )
    
    # 检查身份证是否已被使用
    existing_id_card = teacher_repo.get_by_id_card(db, teacher_data.id_card)
    if existing_id_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="身份证号已被使用"
        )
    
    # 创建教师记录
    teacher_data.user_id = current_user["id"]
    teacher = teacher_repo.create(db, **teacher_data.model_dump())
    
    # 更新用户角色为教师
    user_repo = UserRepository()
    user_repo.update(db, user_repo.get_by_id(db, current_user["id"]), role=UserRole.TEACHER)
    
    return TeacherResponse.model_validate(teacher)


@router.get("/my-profile", response_model=TeacherResponse)
async def get_my_teacher_profile(request: Request, db: Session = Depends(get_db)):
    """获取我的教师资料"""
    current_user = get_user_from_header(request)
    
    if current_user["role"] != UserRole.TEACHER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    teacher_repo = TeacherRepository()
    teacher = teacher_repo.get_by_user_id(db, current_user["id"])
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教师资料不存在"
        )
    
    return TeacherResponse.model_validate(teacher)


@router.get("/my-students", response_model=List[StudentResponse])
async def get_my_students(request: Request, db: Session = Depends(get_db)):
    """获取我负责的学生列表"""
    current_user = get_user_from_header(request)
    
    if current_user["role"] != UserRole.TEACHER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    teacher_repo = TeacherRepository()
    teacher = teacher_repo.get_by_user_id(db, current_user["id"])
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教师资料不存在"
        )
    
    student_repo = StudentRepository()
    students = student_repo.get_by_teacher_id(db, teacher.id)
    
    return [StudentResponse.model_validate(student) for student in students]


@router.get("/", response_model=PaginatedResponseModel)
async def get_teachers(
    request: Request,
    verified: Optional[bool] = Query(None, description="认证状态筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取教师列表（仅管理员）"""
    current_user = get_user_from_header(request)
    
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    teacher_repo = TeacherRepository()
    
    if keyword:
        teachers = teacher_repo.search_teachers(db, keyword, verified, (page - 1) * size, size)
        total = len(teachers)
    else:
        if verified is not None:
            if verified:
                teachers = teacher_repo.get_verified_teachers(db, (page - 1) * size, size)
            else:
                teachers = teacher_repo.get_pending_verification(db, (page - 1) * size, size)
        else:
            teachers = teacher_repo.get_multi(db, (page - 1) * size, size)
        
        total = teacher_repo.count(db)
    
    teacher_responses = [TeacherResponse.model_validate(teacher) for teacher in teachers]
    
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
        message="获取教师列表成功",
        data=teacher_responses,
        pagination=pagination
    )


@router.post("/{teacher_id}/verify", response_model=TeacherResponse)
async def verify_teacher(
    teacher_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """认证教师（仅管理员）"""
    current_user = get_user_from_header(request)
    
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    teacher_repo = TeacherRepository()
    teacher = teacher_repo.get_by_id(db, teacher_id)
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教师不存在"
        )
    
    if teacher.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="教师已经认证"
        )
    
    verified_teacher = teacher_repo.verify_teacher(db, teacher_id)
    
    return TeacherResponse.model_validate(verified_teacher)


@router.get("/dashboard", response_model=ResponseModel)
async def get_teacher_dashboard(request: Request, db: Session = Depends(get_db)):
    """获取教师仪表板"""
    current_user = get_user_from_header(request)
    
    if current_user["role"] != UserRole.TEACHER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    teacher_repo = TeacherRepository()
    teacher = teacher_repo.get_by_user_id(db, current_user["id"])
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教师资料不存在"
        )
    
    student_repo = StudentRepository()
    students = student_repo.get_by_teacher_id(db, teacher.id)
    
    dashboard_data = {
        "teacher_id": teacher.id,
        "verification_status": teacher.is_verified,
        "total_students": len(students),
        "total_corrections": teacher.total_corrections,
        "rating": float(teacher.rating) if teacher.rating else 0.0,
        "total_income": float(teacher.total_income),
        "available_withdrawal": float(teacher.total_income - teacher.withdraw_amount),
        "recent_activities": [
            {"time": "2小时前", "activity": "批改了小明的数学作业"},
            {"time": "昨天", "activity": "为小红解答了英语问题"},
            {"time": "2天前", "activity": "完成了班级学情分析"}
        ],
        "student_performance": [
            {"name": "小明", "recent_score": 85, "trend": "improving"},
            {"name": "小红", "recent_score": 92, "trend": "stable"},
            {"name": "小李", "recent_score": 78, "trend": "declining"}
        ]
    }
    
    return ResponseModel(
        code=200,
        message="获取教师仪表板成功",
        data=dashboard_data
    )