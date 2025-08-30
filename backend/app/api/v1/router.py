from fastapi import APIRouter
from app.api.v1 import auth, homework, student, image, parent, teacher, payment, user, bind, support, exercise

api_router = APIRouter()

# 认证相关路由
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["认证"]
)

# 作业批改相关路由  
api_router.include_router(
    homework.router,
    prefix="/homework", 
    tags=["作业批改"]
)

# 学生端相关路由
api_router.include_router(
    student.router,
    prefix="/student",
    tags=["学生端"]
)

# 家长端相关路由 
api_router.include_router(
    parent.router,
    prefix="/parent",
    tags=["家长端"]
)

# 家长绑定相关路由
api_router.include_router(
    bind.router,
    prefix="/bind",
    tags=["家长绑定"]
)

# 教师端相关路由
api_router.include_router(
    teacher.router,
    prefix="/teacher",
    tags=["教师端"]
)

# 图片处理相关路由
api_router.include_router(
    image.router,
    prefix="/image",
    tags=["图片处理"]
)

# 支付和VIP相关路由
api_router.include_router(
    payment.router,
    prefix="/payment",
    tags=["支付VIP"]
)

# 用户管理相关路由
api_router.include_router(
    user.router,
    prefix="/user",
    tags=["用户管理"]
)

# 客服支持相关路由
api_router.include_router(
    support.router,
    prefix="/support",
    tags=["客服支持"]
)

# 智能出题相关路由
api_router.include_router(
    exercise.router,
    prefix="/exercise",
    tags=["智能出题"]
)

# 临时移除问题模块