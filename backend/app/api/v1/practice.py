"""
练习题生成API
提供AI驱动的相似练习题生成服务
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.homework import ErrorQuestion
from app.services.ai_exercise_generator import AIExerciseGenerator, GeneratedExercise

router = APIRouter()


class ExerciseGenerationRequest(BaseModel):
    """练习题生成请求"""
    original_question: Dict[str, Any] = Field(..., description="原始错题信息")
    question_count: int = Field(default=5, ge=1, le=50, description="生成题目数量")
    difficulty_level: str = Field(default="same", description="难度级别：easier, same, harder, mixed")
    question_type: str = Field(default="similar", description="题目类型：similar, extended, comprehensive")
    include_answers: bool = Field(default=True, description="是否包含答案")
    include_analysis: bool = Field(default=True, description="是否包含解题分析")


class ExerciseResponse(BaseModel):
    """练习题响应"""
    number: int
    subject: str
    question_text: str
    correct_answer: str
    analysis: str
    difficulty: str
    knowledge_points: List[str]
    question_type: str


class GenerationResult(BaseModel):
    """生成结果"""
    success: bool
    message: str
    questions: List[ExerciseResponse]
    total_count: int
    generation_config: Dict[str, Any]
    student_profile: Optional[Dict[str, Any]] = None


@router.post("/generate", response_model=GenerationResult)
async def generate_similar_exercises(
    request: ExerciseGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成相似练习题
    
    基于学生的错题记录，使用AI算法生成个性化的相似练习题，
    帮助学生针对性地练习和巩固薄弱知识点。
    """
    try:
        # 验证用户权限
        if current_user.role not in ['student', 'parent']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生或家长可以生成练习题"
            )
        
        # 获取目标用户ID（家长查看孩子时使用child_id，学生查看自己时使用自己的ID）
        target_user_id = current_user.id
        
        # 如果是家长角色，需要验证是否有权限查看指定孩子的错题
        if current_user.role == 'parent':
            # 可以添加家长-孩子关系验证逻辑
            pass
        
        # 验证原始错题信息
        original_question = request.original_question
        if not original_question.get('id'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少原始错题ID"
            )
        
        # 验证错题是否存在且属于目标用户
        error_question = db.query(ErrorQuestion).filter(
            ErrorQuestion.id == original_question['id'],
            ErrorQuestion.user_id == target_user_id
        ).first()
        
        if not error_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到指定的错题记录"
            )
        
        # 补充错题信息
        enhanced_question = {
            'id': error_question.id,
            'user_id': error_question.user_id,
            'subject': error_question.subject,
            'question_text': error_question.question_text,
            'user_answer': error_question.user_answer,
            'correct_answer': error_question.correct_answer,
            'error_type': error_question.error_type,
            'knowledge_points': error_question.knowledge_points or [],
            'created_at': error_question.created_at.isoformat() if error_question.created_at else None
        }
        
        # 准备生成配置
        generation_config = {
            'question_count': request.question_count,
            'difficulty_level': request.difficulty_level,
            'question_type': request.question_type,
            'include_answers': request.include_answers,
            'include_analysis': request.include_analysis
        }
        
        # 创建AI练习题生成器
        exercise_generator = AIExerciseGenerator(db)
        
        # 生成练习题
        generated_exercises = exercise_generator.generate_exercises(
            enhanced_question, generation_config
        )
        
        # 转换为响应格式
        exercise_responses = []
        for exercise in generated_exercises:
            exercise_response = ExerciseResponse(
                number=exercise.number,
                subject=exercise.subject,
                question_text=exercise.question_text,
                correct_answer=exercise.correct_answer,
                analysis=exercise.analysis,
                difficulty=exercise.difficulty,
                knowledge_points=exercise.knowledge_points,
                question_type=exercise.question_type
            )
            exercise_responses.append(exercise_response)
        
        # 获取学生画像信息（可选）
        student_profile = exercise_generator._get_student_profile(target_user_id)
        
        return GenerationResult(
            success=True,
            message=f"成功生成{len(exercise_responses)}道练习题",
            questions=exercise_responses,
            total_count=len(exercise_responses),
            generation_config=generation_config,
            student_profile=student_profile
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"练习题生成失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"练习题生成失败: {str(e)}"
        )


