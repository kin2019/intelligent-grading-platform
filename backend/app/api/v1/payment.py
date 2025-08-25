from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
import json
import time
import random
import uuid
from datetime import datetime, timedelta

router = APIRouter()

class VIPPlan(BaseModel):
    """VIP套餐信息"""
    id: str
    name: str
    description: str
    price: float
    original_price: float
    duration_days: int
    daily_quota: int
    features: List[str]
    is_popular: bool

class PaymentOrder(BaseModel):
    """支付订单"""
    order_id: str
    plan_id: str
    amount: float
    status: str
    payment_method: str
    created_at: str
    expires_at: str

class VIPStatus(BaseModel):
    """VIP状态"""
    is_vip: bool
    vip_type: Optional[str]
    expire_date: Optional[str]
    remaining_days: Optional[int]
    daily_quota: int
    monthly_quota: int
    total_used: int

@router.get("/plans", summary="获取VIP套餐列表")
def get_vip_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有VIP套餐信息
    
    包括价格、功能对比等
    """
    plans = [
        {
            "id": "monthly",
            "name": "月度VIP",
            "description": "适合短期使用，性价比高",
            "price": 29.9,
            "original_price": 39.9,
            "duration_days": 30,
            "daily_quota": 50,
            "features": [
                "每日50次批改额度",
                "无限错题本存储",
                "AI学习报告",
                "优先客服支持",
                "高级批改功能"
            ],
            "is_popular": False
        },
        {
            "id": "quarterly",
            "name": "季度VIP",
            "description": "最受欢迎的选择，平均每月仅需20元",
            "price": 59.9,
            "original_price": 89.7,
            "duration_days": 90,
            "daily_quota": 80,
            "features": [
                "每日80次批改额度",
                "无限错题本存储",
                "AI学习报告",
                "优先客服支持",
                "高级批改功能",
                "专属学习计划",
                "学科专项训练"
            ],
            "is_popular": True
        },
        {
            "id": "yearly",
            "name": "年度VIP",
            "description": "超值选择，享受全年无忧学习",
            "price": 199.9,
            "original_price": 358.8,
            "duration_days": 365,
            "daily_quota": 120,
            "features": [
                "每日120次批改额度",
                "无限错题本存储",
                "AI学习报告",
                "优先客服支持",
                "高级批改功能",
                "专属学习计划",
                "学科专项训练",
                "一对一学习指导",
                "家长深度报告"
            ],
            "is_popular": False
        }
    ]
    
    return {
        "plans": plans,
        "current_vip_status": {
            "is_vip": getattr(current_user, 'is_vip', False),
            "vip_type": "free",
            "expire_date": None,
            "daily_quota": getattr(current_user, 'daily_quota', 5)
        }
    }

@router.post("/create-order", summary="创建支付订单")
def create_payment_order(
    plan_id: str = Form(..., description="套餐ID"),
    payment_method: str = Form(default="wechat", description="支付方式"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建支付订单
    
    - **plan_id**: VIP套餐ID
    - **payment_method**: 支付方式 (wechat/alipay)
    """
    # 验证套餐
    valid_plans = {
        "monthly": {"price": 29.9, "name": "月度VIP"},
        "quarterly": {"price": 59.9, "name": "季度VIP"},
        "yearly": {"price": 199.9, "name": "年度VIP"}
    }
    
    if plan_id not in valid_plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的套餐ID"
        )
    
    plan = valid_plans[plan_id]
    order_id = f"order_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # 模拟订单创建
    order = {
        "order_id": order_id,
        "user_id": current_user.id,
        "plan_id": plan_id,
        "plan_name": plan["name"],
        "amount": plan["price"],
        "payment_method": payment_method,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat(),
        "payment_url": f"https://pay.example.com/{payment_method}/{order_id}"
    }
    
    return order

