from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
import json
import time
import random
import base64
from datetime import datetime, timedelta

router = APIRouter()

class OCRResponse(BaseModel):
    """OCR识别响应"""
    image_id: str
    recognized_text: str
    confidence: float
    detected_regions: List[Dict[str, Any]]
    processing_time: float

class ImageProcessResponse(BaseModel):
    """图片处理响应"""
    original_url: str
    processed_url: str
    processing_steps: List[str]
    image_info: Dict[str, Any]

@router.post("/ocr", response_model=OCRResponse, summary="图片OCR文字识别")
async def image_ocr(
    file: UploadFile = File(..., description="需要识别的图片文件"),
    language: str = Form(default="zh", description="识别语言(zh/en)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    对上传的图片进行OCR文字识别
    
    - **file**: 图片文件 (jpg, png, jpeg)
    - **language**: 识别语言 (zh=中文, en=英文)
    
    返回识别的文字内容和位置信息
    """
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持图片文件"
        )
    
    # 验证文件大小
    if file.size and file.size > 5 * 1024 * 1024:  # 5MB限制
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片文件大小不能超过5MB"
        )
    
    start_time = time.time()
    
    # 模拟OCR处理
    # 在实际应用中，这里会调用真实的OCR服务如百度OCR、腾讯OCR等
    image_id = f"ocr_{int(time.time())}_{current_user.id}"
    
    # 模拟识别结果
    if language == "zh":
        mock_text = """
        1. 计算下列各题：
        (1) 25 + 37 = 62
        (2) 84 - 29 = 55
        (3) 15 × 6 = 90
        (4) 96 ÷ 8 = 12
        
        2. 解决问题：
        小明有45个苹果，吃掉了18个，还剩多少个？
        答：45 - 18 = 27（个）
        """
    else:
        mock_text = """
        1. Calculate the following:
        (1) 25 + 37 = 62
        (2) 84 - 29 = 55
        (3) 15 × 6 = 90
        (4) 96 ÷ 8 = 12
        
        2. Word problem:
        Tom has 45 apples, he ate 18. How many are left?
        Answer: 45 - 18 = 27 apples
        """
    
    # 模拟文字区域检测
    detected_regions = [
        {
            "text": "1. 计算下列各题：",
            "confidence": 0.95,
            "bbox": {"x": 50, "y": 100, "width": 200, "height": 30},
            "type": "title"
        },
        {
            "text": "(1) 25 + 37 = 62",
            "confidence": 0.98,
            "bbox": {"x": 70, "y": 140, "width": 150, "height": 25},
            "type": "equation"
        },
        {
            "text": "(2) 84 - 29 = 55",
            "confidence": 0.97,
            "bbox": {"x": 70, "y": 170, "width": 150, "height": 25},
            "type": "equation"
        },
        {
            "text": "小明有45个苹果，吃掉了18个，还剩多少个？",
            "confidence": 0.93,
            "bbox": {"x": 50, "y": 250, "width": 350, "height": 30},
            "type": "question"
        }
    ]
    
    processing_time = time.time() - start_time
    
    return {
        "image_id": image_id,
        "recognized_text": mock_text.strip(),
        "confidence": round(random.uniform(0.90, 0.99), 2),
        "detected_regions": detected_regions,
        "processing_time": round(processing_time, 2)
    }

@router.post("/process", response_model=ImageProcessResponse, summary="图片预处理")
async def process_image(
    file: UploadFile = File(..., description="需要处理的图片文件"),
    enhance: bool = Form(default=True, description="是否增强图片质量"),
    rotate: bool = Form(default=True, description="是否自动旋转"),
    crop: bool = Form(default=True, description="是否智能裁剪"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    对图片进行预处理以提高OCR识别准确率
    
    - **file**: 原始图片文件
    - **enhance**: 是否进行图片增强
    - **rotate**: 是否自动纠正旋转
    - **crop**: 是否智能裁剪边缘
    
    返回处理后的图片URL和处理信息
    """
    # 验证文件
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持图片文件"
        )
    
    # 模拟图片处理
    original_url = f"https://example.com/original/{int(time.time())}.jpg"
    processed_url = f"https://example.com/processed/{int(time.time())}.jpg"
    
    processing_steps = []
    if enhance:
        processing_steps.append("图片质量增强")
    if rotate:
        processing_steps.append("自动旋转纠正")
    if crop:
        processing_steps.append("智能边缘裁剪")
    
    # 模拟图片信息
    image_info = {
        "original_size": {"width": 1920, "height": 1080},
        "processed_size": {"width": 1800, "height": 1000},
        "format": "JPEG",
        "quality_score": round(random.uniform(0.85, 0.98), 2),
        "rotation_angle": random.choice([0, 90, 180, 270]) if rotate else 0,
        "crop_area": {"x": 60, "y": 40, "width": 1800, "height": 1000} if crop else None
    }
    
    return {
        "original_url": original_url,
        "processed_url": processed_url,
        "processing_steps": processing_steps,
        "image_info": image_info
    }

@router.get("/history", summary="获取图片处理历史")
def get_image_history(
    page: int = 1,
    limit: int = 20,
    image_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的图片处理历史记录
    
    - **page**: 页码
    - **limit**: 每页数量
    - **image_type**: 图片类型筛选 (homework/test/exercise)
    """
    # 模拟历史记录
    mock_history = []
    for i in range(limit):
        record = {
            "id": i + 1,
            "image_url": f"https://example.com/image_{i+1}.jpg",
            "image_type": random.choice(["homework", "test", "exercise"]),
            "ocr_text": f"这是第{i+1}张图片的识别文本内容...",
            "confidence": round(random.uniform(0.85, 0.99), 2),
            "processing_time": round(random.uniform(1.0, 5.0), 2),
            "status": random.choice(["completed", "processing", "failed"]),
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "file_size": random.randint(100, 5000),  # KB
            "dimensions": {
                "width": random.randint(800, 2000),
                "height": random.randint(600, 1500)
            }
        }
        
        # 类型筛选
        if image_type and record["image_type"] != image_type:
            continue
            
        mock_history.append(record)
    
    return {
        "total": len(mock_history),
        "page": page,
        "limit": limit,
        "history": mock_history
    }

@router.delete("/{image_id}", summary="删除图片记录")
def delete_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除指定的图片记录
    
    - **image_id**: 图片ID
    """
    # 在实际应用中，这里会从数据库和存储中删除图片
    return {
        "message": f"图片 {image_id} 已删除",
        "deleted_at": datetime.now().isoformat()
    }

@router.post("/batch-ocr", summary="批量OCR识别")
async def batch_ocr(
    files: List[UploadFile] = File(..., description="多个图片文件"),
    language: str = Form(default="zh", description="识别语言"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量处理多张图片的OCR识别
    
    - **files**: 多个图片文件
    - **language**: 识别语言
    
    适用于多页作业的批量处理
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="单次最多支持10张图片"
        )
    
    results = []
    for i, file in enumerate(files):
        # 验证文件
        if not file.content_type or not file.content_type.startswith('image/'):
            results.append({
                "file_name": file.filename,
                "status": "error",
                "message": "不支持的文件格式"
            })
            continue
        
        # 模拟OCR处理
        image_id = f"batch_{int(time.time())}_{i}_{current_user.id}"
        mock_text = f"第{i+1}页识别内容：\n1. 题目内容...\n2. 答案内容..."
        
        results.append({
            "file_name": file.filename,
            "image_id": image_id,
            "status": "success",
            "recognized_text": mock_text,
            "confidence": round(random.uniform(0.85, 0.98), 2),
            "processing_time": round(random.uniform(1.0, 3.0), 2)
        })
    
    return {
        "total_files": len(files),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results,
        "batch_id": f"batch_{int(time.time())}_{current_user.id}",
        "created_at": datetime.now().isoformat()
    }