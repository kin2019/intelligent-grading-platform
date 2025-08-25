"""
学生管理API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from ....shared.models.user import (
    StudentResponse, StudentCreate, StudentUpdate,
    UserRole, GradeLevel
)
from ....shared.models.base import ResponseModel, PaginatedResponseModel, PaginationModel
from ....shared.utils.database import get_db
from ..repositories.user_repository import StudentRepository, UserRepository

router = APIRouter()


def get_user_from_header(request: Request) -> dict:
    """从请求头获取用户信息"""
    return {
        "id": int(request.headers.get("X-User-ID")),
        "role": request.headers.get("X-User-Role"),
        "openid": request.headers.get("X-User-OpenID"),
        "vip_type": request.headers.get("X-User-VIP-Type")
    }


@router.post("/", response_model=StudentResponse)
async def create_student(
    student_data: StudentCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """创建学生"""
    current_user = get_user_from_header(request)
    
    # 检查权限：只有家长可以创建学生，或者管理员
    if current_user["role"] not in [UserRole.PARENT.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 家长只能为自己创建学生
    if current_user["role"] == UserRole.PARENT.value and student_data.parent_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能为自己创建学生档案"
        )
    
    # 验证家长是否存在
    user_repo = UserRepository()
    parent = user_repo.get_by_id(db, student_data.parent_id)
    if not parent or parent.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="家长用户不存在"
        )
    
    # 创建学生
    student_repo = StudentRepository()
    student = student_repo.create(db, **student_data.model_dump())
    
    return StudentResponse.model_validate(student)


@router.get("/", response_model=PaginatedResponseModel)
async def get_students(
    request: Request,
    grade: Optional[GradeLevel] = Query(None, description="年级筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取学生列表"""
    current_user = get_user_from_header(request)
    
    student_repo = StudentRepository()
    
    # 根据用户角色获取不同的学生列表
    if current_user["role"] == UserRole.PARENT.value:
        # 家长只能看到自己的学生
        students = student_repo.get_by_parent_id(db, current_user["id"])
        total = len(students)
        
        # 应用分页
        start = (page - 1) * size
        end = start + size
        students = students[start:end]
        
    elif current_user["role"] == UserRole.TEACHER.value:
        # 教师看到自己负责的学生
        # 首先获取教师ID
        from ..repositories.user_repository import TeacherRepository
        teacher_repo = TeacherRepository()
        teacher = teacher_repo.get_by_user_id(db, current_user["id"])
        
        if teacher:
            students = student_repo.get_by_teacher_id(db, teacher.id)
        else:
            students = []
        
        total = len(students)
        
        # 应用分页
        start = (page - 1) * size
        end = start + size
        students = students[start:end]
        
    elif current_user["role"] == UserRole.ADMIN.value:
        # 管理员可以看到所有学生
        if keyword:
            students = student_repo.search_students(db, keyword, grade, None, (page - 1) * size, size)
            total = len(students)  # 简化处理
        else:
            if grade:
                students = student_repo.get_by_grade(db, grade, (page - 1) * size, size)
            else:
                students = student_repo.get_multi(db, (page - 1) * size, size)
            total = student_repo.count(db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 转换为响应模型
    student_responses = [StudentResponse.model_validate(student) for student in students]
    
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
        message="获取学生列表成功",
        data=student_responses,
        pagination=pagination
    )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student_by_id(
    student_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """根据ID获取学生信息"""
    current_user = get_user_from_header(request)
    
    student_repo = StudentRepository()
    student = student_repo.get_by_id(db, student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )
    
    # 检查权限：家长只能查看自己的学生，教师可以查看负责的学生，管理员可以查看所有
    if current_user["role"] == UserRole.PARENT.value:
        if student.parent_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    elif current_user["role"] == UserRole.TEACHER.value:
        # 检查是否是该教师负责的学生
        from ..repositories.user_repository import TeacherRepository
        teacher_repo = TeacherRepository()
        teacher = teacher_repo.get_by_user_id(db, current_user["id"])
        
        if not teacher or student.teacher_id != teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    elif current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return StudentResponse.model_validate(student)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_update: StudentUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """更新学生信息"""
    current_user = get_user_from_header(request)
    
    student_repo = StudentRepository()
    student = student_repo.get_by_id(db, student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )
    
    # 检查权限：家长只能修改自己的学生，教师和管理员可以修改负责的学生
    if current_user["role"] == UserRole.PARENT.value:
        if student.parent_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    elif current_user["role"] == UserRole.TEACHER.value:
        # 教师可以修改负责的学生，但不能修改家长关联
        if student_update.teacher_id is not None:
            student_update.teacher_id = None  # 教师不能修改教师分配
        
        from ..repositories.user_repository import TeacherRepository
        teacher_repo = TeacherRepository()
        teacher = teacher_repo.get_by_user_id(db, current_user["id"])
        
        if not teacher or student.teacher_id != teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    elif current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 如果要分配教师，验证教师是否存在且已认证
    if student_update.teacher_id is not None:
        from ..repositories.user_repository import TeacherRepository
        teacher_repo = TeacherRepository()
        teacher = teacher_repo.get_by_id(db, student_update.teacher_id)
        
        if not teacher or not teacher.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="教师不存在或未认证"
            )
    
    # 更新学生信息
    updated_student = student_repo.update(db, student, **student_update.model_dump(exclude_unset=True))
    
    return StudentResponse.model_validate(updated_student)