@router.get("/orders", summary="获取支付订单历史")
def get_payment_orders(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的支付订单历史
    
    - **page**: 页码
    - **limit**: 每页数量
    - **status**: 状态筛选 (pending/paid/cancelled/expired)
    """
    # 模拟订单历史
    orders = []
    for i in range(limit):
        order_status = random.choice(["pending", "paid", "cancelled", "expired"])
        if status and order_status != status:
            continue
            
        order = {
            "order_id": f"order_{int(time.time())}_{i}",
            "plan_name": random.choice(["月度VIP", "季度VIP", "年度VIP"]),
            "amount": random.choice([29.9, 59.9, 199.9]),
            "status": order_status,
            "payment_method": random.choice(["wechat", "alipay"]),
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "paid_at": (datetime.now() - timedelta(days=random.randint(0, 29))).isoformat() if order_status == "paid" else None
        }
        orders.append(order)
    
    return {
        "total": len(orders),
        "page": page,
        "limit": limit,
        "orders": orders
    }

@router.post("/verify-payment", summary="验证支付结果")
def verify_payment(
    order_id: str = Form(..., description="订单ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    验证支付结果并激活VIP
    
    - **order_id**: 订单ID
    """
    # 模拟支付验证
    # 在实际应用中，这里会调用支付平台的API验证支付状态
    
    # 随机模拟支付成功/失败
    is_paid = random.choice([True, True, True, False])  # 75%成功率
    
    if not is_paid:
        return {
            "order_id": order_id,
            "status": "failed",
            "message": "支付未完成或已取消",
            "verified_at": datetime.now().isoformat()
        }
    
    # 模拟VIP激活
    plan_mapping = {
        "monthly": {"days": 30, "quota": 50},
        "quarterly": {"days": 90, "quota": 80},
        "yearly": {"days": 365, "quota": 120}
    }
    
    # 假设订单对应季度VIP
    plan = plan_mapping["quarterly"]
    expire_date = datetime.now() + timedelta(days=plan["days"])
    
    # 在实际应用中，这里会更新数据库中的用户VIP状态
    return {
        "order_id": order_id,
        "status": "success",
        "message": "支付成功，VIP已激活",
        "vip_info": {
            "is_vip": True,
            "vip_type": "quarterly",
            "expire_date": expire_date.isoformat(),
            "daily_quota": plan["quota"]
        },
        "verified_at": datetime.now().isoformat()
    }

@router.get("/vip-status", response_model=VIPStatus, summary="获取VIP状态")
def get_vip_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的VIP状态详情
    """
    # 模拟VIP状态
    is_vip = getattr(current_user, 'is_vip', False) or random.choice([True, False])
    
    if is_vip:
        expire_date = datetime.now() + timedelta(days=random.randint(1, 365))
        remaining_days = (expire_date - datetime.now()).days
        vip_type = random.choice(["monthly", "quarterly", "yearly"])
        daily_quota = {"monthly": 50, "quarterly": 80, "yearly": 120}[vip_type]
    else:
        expire_date = None
        remaining_days = 0
        vip_type = "free"
        daily_quota = 5
    
    return {
        "is_vip": is_vip,
        "vip_type": vip_type,
        "expire_date": expire_date.isoformat() if expire_date else None,
        "remaining_days": remaining_days,
        "daily_quota": daily_quota,
        "monthly_quota": daily_quota * 30,
        "total_used": random.randint(50, 500)
    }

@router.post("/cancel-order", summary="取消订单")
def cancel_order(
    order_id: str = Form(..., description="订单ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取消未支付的订单
    
    - **order_id**: 订单ID
    """
    # 在实际应用中，这里会检查订单状态并更新
    return {
        "order_id": order_id,
        "status": "cancelled",
        "message": "订单已取消",
        "cancelled_at": datetime.now().isoformat()
    }

@router.get("/usage-statistics", summary="获取使用统计")
def get_usage_statistics(
    period: str = "month",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的使用统计数据
    
    - **period**: 统计周期 (week/month/year)
    """
    # 模拟使用统计
    total_corrections = random.randint(100, 500)
    period_corrections = random.randint(20, total_corrections)
    
    return {
        "period": period,
        "vip_status": {
            "is_vip": getattr(current_user, 'is_vip', False),
            "daily_quota": getattr(current_user, 'daily_quota', 5)
        },
        "usage": {
            "total_corrections": total_corrections,
            "period_corrections": period_corrections,
            "daily_average": round(period_corrections / 30, 1),
            "quota_utilization": round(period_corrections / (getattr(current_user, 'daily_quota', 5) * 30), 2)
        },
        "trends": [
            {
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "corrections": random.randint(0, 8),
                "quota_used": random.randint(0, 5)
            }
            for i in range(7)
        ],
        "generated_at": datetime.now().isoformat()
    }

@router.post("/redeem-code", summary="兑换优惠码")
def redeem_code(
    code: str = Form(..., description="优惠码"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    兑换优惠码
    
    - **code**: 优惠码
    """
    # 模拟优惠码验证
    valid_codes = {
        "VIP30": {"type": "discount", "value": 30, "description": "30%折扣券"},
        "FREE7": {"type": "free_trial", "value": 7, "description": "7天免费试用"},
        "QUOTA50": {"type": "quota", "value": 50, "description": "50次批改额度"}
    }
    
    if code not in valid_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的优惠码"
        )
    
    reward = valid_codes[code]
    
    return {
        "code": code,
        "status": "success",
        "reward": reward,
        "message": f"优惠码兑换成功：{reward['description']}",
        "redeemed_at": datetime.now().isoformat()
    }