@router.get("/templates/{subject}")
async def get_exercise_templates(
    subject: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定学科的练习题模板
    
    返回预定义的练习题模板，用于生成练习题时的参考
    """
    try:
        # 验证用户权限
        if current_user.role not in ['student', 'parent', 'teacher']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        # 根据学科返回相应的模板
        templates = {
            '数学': [
                {
                    'type': 'calculation',
                    'name': '四则运算',
                    'description': '基础计算题，包含加减乘除运算',
                    'difficulty_levels': ['易', '中', '难'],
                    'example': '计算：125 × 8 = ?'
                },
                {
                    'type': 'equation',
                    'name': '方程求解',
                    'description': '一元一次方程、二元一次方程组等',
                    'difficulty_levels': ['易', '中', '难'],
                    'example': '解方程：2x + 5 = 17'
                },
                {
                    'type': 'geometry',
                    'name': '几何题',
                    'description': '图形面积、周长、体积计算',
                    'difficulty_levels': ['易', '中', '难'],
                    'example': '求边长为5cm的正方形面积'
                }
            ],
            '语文': [
                {
                    'type': 'author_work',
                    'name': '作者作品',
                    'description': '古诗文作者与作品对应关系',
                    'difficulty_levels': ['易', '中', '难'],
                    'example': '《静夜思》的作者是谁？'
                },
                {
                    'type': 'poetry',
                    'name': '诗词填空',
                    'description': '古诗词名句填空与默写',
                    'difficulty_levels': ['易', '中', '难'],
                    'example': '床前明月光，_______'
                },
                {
                    'type': 'grammar',
                    'name': '语法题',
                    'description': '词汇辨析、句式分析、标点符号',
                    'difficulty_levels': ['易', '中', '难'],
                    'example': '选择没有错别字的词组'
                }
            ],
            '英语': [
                {
                    'type': 'grammar',
                    'name': '语法选择',
                    'description': '时态、语态、词性变化等语法题',
                    'difficulty_levels': ['易', '中', '难'],
                    'example': 'I _____ to school every day.'
                },
                {
                    'type': 'vocabulary',
                    'name': '词汇题',
                    'description': '单词释义、同义词、反义词',
                    'difficulty_levels': ['易', '中', '难'],
                    'example': 'What does "happy" mean?'
                },
                {
                    'type': 'translation',
                    'name': '翻译题',
                    'description': '英汉互译，句子翻译',
                    'difficulty_levels': ['易', '中', '难'],
                    'example': 'Translate: I like music.'
                }
            ]
        }
        
        subject_templates = templates.get(subject, [])
        
        if not subject_templates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"暂不支持{subject}学科的模板"
            )
        
        return {
            'subject': subject,
            'templates': subject_templates,
            'total_count': len(subject_templates)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取模板失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模板失败: {str(e)}"
        )


@router.post("/batch-generate")
async def batch_generate_exercises(
    error_ids: List[int],
    generation_config: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量生成练习题
    
    基于多道错题批量生成练习题集
    """
    try:
        # 验证用户权限
        if current_user.role not in ['student', 'parent']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        # 限制批量数量
        if len(error_ids) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="一次最多只能选择20道错题进行批量生成"
            )
        
        target_user_id = current_user.id
        
        # 获取错题记录
        error_questions = db.query(ErrorQuestion).filter(
            ErrorQuestion.id.in_(error_ids),
            ErrorQuestion.user_id == target_user_id
        ).all()
        
        if len(error_questions) != len(error_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部分错题记录不存在或无权限访问"
            )
        
        # 创建生成器
        exercise_generator = AIExerciseGenerator(db)
        
        all_exercises = []
        generation_summary = {
            'total_errors': len(error_questions),
            'total_exercises': 0,
            'by_subject': {},
            'by_difficulty': {}
        }
        
        # 逐个错题生成练习
        for error_question in error_questions:
            enhanced_question = {
                'id': error_question.id,
                'user_id': error_question.user_id,
                'subject': error_question.subject,
                'question_text': error_question.question_text,
                'user_answer': error_question.user_answer,
                'correct_answer': error_question.correct_answer,
                'error_type': error_question.error_type,
                'knowledge_points': error_question.knowledge_points or [],
                'created_at': error_question.created_at.isoformat() if error_question.created_at else None
            }
            
            # 为每个错题生成少量练习（避免总数过多）
            config = generation_config.copy()
            config['question_count'] = min(config.get('question_count', 3), 5)
            
            exercises = exercise_generator.generate_exercises(enhanced_question, config)
            
            # 统计信息
            subject = error_question.subject
            generation_summary['by_subject'][subject] = generation_summary['by_subject'].get(subject, 0) + len(exercises)
            
            for exercise in exercises:
                generation_summary['by_difficulty'][exercise.difficulty] = generation_summary['by_difficulty'].get(exercise.difficulty, 0) + 1
            
            all_exercises.extend(exercises)
        
        generation_summary['total_exercises'] = len(all_exercises)
        
        # 重新编号
        for i, exercise in enumerate(all_exercises):
            exercise.number = i + 1
        
        # 转换响应格式
        exercise_responses = [
            ExerciseResponse(
                number=exercise.number,
                subject=exercise.subject,
                question_text=exercise.question_text,
                correct_answer=exercise.correct_answer,
                analysis=exercise.analysis,
                difficulty=exercise.difficulty,
                knowledge_points=exercise.knowledge_points,
                question_type=exercise.question_type
            )
            for exercise in all_exercises
        ]
        
        return {
            'success': True,
            'message': f"批量生成完成，共{len(exercise_responses)}道练习题",
            'questions': exercise_responses,
            'summary': generation_summary,
            'generation_config': generation_config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"批量生成失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量生成失败: {str(e)}"
        )


@router.get("/difficulty-guide")
async def get_difficulty_guide(
    current_user: User = Depends(get_current_user)
):
    """获取难度级别说明"""
    
    return {
        'difficulty_levels': {
            'easier': {
                'name': '简化版',
                'description': '比原题简单，适合基础薄弱的学生',
                'coefficient': 0.7,
                'features': ['数字更小', '步骤更少', '概念更基础']
            },
            'same': {
                'name': '相同难度',
                'description': '与原题难度相当，巩固练习',
                'coefficient': 1.0,
                'features': ['难度相等', '题型相似', '知识点一致']
            },
            'harder': {
                'name': '提高版',
                'description': '比原题困难，适合能力较强的学生',
                'coefficient': 1.3,
                'features': ['数字更大', '步骤更多', '综合性更强']
            },
            'mixed': {
                'name': '混合难度',
                'description': '包含不同难度级别，循序渐进',
                'coefficient': 'variable',
                'features': ['难度递进', '全面训练', '适应性强']
            }
        },
        'question_types': {
            'similar': {
                'name': '相似题目',
                'description': '与原题结构相似，题型一致',
                'weight': 0.5
            },
            'extended': {
                'name': '拓展变式',
                'description': '在原题基础上扩展，增加变化',
                'weight': 0.3
            },
            'comprehensive': {
                'name': '综合应用',
                'description': '结合多个知识点，提高综合能力',
                'weight': 0.2
            }
        }
    }