@router.delete("/{student_id}", response_model=ResponseModel)
async def delete_student(
    student_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """删除学生"""
    current_user = get_user_from_header(request)
    
    student_repo = StudentRepository()
    student = student_repo.get_by_id(db, student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )
    
    # 检查权限：只有家长（学生的家长）和管理员可以删除
    if current_user["role"] == UserRole.PARENT.value:
        if student.parent_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    elif current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 删除学生
    student_repo.delete(db, student_id)
    
    return ResponseModel(
        code=200,
        message="学生删除成功"
    )


@router.post("/{student_id}/assign-teacher", response_model=StudentResponse)
async def assign_teacher_to_student(
    student_id: int,
    teacher_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """为学生分配教师"""
    current_user = get_user_from_header(request)
    
    # 只有管理员可以分配教师
    if current_user["role"] != UserRole.ADMIN.value:
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
    
    # 验证教师是否存在且已认证
    from ..repositories.user_repository import TeacherRepository
    teacher_repo = TeacherRepository()
    teacher = teacher_repo.get_by_id(db, teacher_id)
    
    if not teacher or not teacher.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="教师不存在或未认证"
        )
    
    # 分配教师
    updated_student = student_repo.assign_teacher(db, student_id, teacher_id)
    
    # 更新教师学生数统计
    teacher_repo.update_statistics(db, teacher_id, students=1)
    
    return StudentResponse.model_validate(updated_student)


@router.get("/{student_id}/statistics", response_model=ResponseModel)
async def get_student_statistics(
    student_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """获取学生学习统计"""
    current_user = get_user_from_header(request)
    
    student_repo = StudentRepository()
    student = student_repo.get_by_id(db, student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生不存在"
        )
    
    # 检查权限
    if current_user["role"] == UserRole.PARENT.value:
        if student.parent_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    elif current_user["role"] == UserRole.TEACHER.value:
        from ..repositories.user_repository import TeacherRepository
        teacher_repo = TeacherRepository()
        teacher = teacher_repo.get_by_user_id(db, current_user["id"])
        
        if not teacher or student.teacher_id != teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    elif current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 构建统计信息
    statistics = {
        "student_id": student.id,
        "name": student.name,
        "grade": student.grade.value,
        "total_homework": student.total_homework,
        "completed_homework": student.completed_homework,
        "completion_rate": (student.completed_homework / student.total_homework * 100) if student.total_homework > 0 else 0,
        "average_score": float(student.average_score) if student.average_score else 0.0,
        "school": student.school,
        "class_name": student.class_name,
        "created_at": student.created_at.isoformat()
    }
    
    return ResponseModel(
        code=200,
        message="获取学生统计信息成功",
        data=statistics
    )