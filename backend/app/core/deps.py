from typing import Generator, Optional
from datetime import datetime, date, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User

# HTTP Bearer Token认证
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    print(f"DEBUG: Received token: {token}")
    
    # 临时测试：直接返回ID=1的用户，跳过token验证 
    if token == "test-token-123":
        print("DEBUG: Using test token bypass")
        # 从数据库获取真实的用户记录
        user = db.query(User).filter(User.id == 1).first()
        if user:
            print(f"DEBUG: Found real user ID=1: {user.nickname}")
            return user
        else:
            print("DEBUG: User ID=1 not found, creating new user")
            # 如果找不到用户，创建一个新的用户记录
            user = User(
                openid="test_user_1",
                unionid="test_user_1",
                nickname="测试用户",
                role="student",
                is_active=True,
                avatar_url=None,
                grade="五年级",
                phone=None,
                email=None,
                is_vip=False,
                vip_expire_time=None,
                daily_quota=5,
                daily_used=0,
                total_used=0,
                settings=None
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
    
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 查询用户，如果不存在则创建模拟用户
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        # 创建模拟用户用于测试
        user = User(
            openid=user_id,
            unionid=f"mock_openid_{user_id}",
            nickname="测试用户",
            role="student",
            is_active=True,
            is_vip=False,
            daily_quota=5,
            daily_used=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="用户账号已被禁用"
        )
    return current_user

def get_db_session() -> Generator:
    """获取数据库会话（同步版本，用于依赖注入）"""
    return Depends(get_db)


# ==================== VIP权限控制 ====================

def check_vip_status(user: User, db: Session) -> dict:
    """检查用户VIP状态并更新相关信息"""
    now = datetime.now()
    today = now.date()
    
    # 检查VIP是否过期
    is_vip_active = False
    if user.is_vip:
        if user.vip_expire_time:
            is_vip_active = user.vip_expire_time > now
            if not is_vip_active:
                # VIP已过期，更新状态
                user.is_vip = False
                user.vip_expire_time = None
                db.commit()
        else:
            # 没有过期时间的VIP用户（永久VIP或数据问题）
            is_vip_active = True
    
    # 检查并重置每日额度
    if user.last_quota_reset != today:
        user.daily_used = 0
        user.last_quota_reset = today
        db.commit()
    
    # 计算剩余额度
    if is_vip_active:
        remaining_quota = -1  # VIP用户无限制，用-1表示
    else:
        remaining_quota = max(0, user.daily_quota - user.daily_used)
    
    return {
        'is_vip': is_vip_active,
        'daily_quota': user.daily_quota,
        'daily_used': user.daily_used,
        'remaining_quota': remaining_quota,
        'total_used': user.total_used,
        'vip_expire_time': user.vip_expire_time.isoformat() if user.vip_expire_time else None
    }


def get_current_user_with_quota(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> tuple[User, dict]:
    """获取当前用户并返回VIP状态信息（不检查使用限制）"""
    vip_status = check_vip_status(current_user, db)
    return current_user, vip_status


def check_exercise_generation_permission(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> tuple[User, dict]:
    """检查出题权限 - 基于VIP系统控制出题次数"""
    vip_status = check_vip_status(current_user, db)
    
    # VIP用户无限制使用
    if vip_status['is_vip']:
        return current_user, vip_status
    
    # 普通用户检查每日限制
    if vip_status['remaining_quota'] <= 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "QUOTA_EXCEEDED",
                "message": f"今日出题次数已用完（{vip_status['daily_used']}/{vip_status['daily_quota']}），请明天再试或升级VIP享受无限制使用",
                "quota_info": {
                    "daily_quota": vip_status['daily_quota'],
                    "daily_used": vip_status['daily_used'],
                    "remaining_quota": 0,
                    "reset_time": (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + 
                                 timedelta(days=1)).isoformat()
                },
                "upgrade_suggestion": {
                    "title": "升级VIP享受无限制出题",
                    "benefits": [
                        "无限制智能出题",
                        "高级题目定制",
                        "优先AI生成",
                        "专属客户服务"
                    ]
                }
            }
        )
    
    return current_user, vip_status


def increment_usage_count(
    user: User,
    db: Session,
    operation_type: str = "exercise_generation"
) -> dict:
    """增加用户使用次数统计"""
    try:
        # 增加每日使用次数
        user.daily_used += 1
        
        # 增加总使用次数
        user.total_used += 1
        
        # 更新最后使用时间
        user.last_login_at = datetime.now()
        
        db.commit()
        
        # 重新获取VIP状态
        vip_status = check_vip_status(user, db)
        
        return {
            "success": True,
            "operation_type": operation_type,
            "usage_updated": {
                "daily_used": user.daily_used,
                "total_used": user.total_used,
                "remaining_quota": vip_status['remaining_quota']
            }
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": f"更新使用统计失败: {str(e)}"
        }


def get_user_usage_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取用户使用统计信息"""
    vip_status = check_vip_status(current_user, db)
    
    # 计算本月使用情况（简单实现，实际项目可能需要更复杂的统计）
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    # 这里简化处理，实际项目中应该有专门的使用记录表
    stats = {
        "user_id": current_user.id,
        "nickname": current_user.nickname,
        "role": current_user.role,
        "vip_info": vip_status,
        "usage_summary": {
            "today_used": vip_status['daily_used'],
            "today_quota": vip_status['daily_quota'],
            "today_remaining": vip_status['remaining_quota'],
            "total_used": vip_status['total_used']
        },
        "account_info": {
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "last_login": current_user.last_login_at.isoformat() if current_user.last_login_at else None
        }
    }
    
    return stats


# ==================== 角色权限控制 ====================

def require_admin_permission(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """要求管理员权限"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限才能访问此资源"
        )
    return current_user


def require_teacher_or_admin_permission(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """要求教师或管理员权限"""
    if not (current_user.is_teacher or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要教师或管理员权限才能访问此资源"
        )
    return current_user


def require_parent_or_admin_permission(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """要求家长或管理员权限"""
    if not (current_user.is_parent or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要家长或管理员权限才能访问此资源"
        )
    return current_user