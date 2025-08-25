"""
智能批改API
集成OCR文字识别和AI题目分析功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import os
import json
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.homework import Homework
from app.services.vision_ocr_service import VisionOCRService
from app.services.homework_analysis_ai import HomeworkAnalysisAI

router = APIRouter()


class IntelligentCorrectionRequest(BaseModel):
    """智能批改请求"""
    image_url: str = Field(..., description="作业图片URL")
    subject: str = Field(..., description="学科")
    grade: str = Field(..., description="年级")
    homework_title: str = Field(default="作业批改", description="作业标题")


class QuestionDetail(BaseModel):
    """题目详情"""
    question_number: int
    question_text: str
    question_type: str
    knowledge_points: List[str]
    difficulty_level: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    correctness_score: float
    error_type: Optional[str]
    error_description: Optional[str]
    explanation: str
    improvement_suggestions: List[str]


class IntelligentCorrectionResult(BaseModel):
    """智能批改结果"""
    homework_id: str
    success: bool
    message: str
    
    # OCR提取结果
    ocr_confidence: float
    extracted_text: str
    text_regions_count: int
    
    # 批改结果
    subject: str
    grade: str
    total_questions: int
    correct_count: int
    wrong_count: int
    accuracy_rate: float
    overall_score: float
    
    # 题目详情
    question_details: List[QuestionDetail]
    
    # 分析报告
    performance_analysis: Dict[str, Any]
    learning_suggestions: List[str]
    time_spent_estimate: int
    
    # 元数据
    analysis_time: str
    ai_version: str


class OCRAnalysisRequest(BaseModel):
    """OCR分析请求"""
    image_url: str = Field(..., description="图片URL")
    preprocessing: bool = Field(default=True, description="是否进行预处理")


@router.post("/ocr-extract", summary="OCR文字提取")
async def extract_text_from_image(
    request: OCRAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    使用OCR技术从作业图片中提取文字内容
    """
    try:
        # 验证用户权限
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要登录"
            )
        
        # 初始化OCR服务
        ocr_service = VisionOCRService()
        
        # 执行OCR提取
        ocr_result = ocr_service.extract_text_from_image(
            request.image_url, 
            preprocessing=request.preprocessing
        )
        
        if not ocr_result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OCR提取失败: {ocr_result['message']}"
            )
        
        # 获取提取统计信息
        statistics = ocr_service.get_text_statistics(ocr_result)
        
        return {
            'success': True,
            'message': ocr_result['message'],
            'extraction_result': {
                'raw_text': ocr_result['raw_text'],
                'total_regions': ocr_result['total_regions'],
                'confidence_score': ocr_result['confidence_score'],
                'structured_content': ocr_result['structured_content'],
                'text_regions': ocr_result['regions'][:10]  # 限制返回前10个区域
            },
            'statistics': statistics,
            'extraction_time': ocr_result['extraction_time']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"OCR提取异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR提取服务异常: {str(e)}"
        )


@router.post("/intelligent-correct", response_model=IntelligentCorrectionResult)
async def intelligent_homework_correction(
    request: IntelligentCorrectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    智能作业批改
    
    使用视觉模型提取图片中的文字，然后用专门的AI模型分析题目并给出批改结果
    """
    try:
        # 验证用户权限
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要登录"
            )
        
        print(f"开始智能批改，用户: {current_user.username}, 学科: {request.subject}")
        
        # 初始化AI分析服务
        analysis_ai = HomeworkAnalysisAI()
        
        # 执行智能分析
        correction_result = analysis_ai.analyze_homework_image(
            image_path=request.image_url,
            subject=request.subject,
            grade=request.grade,
            student_id=str(current_user.id)
        )
        
        # 检查分析是否成功
        if correction_result.homework_id == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=correction_result.learning_suggestions[0] if correction_result.learning_suggestions else "分析失败"
            )
        
        # 保存作业记录到数据库
        homework = Homework(
            user_id=current_user.id,
            image_url=request.image_url,
            subject=request.subject,
            title=request.homework_title,
            total_questions=correction_result.total_questions,
            correct_count=correction_result.correct_count,
            wrong_count=correction_result.wrong_count,
            accuracy_rate=correction_result.accuracy_rate / 100,  # 转换为小数
            overall_score=correction_result.overall_score,
            status='completed',
            correction_results=json.dumps([
                {
                    'question_number': q['question_number'],
                    'question_text': q['question_text'],
                    'user_answer': q['user_answer'],
                    'correct_answer': q['correct_answer'],
                    'is_correct': q['is_correct'],
                    'explanation': q['explanation'],
                    'error_type': q['error_type'],
                    'knowledge_points': q['knowledge_points']
                }
                for q in correction_result.question_details
            ], ensure_ascii=False)
        )
        
        db.add(homework)
        db.commit()
        db.refresh(homework)
        
        print(f"作业记录已保存，ID: {homework.id}")
        
        # 转换为响应格式
        question_details = [
            QuestionDetail(
                question_number=q['question_number'],
                question_text=q['question_text'],
                question_type=q['question_type'],
                knowledge_points=q['knowledge_points'],
                difficulty_level=q['difficulty_level'],
                user_answer=q['user_answer'],
                correct_answer=q['correct_answer'],
                is_correct=q['is_correct'],
                correctness_score=q['correctness_score'],
                error_type=q['error_type'],
                error_description=q['error_description'],
                explanation=q['explanation'],
                improvement_suggestions=q['improvement_suggestions']
            )
            for q in correction_result.question_details
        ]
        
        return IntelligentCorrectionResult(
            homework_id=str(homework.id),
            success=True,
            message=f"智能批改完成，识别到{correction_result.total_questions}道题目",
            
            # OCR信息（从AI分析结果推断）
            ocr_confidence=0.85,  # 模拟值，实际应该从OCR结果获取
            extracted_text=f"识别到{correction_result.total_questions}道题目的完整内容",
            text_regions_count=correction_result.total_questions * 3,  # 估算
            
            # 批改结果
            subject=correction_result.subject,
            grade=request.grade,
            total_questions=correction_result.total_questions,
            correct_count=correction_result.correct_count,
            wrong_count=correction_result.wrong_count,
            accuracy_rate=correction_result.accuracy_rate,
            overall_score=correction_result.overall_score,
            
            # 详细结果
            question_details=question_details,
            
            # 分析报告
            performance_analysis=correction_result.performance_analysis,
            learning_suggestions=correction_result.learning_suggestions,
            time_spent_estimate=correction_result.time_spent_estimate,
            
            # 元数据
            analysis_time=datetime.now().isoformat(),
            ai_version="v1.0-advanced"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"智能批改异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"智能批改服务异常: {str(e)}"
        )


@router.get("/homework-analysis/{homework_id}", summary="获取作业分析详情")
async def get_homework_analysis_detail(
    homework_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取作业的详细AI分析结果
    """
    try:
        # 查询作业记录
        homework = db.query(Homework).filter(
            Homework.id == homework_id,
            Homework.user_id == current_user.id
        ).first()
        
        if not homework:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到指定的作业记录"
            )
        
        # 解析批改结果
        correction_results = []
        if homework.correction_results:
            try:
                correction_results = json.loads(homework.correction_results)
            except json.JSONDecodeError:
                print("批改结果JSON解析失败")
        
        # 重新生成AI分析（如果需要）
        enhanced_analysis = None
        if homework.image_url:
            try:
                analysis_ai = HomeworkAnalysisAI()
                enhanced_analysis = analysis_ai.analyze_homework_image(
                    image_path=homework.image_url,
                    subject=homework.subject,
                    grade="小学四年级",  # 默认年级，实际应从用户信息获取
                    student_id=str(current_user.id)
                )
            except Exception as e:
                print(f"重新分析失败: {e}")
        
        return {
            'homework_id': homework.id,
            'basic_info': {
                'title': homework.title,
                'subject': homework.subject,
                'created_at': homework.created_at.isoformat() if homework.created_at else None,
                'total_questions': homework.total_questions,
                'accuracy_rate': homework.accuracy_rate * 100 if homework.accuracy_rate else 0
            },
            'correction_results': correction_results,
            'enhanced_analysis': {
                'performance_analysis': enhanced_analysis.performance_analysis if enhanced_analysis else {},
                'learning_suggestions': enhanced_analysis.learning_suggestions if enhanced_analysis else [],
                'time_estimate': enhanced_analysis.time_spent_estimate if enhanced_analysis else 0
            } if enhanced_analysis else None,
            'ai_insights': _generate_ai_insights(homework, correction_results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取分析详情异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析详情失败: {str(e)}"
        )


@router.post("/batch-correct", summary="批量智能批改")
async def batch_intelligent_correction(
    image_files: List[UploadFile] = File(...),
    subject: str = "math",
    grade: str = "小学四年级",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量处理多张作业图片进行智能批改
    """
    try:
        if len(image_files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="一次最多只能上传10张图片"
            )
        
        # 创建上传目录
        upload_dir = "uploads/batch_homework"
        os.makedirs(upload_dir, exist_ok=True)
        
        batch_results = []
        analysis_ai = HomeworkAnalysisAI()
        
        for i, image_file in enumerate(image_files):
            try:
                # 保存上传的图片
                file_extension = os.path.splitext(image_file.filename)[1]
                unique_filename = f"batch_{uuid.uuid4()}{file_extension}"
                file_path = os.path.join(upload_dir, unique_filename)
                
                content = await image_file.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                
                # 执行智能分析
                correction_result = analysis_ai.analyze_homework_image(
                    image_path=file_path,
                    subject=subject,
                    grade=grade,
                    student_id=str(current_user.id)
                )
                
                # 保存到数据库
                homework = Homework(
                    user_id=current_user.id,
                    image_url=file_path,
                    subject=subject,
                    title=f"批量批改 {i+1}",
                    total_questions=correction_result.total_questions,
                    correct_count=correction_result.correct_count,
                    wrong_count=correction_result.wrong_count,
                    accuracy_rate=correction_result.accuracy_rate / 100,
                    overall_score=correction_result.overall_score,
                    status='completed'
                )
                
                db.add(homework)
                db.commit()
                db.refresh(homework)
                
                batch_results.append({
                    'homework_id': homework.id,
                    'filename': image_file.filename,
                    'status': 'success',
                    'total_questions': correction_result.total_questions,
                    'accuracy_rate': correction_result.accuracy_rate,
                    'correct_count': correction_result.correct_count
                })
                
            except Exception as e:
                print(f"批量处理第{i+1}张图片失败: {e}")
                batch_results.append({
                    'homework_id': None,
                    'filename': image_file.filename,
                    'status': 'failed',
                    'error': str(e)
                })
        
        success_count = sum(1 for r in batch_results if r['status'] == 'success')
        
        return {
            'success': True,
            'message': f"批量批改完成，成功处理{success_count}张图片",
            'total_processed': len(image_files),
            'success_count': success_count,
            'failed_count': len(image_files) - success_count,
            'results': batch_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"批量批改异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量批改失败: {str(e)}"
        )


def _generate_ai_insights(homework, correction_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成AI洞察分析"""
    
    if not correction_results:
        return {
            'insights': ['暂无详细分析数据'],
            'recommendations': ['建议重新分析作业内容'],
            'strengths': [],
            'improvements': []
        }
    
    # 分析错误模式
    error_types = {}
    knowledge_gaps = []
    correct_answers = 0
    
    for result in correction_results:
        if result.get('is_correct'):
            correct_answers += 1
        else:
            error_type = result.get('error_type', '未知错误')
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # 收集知识点缺陷
            for kp in result.get('knowledge_points', []):
                if kp not in knowledge_gaps:
                    knowledge_gaps.append(kp)
    
    accuracy = correct_answers / len(correction_results) if correction_results else 0
    
    # 生成洞察
    insights = []
    if accuracy >= 0.8:
        insights.append(f"🎉 整体表现优秀，正确率达到{accuracy*100:.1f}%")
    elif accuracy >= 0.6:
        insights.append(f"👍 基础掌握良好，正确率{accuracy*100:.1f}%，还有提升空间")
    else:
        insights.append(f"📚 需要加强基础练习，当前正确率{accuracy*100:.1f}%")
    
    if error_types:
        most_common_error = max(error_types, key=error_types.get)
        insights.append(f"⚠️ 主要错误类型：{most_common_error}")
    
    # 生成建议
    recommendations = []
    if 'calculation' in error_types:
        recommendations.append("加强基础运算练习")
    if 'comprehension' in error_types:
        recommendations.append("提高阅读理解能力")
    if knowledge_gaps:
        recommendations.append(f"重点复习：{', '.join(knowledge_gaps[:3])}")
    
    return {
        'insights': insights,
        'recommendations': recommendations,
        'strengths': ["认真完成作业", "书写工整"] if accuracy > 0.5 else [],
        'improvements': ["计算准确性", "答题规范性"] if accuracy < 0.8 else []
    }