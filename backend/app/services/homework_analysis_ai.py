"""
中小学作业智能分析AI模型
专门针对中小学各学科题目进行智能分析、批改和评价
"""
import re
import json
import math
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from app.services.vision_ocr_service import VisionOCRService


class SubjectType(Enum):
    MATH = "math"
    CHINESE = "chinese"
    ENGLISH = "english"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"


class GradeLevel(Enum):
    PRIMARY_1_3 = "primary_1_3"  # 小学1-3年级
    PRIMARY_4_6 = "primary_4_6"  # 小学4-6年级
    MIDDLE_1_2 = "middle_1_2"    # 初中1-2年级
    MIDDLE_3 = "middle_3"        # 初中3年级
    HIGH_1_2 = "high_1_2"       # 高中1-2年级
    HIGH_3 = "high_3"           # 高中3年级


@dataclass
class QuestionAnalysis:
    """题目分析结果"""
    question_number: int
    question_text: str
    question_type: str
    subject: str
    grade_level: str
    knowledge_points: List[str]
    difficulty_level: str
    expected_answer: str
    answer_format: str
    step_by_step_solution: List[str]
    common_mistakes: List[str]
    scoring_criteria: Dict[str, Any]


@dataclass
class AnswerEvaluation:
    """答案评估结果"""
    user_answer: str
    is_correct: bool
    correctness_score: float
    step_analysis: List[Dict[str, Any]]
    error_type: Optional[str]
    error_description: Optional[str]
    improvement_suggestions: List[str]
    partial_credit: Dict[str, float]


@dataclass
class HomeworkCorrectionResult:
    """作业批改结果"""
    homework_id: str
    student_id: str
    subject: str
    total_questions: int
    correct_count: int
    wrong_count: int
    accuracy_rate: float
    overall_score: float
    question_details: List[Dict[str, Any]]
    performance_analysis: Dict[str, Any]
    learning_suggestions: List[str]
    time_spent_estimate: int  # 估计用时（分钟）


class HomeworkAnalysisAI:
    """作业分析AI引擎"""
    
    def __init__(self):
        self.ocr_service = VisionOCRService()
        
        # 初始化各学科的分析器
        self.subject_analyzers = {
            SubjectType.MATH: MathAnalyzer(),
            SubjectType.CHINESE: ChineseAnalyzer(), 
            SubjectType.ENGLISH: EnglishAnalyzer(),
            SubjectType.PHYSICS: PhysicsAnalyzer(),
            SubjectType.CHEMISTRY: ChemistryAnalyzer()
        }
        
        # 年级难度映射
        self.grade_difficulty_map = {
            GradeLevel.PRIMARY_1_3: 1,
            GradeLevel.PRIMARY_4_6: 2,
            GradeLevel.MIDDLE_1_2: 3,
            GradeLevel.MIDDLE_3: 4,
            GradeLevel.HIGH_1_2: 5,
            GradeLevel.HIGH_3: 6
        }
    
    def analyze_homework_image(self, image_path: str, subject: str, 
                             grade: str, student_id: str) -> HomeworkCorrectionResult:
        """
        分析作业图片并生成批改结果
        
        Args:
            image_path: 作业图片路径
            subject: 学科
            grade: 年级
            student_id: 学生ID
            
        Returns:
            批改结果
        """
        try:
            print(f"开始分析作业图片: {image_path}")
            
            # 1. OCR文字提取
            ocr_result = self.ocr_service.extract_text_from_image(image_path)
            
            if not ocr_result['success']:
                return self._create_error_result(
                    f"图片文字识别失败: {ocr_result['message']}"
                )
            
            print(f"OCR提取成功，识别到{len(ocr_result['regions'])}个文字区域")
            
            # 2. 题目结构化解析
            questions = self._parse_questions_from_ocr(ocr_result)
            
            if not questions:
                return self._create_error_result("未能识别到有效的题目结构")
            
            print(f"识别到{len(questions)}道题目")
            
            # 3. 学科专项分析
            subject_enum = self._get_subject_enum(subject)
            grade_enum = self._get_grade_enum(grade)
            
            analyzer = self.subject_analyzers.get(subject_enum)
            if not analyzer:
                return self._create_error_result(f"暂不支持{subject}学科的智能分析")
            
            # 4. 逐题分析和批改
            question_results = []
            correct_count = 0
            total_score = 0
            
            for i, question_data in enumerate(questions):
                print(f"分析第{i+1}题...")
                
                # 题目分析
                question_analysis = analyzer.analyze_question(
                    question_data['question_text'], 
                    grade_enum
                )
                
                # 答案评估
                user_answer = question_data.get('user_answer', '')
                answer_evaluation = analyzer.evaluate_answer(
                    question_analysis, 
                    user_answer
                )
                
                # 合并结果
                question_result = {
                    'question_number': i + 1,
                    'question_text': question_analysis.question_text,
                    'question_type': question_analysis.question_type,
                    'knowledge_points': question_analysis.knowledge_points,
                    'difficulty_level': question_analysis.difficulty_level,
                    'user_answer': answer_evaluation.user_answer,
                    'correct_answer': question_analysis.expected_answer,
                    'is_correct': answer_evaluation.is_correct,
                    'correctness_score': answer_evaluation.correctness_score,
                    'error_type': answer_evaluation.error_type,
                    'error_description': answer_evaluation.error_description,
                    'step_by_step_solution': question_analysis.step_by_step_solution,
                    'improvement_suggestions': answer_evaluation.improvement_suggestions,
                    'explanation': self._generate_explanation(question_analysis, answer_evaluation)
                }
                
                question_results.append(question_result)
                
                if answer_evaluation.is_correct:
                    correct_count += 1
                
                total_score += answer_evaluation.correctness_score
            
            # 5. 整体分析和建议
            performance_analysis = self._analyze_overall_performance(
                question_results, subject, grade
            )
            
            learning_suggestions = self._generate_learning_suggestions(
                question_results, performance_analysis, subject
            )
            
            # 6. 构建最终结果
            total_questions = len(question_results)
            wrong_count = total_questions - correct_count
            accuracy_rate = (correct_count / total_questions * 100) if total_questions > 0 else 0
            overall_score = (total_score / total_questions * 100) if total_questions > 0 else 0
            
            return HomeworkCorrectionResult(
                homework_id=f"hw_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                student_id=student_id,
                subject=subject,
                total_questions=total_questions,
                correct_count=correct_count,
                wrong_count=wrong_count,
                accuracy_rate=round(accuracy_rate, 1),
                overall_score=round(overall_score, 1),
                question_details=question_results,
                performance_analysis=performance_analysis,
                learning_suggestions=learning_suggestions,
                time_spent_estimate=self._estimate_time_spent(question_results)
            )
            
        except Exception as e:
            print(f"作业分析失败: {e}")
            return self._create_error_result(f"作业分析失败: {str(e)}")
    
    def _parse_questions_from_ocr(self, ocr_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从OCR结果中解析题目结构"""
        structured_content = ocr_result.get('structured_content', {})
        questions_data = structured_content.get('questions', [])
        
        questions = []
        
        if questions_data:
            # 使用结构化解析的题目
            for q_data in questions_data:
                question_text_parts = []
                
                # 组合题目文本
                for part in q_data.get('content_parts', []):
                    question_text_parts.append(part['text'])
                
                # 添加公式
                for formula in q_data.get('formulas', []):
                    question_text_parts.append(formula['text'])
                
                question_text = ' '.join(question_text_parts)
                
                # 尝试从选择题选项中找答案
                user_answer = ''
                options = q_data.get('answer_options', [])
                if options:
                    question_text += ' ' + ' '.join([f"{opt['option']}. {opt['text']}" for opt in options])
                    # 简单的答案识别逻辑（实际应该更复杂）
                    user_answer = self._extract_user_choice(options)
                
                questions.append({
                    'question_number': q_data.get('number', len(questions) + 1),
                    'question_text': question_text.strip(),
                    'user_answer': user_answer,
                    'bbox': q_data.get('bbox')
                })
        else:
            # 使用简单的文本解析
            raw_text = ocr_result.get('raw_text', '')
            questions = self._parse_questions_from_text(raw_text)
        
        return questions
    
    def _parse_questions_from_text(self, text: str) -> List[Dict[str, Any]]:
        """从纯文本中解析题目（备用方法）"""
        questions = []
        
        # 按题号分割
        question_pattern = r'(\d+)[\.、)]\s*([^0-9]*?)(?=\d+[\.、)]|$)'
        matches = re.findall(question_pattern, text, re.DOTALL)
        
        for match in matches:
            question_number, question_content = match
            
            # 清理内容
            content = question_content.strip()
            if len(content) > 5:  # 过滤太短的内容
                questions.append({
                    'question_number': int(question_number),
                    'question_text': f"{question_number}. {content}",
                    'user_answer': self._extract_answer_from_content(content),
                    'bbox': None
                })
        
        return questions
    
    def _extract_user_choice(self, options: List[Dict[str, Any]]) -> str:
        """从选择题选项中提取用户答案（简化版）"""
        # 这里应该有更复杂的逻辑来识别用户的选择标记
        # 现在简单返回一个模拟答案
        if options:
            return options[0]['option']  # 简化：返回第一个选项
        return ''
    
    def _extract_answer_from_content(self, content: str) -> str:
        """从题目内容中提取用户答案（简化版）"""
        # 寻找等号后的答案
        if '=' in content:
            parts = content.split('=')
            if len(parts) > 1:
                answer = parts[-1].strip()
                # 提取数字答案
                number_match = re.search(r'\d+\.?\d*', answer)
                if number_match:
                    return number_match.group()
        
        return ''
    
    def _get_subject_enum(self, subject: str) -> SubjectType:
        """获取学科枚举"""
        subject_mapping = {
            'math': SubjectType.MATH,
            'chinese': SubjectType.CHINESE,
            'english': SubjectType.ENGLISH,
            'physics': SubjectType.PHYSICS,
            'chemistry': SubjectType.CHEMISTRY,
            'biology': SubjectType.BIOLOGY
        }
        return subject_mapping.get(subject.lower(), SubjectType.MATH)
    
    def _get_grade_enum(self, grade: str) -> GradeLevel:
        """获取年级枚举"""
        if '小学' in grade:
            if any(num in grade for num in ['1', '2', '3', '一', '二', '三']):
                return GradeLevel.PRIMARY_1_3
            else:
                return GradeLevel.PRIMARY_4_6
        elif '初中' in grade:
            if any(num in grade for num in ['3', '三']):
                return GradeLevel.MIDDLE_3
            else:
                return GradeLevel.MIDDLE_1_2
        elif '高中' in grade:
            if any(num in grade for num in ['3', '三']):
                return GradeLevel.HIGH_3
            else:
                return GradeLevel.HIGH_1_2
        else:
            return GradeLevel.PRIMARY_4_6  # 默认
    
    def _generate_explanation(self, question_analysis: QuestionAnalysis, 
                            answer_evaluation: AnswerEvaluation) -> str:
        """生成题目解析"""
        if answer_evaluation.is_correct:
            return f"答案正确！{question_analysis.step_by_step_solution[0] if question_analysis.step_by_step_solution else '解题思路正确。'}"
        else:
            error_desc = answer_evaluation.error_description or '答案有误'
            solution = question_analysis.step_by_step_solution[0] if question_analysis.step_by_step_solution else '请检查计算过程'
            return f"{error_desc}。正确解法：{solution}"
    
    def _analyze_overall_performance(self, question_results: List[Dict[str, Any]], 
                                   subject: str, grade: str) -> Dict[str, Any]:
        """分析整体表现"""
        if not question_results:
            return {}
        
        # 统计错误类型
        error_types = {}
        knowledge_point_errors = {}
        difficulty_performance = {}
        
        for q in question_results:
            if not q['is_correct'] and q['error_type']:
                error_types[q['error_type']] = error_types.get(q['error_type'], 0) + 1
            
            for kp in q['knowledge_points']:
                if kp not in knowledge_point_errors:
                    knowledge_point_errors[kp] = {'correct': 0, 'total': 0}
                
                knowledge_point_errors[kp]['total'] += 1
                if q['is_correct']:
                    knowledge_point_errors[kp]['correct'] += 1
            
            difficulty = q['difficulty_level']
            if difficulty not in difficulty_performance:
                difficulty_performance[difficulty] = {'correct': 0, 'total': 0}
            
            difficulty_performance[difficulty]['total'] += 1
            if q['is_correct']:
                difficulty_performance[difficulty]['correct'] += 1
        
        # 计算知识点掌握情况
        weak_knowledge_points = []
        for kp, stats in knowledge_point_errors.items():
            accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            if accuracy < 0.7:  # 正确率低于70%认为是薄弱点
                weak_knowledge_points.append({
                    'knowledge_point': kp,
                    'accuracy': round(accuracy * 100, 1),
                    'total_questions': stats['total']
                })
        
        return {
            'main_error_types': dict(sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:3]),
            'weak_knowledge_points': weak_knowledge_points[:5],
            'difficulty_performance': difficulty_performance,
            'overall_difficulty_match': self._assess_difficulty_match(difficulty_performance, grade)
        }
    
    def _assess_difficulty_match(self, difficulty_performance: Dict[str, Dict[str, int]], 
                               grade: str) -> str:
        """评估难度匹配度"""
        if not difficulty_performance:
            return 'unknown'
        
        # 简化的难度匹配评估
        easy_accuracy = 0
        medium_accuracy = 0
        hard_accuracy = 0
        
        if 'easy' in difficulty_performance:
            stats = difficulty_performance['easy']
            easy_accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        if 'medium' in difficulty_performance:
            stats = difficulty_performance['medium']
            medium_accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        if 'hard' in difficulty_performance:
            stats = difficulty_performance['hard']
            hard_accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        if easy_accuracy >= 0.8 and medium_accuracy >= 0.6:
            return 'appropriate'
        elif easy_accuracy < 0.6:
            return 'too_hard'
        elif easy_accuracy >= 0.9 and medium_accuracy >= 0.8:
            return 'too_easy'
        else:
            return 'suitable'
    
    def _generate_learning_suggestions(self, question_results: List[Dict[str, Any]], 
                                     performance_analysis: Dict[str, Any], 
                                     subject: str) -> List[str]:
        """生成学习建议"""
        suggestions = []
        
        # 基于错误类型的建议
        main_errors = performance_analysis.get('main_error_types', {})
        
        if 'calculation' in main_errors:
            suggestions.append("💪 建议加强基础计算练习，提高运算准确性")
        
        if 'comprehension' in main_errors:
            suggestions.append("📖 需要提高阅读理解能力，仔细审题")
        
        if 'method' in main_errors:
            suggestions.append("🧠 建议学习更多解题方法和技巧")
        
        if 'careless' in main_errors:
            suggestions.append("⚠️ 要养成检查答案的好习惯，减少粗心错误")
        
        # 基于薄弱知识点的建议
        weak_points = performance_analysis.get('weak_knowledge_points', [])
        if weak_points:
            top_weak = weak_points[0]['knowledge_point']
            suggestions.append(f"📚 重点复习{top_weak}相关知识点")
        
        # 基于整体表现的建议
        total_correct = sum(1 for q in question_results if q['is_correct'])
        accuracy_rate = total_correct / len(question_results) if question_results else 0
        
        if accuracy_rate >= 0.9:
            suggestions.append("🎉 表现优秀！可以尝试更有挑战性的题目")
        elif accuracy_rate >= 0.7:
            suggestions.append("👍 掌握不错，继续保持并巩固薄弱环节")
        elif accuracy_rate >= 0.5:
            suggestions.append("📝 建议多做基础题目，打牢基础")
        else:
            suggestions.append("🤝 建议寻求老师或同学的帮助，从基础开始复习")
        
        return suggestions[:5]  # 限制建议数量
    
    def _estimate_time_spent(self, question_results: List[Dict[str, Any]]) -> int:
        """估计完成时间（分钟）"""
        # 基于题目数量和难度的简单估计
        total_time = 0
        
        for question in question_results:
            difficulty = question.get('difficulty_level', 'medium')
            
            if difficulty == 'easy':
                total_time += 2
            elif difficulty == 'medium':
                total_time += 5
            elif difficulty == 'hard':
                total_time += 8
            else:
                total_time += 5
        
        return max(total_time, 10)  # 至少10分钟
    
    def _create_error_result(self, error_message: str) -> HomeworkCorrectionResult:
        """创建错误结果"""
        return HomeworkCorrectionResult(
            homework_id="error",
            student_id="",
            subject="unknown",
            total_questions=0,
            correct_count=0,
            wrong_count=0,
            accuracy_rate=0,
            overall_score=0,
            question_details=[],
            performance_analysis={'error': error_message},
            learning_suggestions=[f"⚠️ 分析失败: {error_message}"],
            time_spent_estimate=0
        )


class SubjectAnalyzer:
    """学科分析器基类"""
    
    def analyze_question(self, question_text: str, grade: GradeLevel) -> QuestionAnalysis:
        """分析题目"""
        raise NotImplementedError
    
    def evaluate_answer(self, question_analysis: QuestionAnalysis, 
                       user_answer: str) -> AnswerEvaluation:
        """评估答案"""
        raise NotImplementedError


class MathAnalyzer(SubjectAnalyzer):
    """数学分析器"""
    
    def analyze_question(self, question_text: str, grade: GradeLevel) -> QuestionAnalysis:
        """分析数学题目"""
        
        # 识别题目类型
        question_type = self._identify_math_type(question_text)
        
        # 提取知识点
        knowledge_points = self._extract_math_knowledge_points(question_text, question_type)
        
        # 评估难度
        difficulty = self._assess_math_difficulty(question_text, grade, question_type)
        
        # 生成预期答案
        expected_answer = self._calculate_math_answer(question_text, question_type)
        
        # 生成解题步骤
        solution_steps = self._generate_math_solution(question_text, question_type)
        
        return QuestionAnalysis(
            question_number=1,
            question_text=question_text,
            question_type=question_type,
            subject='math',
            grade_level=grade.value,
            knowledge_points=knowledge_points,
            difficulty_level=difficulty,
            expected_answer=expected_answer,
            answer_format='number',
            step_by_step_solution=solution_steps,
            common_mistakes=['计算错误', '公式记错', '理解偏差'],
            scoring_criteria={'accuracy': 0.8, 'method': 0.2}
        )
    
    def evaluate_answer(self, question_analysis: QuestionAnalysis, 
                       user_answer: str) -> AnswerEvaluation:
        """评估数学答案"""
        
        if not user_answer or not user_answer.strip():
            return AnswerEvaluation(
                user_answer=user_answer,
                is_correct=False,
                correctness_score=0.0,
                step_analysis=[],
                error_type='no_answer',
                error_description='未作答',
                improvement_suggestions=['请完成作答'],
                partial_credit={}
            )
        
        expected = question_analysis.expected_answer
        is_correct = self._compare_math_answers(user_answer, expected)
        
        score = 1.0 if is_correct else 0.0
        error_type = None
        error_description = None
        suggestions = []
        
        if not is_correct:
            error_type = self._analyze_math_error(user_answer, expected, question_analysis.question_type)
            error_description = self._get_math_error_description(error_type)
            suggestions = self._get_math_improvement_suggestions(error_type)
        
        return AnswerEvaluation(
            user_answer=user_answer,
            is_correct=is_correct,
            correctness_score=score,
            step_analysis=[],
            error_type=error_type,
            error_description=error_description,
            improvement_suggestions=suggestions,
            partial_credit={'calculation': score}
        )
    
    def _identify_math_type(self, question_text: str) -> str:
        """识别数学题目类型"""
        text = question_text.lower()
        
        if '×' in text or '乘' in text or 'multiply' in text:
            return 'multiplication'
        elif '÷' in text or '除' in text or 'divide' in text:
            return 'division'
        elif '+' in text or '加' in text or 'add' in text:
            return 'addition'
        elif '-' in text or '减' in text or 'subtract' in text:
            return 'subtraction'
        elif '面积' in text or '周长' in text:
            return 'geometry'
        elif '方程' in text or 'equation' in text:
            return 'equation'
        elif '应用题' in text or '买' in text or '速度' in text:
            return 'word_problem'
        else:
            return 'arithmetic'
    
    def _extract_math_knowledge_points(self, question_text: str, question_type: str) -> List[str]:
        """提取数学知识点"""
        knowledge_points = []
        
        if question_type == 'multiplication':
            knowledge_points.append('乘法运算')
        elif question_type == 'division':
            knowledge_points.append('除法运算')
        elif question_type == 'addition':
            knowledge_points.append('加法运算')
        elif question_type == 'subtraction':
            knowledge_points.append('减法运算')
        elif question_type == 'geometry':
            knowledge_points.extend(['几何图形', '面积计算'])
        elif question_type == 'equation':
            knowledge_points.extend(['方程求解', '代数运算'])
        elif question_type == 'word_problem':
            knowledge_points.extend(['应用题', '数量关系'])
        
        # 检查是否包含小数
        if '.' in question_text:
            knowledge_points.append('小数运算')
        
        # 检查是否包含分数
        if '/' in question_text or '分' in question_text:
            knowledge_points.append('分数运算')
        
        return knowledge_points
    
    def _assess_math_difficulty(self, question_text: str, grade: GradeLevel, question_type: str) -> str:
        """评估数学题目难度"""
        
        # 提取数字
        numbers = re.findall(r'\d+\.?\d*', question_text)
        
        if numbers:
            max_number = max(float(n) for n in numbers)
            
            if grade in [GradeLevel.PRIMARY_1_3]:
                if max_number <= 20:
                    return 'easy'
                elif max_number <= 100:
                    return 'medium'
                else:
                    return 'hard'
            elif grade in [GradeLevel.PRIMARY_4_6]:
                if max_number <= 100:
                    return 'easy'
                elif max_number <= 1000:
                    return 'medium'
                else:
                    return 'hard'
            else:
                if max_number <= 100:
                    return 'easy'
                elif max_number <= 10000:
                    return 'medium'
                else:
                    return 'hard'
        
        return 'medium'
    
    def _calculate_math_answer(self, question_text: str, question_type: str) -> str:
        """计算数学答案"""
        
        # 提取数字
        numbers = re.findall(r'\d+\.?\d*', question_text)
        
        if len(numbers) >= 2:
            try:
                num1 = float(numbers[0])
                num2 = float(numbers[1])
                
                if question_type == 'multiplication' or '×' in question_text:
                    result = num1 * num2
                elif question_type == 'division' or '÷' in question_text:
                    result = num1 / num2 if num2 != 0 else 0
                elif question_type == 'addition' or '+' in question_text:
                    result = num1 + num2
                elif question_type == 'subtraction' or '-' in question_text:
                    result = num1 - num2
                else:
                    result = num1 * num2  # 默认乘法
                
                # 格式化结果
                if result == int(result):
                    return str(int(result))
                else:
                    return str(round(result, 2))
                    
            except (ValueError, ZeroDivisionError):
                return "计算错误"
        
        return "无法计算"
    
    def _generate_math_solution(self, question_text: str, question_type: str) -> List[str]:
        """生成数学解题步骤"""
        
        numbers = re.findall(r'\d+\.?\d*', question_text)
        
        if len(numbers) >= 2:
            num1, num2 = numbers[0], numbers[1]
            
            if question_type == 'multiplication' or '×' in question_text:
                return [f"计算 {num1} × {num2} = {self._calculate_math_answer(question_text, question_type)}"]
            elif question_type == 'division' or '÷' in question_text:
                return [f"计算 {num1} ÷ {num2} = {self._calculate_math_answer(question_text, question_type)}"]
            elif question_type == 'addition' or '+' in question_text:
                return [f"计算 {num1} + {num2} = {self._calculate_math_answer(question_text, question_type)}"]
            elif question_type == 'subtraction' or '-' in question_text:
                return [f"计算 {num1} - {num2} = {self._calculate_math_answer(question_text, question_type)}"]
        
        return ["按照题目要求进行计算"]
    
    def _compare_math_answers(self, user_answer: str, expected_answer: str) -> bool:
        """比较数学答案"""
        try:
            user_num = float(re.findall(r'\d+\.?\d*', user_answer)[0]) if re.findall(r'\d+\.?\d*', user_answer) else None
            expected_num = float(re.findall(r'\d+\.?\d*', expected_answer)[0]) if re.findall(r'\d+\.?\d*', expected_answer) else None
            
            if user_num is not None and expected_num is not None:
                return abs(user_num - expected_num) < 0.001
        except (ValueError, IndexError):
            pass
        
        return user_answer.strip().lower() == expected_answer.strip().lower()
    
    def _analyze_math_error(self, user_answer: str, expected_answer: str, question_type: str) -> str:
        """分析数学错误类型"""
        
        try:
            user_num = float(re.findall(r'\d+\.?\d*', user_answer)[0]) if re.findall(r'\d+\.?\d*', user_answer) else 0
            expected_num = float(re.findall(r'\d+\.?\d*', expected_answer)[0]) if re.findall(r'\d+\.?\d*', expected_answer) else 0
            
            diff = abs(user_num - expected_num)
            
            if diff < 1:
                return 'minor_calculation'
            elif diff < expected_num * 0.1:
                return 'calculation'
            else:
                return 'method'
        except (ValueError, IndexError):
            return 'format'
    
    def _get_math_error_description(self, error_type: str) -> str:
        """获取数学错误描述"""
        descriptions = {
            'calculation': '计算过程有误',
            'minor_calculation': '计算结果略有偏差',
            'method': '解题方法或思路错误',
            'format': '答案格式不正确',
            'no_answer': '未作答'
        }
        return descriptions.get(error_type, '答案有误')
    
    def _get_math_improvement_suggestions(self, error_type: str) -> List[str]:
        """获取数学改进建议"""
        suggestions = {
            'calculation': ['仔细检查计算过程', '可以使用竖式计算', '验算确认结果'],
            'minor_calculation': ['注意计算细节', '放慢计算速度'],
            'method': ['重新理解题意', '复习相关知识点', '寻求老师帮助'],
            'format': ['注意答案格式要求', '包含必要的单位'],
            'no_answer': ['认真审题', '尝试解答', '不会的题目也要写出思考过程']
        }
        return suggestions.get(error_type, ['加强练习'])


class ChineseAnalyzer(SubjectAnalyzer):
    """语文分析器"""
    
    def analyze_question(self, question_text: str, grade: GradeLevel) -> QuestionAnalysis:
        """分析语文题目"""
        
        question_type = self._identify_chinese_type(question_text)
        knowledge_points = self._extract_chinese_knowledge_points(question_text, question_type)
        difficulty = self._assess_chinese_difficulty(question_text, grade)
        expected_answer = self._generate_chinese_answer(question_text, question_type)
        solution_steps = self._generate_chinese_solution(question_text, question_type)
        
        return QuestionAnalysis(
            question_number=1,
            question_text=question_text,
            question_type=question_type,
            subject='chinese',
            grade_level=grade.value,
            knowledge_points=knowledge_points,
            difficulty_level=difficulty,
            expected_answer=expected_answer,
            answer_format='text',
            step_by_step_solution=solution_steps,
            common_mistakes=['理解偏差', '词汇错误', '语法错误'],
            scoring_criteria={'accuracy': 0.6, 'comprehension': 0.4}
        )
    
    def evaluate_answer(self, question_analysis: QuestionAnalysis, 
                       user_answer: str) -> AnswerEvaluation:
        """评估语文答案"""
        
        if not user_answer or not user_answer.strip():
            return AnswerEvaluation(
                user_answer=user_answer,
                is_correct=False,
                correctness_score=0.0,
                step_analysis=[],
                error_type='no_answer',
                error_description='未作答',
                improvement_suggestions=['请完成作答'],
                partial_credit={}
            )
        
        expected = question_analysis.expected_answer
        is_correct = self._compare_chinese_answers(user_answer, expected, question_analysis.question_type)
        
        score = 1.0 if is_correct else 0.3  # 语文给部分分
        
        return AnswerEvaluation(
            user_answer=user_answer,
            is_correct=is_correct,
            correctness_score=score,
            step_analysis=[],
            error_type='content' if not is_correct else None,
            error_description='答案与标准答案不符' if not is_correct else None,
            improvement_suggestions=['加强阅读理解', '扩大词汇量'] if not is_correct else [],
            partial_credit={'content': score}
        )
    
    def _identify_chinese_type(self, question_text: str) -> str:
        """识别语文题目类型"""
        if '作者' in question_text or '写的' in question_text:
            return 'author_work'
        elif '古诗' in question_text or '诗' in question_text:
            return 'poetry'
        elif '词语' in question_text or '错别字' in question_text:
            return 'vocabulary'
        elif '阅读' in question_text or '文章' in question_text:
            return 'reading_comprehension'
        else:
            return 'general'
    
    def _extract_chinese_knowledge_points(self, question_text: str, question_type: str) -> List[str]:
        """提取语文知识点"""
        if question_type == 'author_work':
            return ['文学常识', '作者作品']
        elif question_type == 'poetry':
            return ['古诗文', '诗词鉴赏']
        elif question_type == 'vocabulary':
            return ['词汇理解', '语言文字运用']
        elif question_type == 'reading_comprehension':
            return ['阅读理解', '文章理解']
        else:
            return ['语文基础知识']
    
    def _assess_chinese_difficulty(self, question_text: str, grade: GradeLevel) -> str:
        """评估语文题目难度"""
        if len(question_text) < 20:
            return 'easy'
        elif len(question_text) < 50:
            return 'medium'
        else:
            return 'hard'
    
    def _generate_chinese_answer(self, question_text: str, question_type: str) -> str:
        """生成语文答案"""
        if question_type == 'author_work':
            return '参考答案：根据题目要求填写相应作者或作品'
        elif question_type == 'poetry':
            return '参考答案：根据诗词内容填写相应句子'
        else:
            return '参考答案：根据题目要求进行作答'
    
    def _generate_chinese_solution(self, question_text: str, question_type: str) -> List[str]:
        """生成语文解题步骤"""
        return ['仔细阅读题目', '理解题意要求', '根据所学知识作答']
    
    def _compare_chinese_answers(self, user_answer: str, expected_answer: str, question_type: str) -> bool:
        """比较语文答案"""
        # 简化的中文答案比较
        return len(user_answer.strip()) > 0  # 只要有内容就给分


class EnglishAnalyzer(SubjectAnalyzer):
    """英语分析器"""
    
    def analyze_question(self, question_text: str, grade: GradeLevel) -> QuestionAnalysis:
        """分析英语题目"""
        
        question_type = self._identify_english_type(question_text)
        knowledge_points = self._extract_english_knowledge_points(question_text, question_type)
        difficulty = self._assess_english_difficulty(question_text, grade)
        expected_answer = self._generate_english_answer(question_text, question_type)
        solution_steps = self._generate_english_solution(question_text, question_type)
        
        return QuestionAnalysis(
            question_number=1,
            question_text=question_text,
            question_type=question_type,
            subject='english',
            grade_level=grade.value,
            knowledge_points=knowledge_points,
            difficulty_level=difficulty,
            expected_answer=expected_answer,
            answer_format='text',
            step_by_step_solution=solution_steps,
            common_mistakes=['语法错误', '词汇错误', '拼写错误'],
            scoring_criteria={'accuracy': 0.7, 'grammar': 0.3}
        )
    
    def evaluate_answer(self, question_analysis: QuestionAnalysis, 
                       user_answer: str) -> AnswerEvaluation:
        """评估英语答案"""
        
        if not user_answer or not user_answer.strip():
            return AnswerEvaluation(
                user_answer=user_answer,
                is_correct=False,
                correctness_score=0.0,
                step_analysis=[],
                error_type='no_answer',
                error_description='未作答',
                improvement_suggestions=['请完成作答'],
                partial_credit={}
            )
        
        # 简化的英语答案评估
        is_correct = len(user_answer.strip()) > 0
        score = 0.8 if is_correct else 0.0
        
        return AnswerEvaluation(
            user_answer=user_answer,
            is_correct=is_correct,
            correctness_score=score,
            step_analysis=[],
            error_type=None,
            error_description=None,
            improvement_suggestions=['加强英语学习'] if not is_correct else [],
            partial_credit={'content': score}
        )
    
    def _identify_english_type(self, question_text: str) -> str:
        """识别英语题目类型"""
        if 'translate' in question_text.lower():
            return 'translation'
        elif 'choose' in question_text.lower():
            return 'choice'
        elif 'fill' in question_text.lower():
            return 'fill_blank'
        else:
            return 'general'
    
    def _extract_english_knowledge_points(self, question_text: str, question_type: str) -> List[str]:
        """提取英语知识点"""
        return ['英语基础', '词汇语法']
    
    def _assess_english_difficulty(self, question_text: str, grade: GradeLevel) -> str:
        """评估英语题目难度"""
        return 'medium'  # 简化处理
    
    def _generate_english_answer(self, question_text: str, question_type: str) -> str:
        """生成英语答案"""
        return 'Sample answer'
    
    def _generate_english_solution(self, question_text: str, question_type: str) -> List[str]:
        """生成英语解题步骤"""
        return ['Read the question carefully', 'Apply grammar rules', 'Check the answer']


class PhysicsAnalyzer(SubjectAnalyzer):
    """物理分析器"""
    
    def analyze_question(self, question_text: str, grade: GradeLevel) -> QuestionAnalysis:
        """分析物理题目"""
        
        return QuestionAnalysis(
            question_number=1,
            question_text=question_text,
            question_type='physics_problem',
            subject='physics',
            grade_level=grade.value,
            knowledge_points=['物理基础'],
            difficulty_level='medium',
            expected_answer='参考答案',
            answer_format='text',
            step_by_step_solution=['根据物理定律求解'],
            common_mistakes=['公式错误', '单位错误'],
            scoring_criteria={'accuracy': 0.8, 'method': 0.2}
        )
    
    def evaluate_answer(self, question_analysis: QuestionAnalysis, 
                       user_answer: str) -> AnswerEvaluation:
        """评估物理答案"""
        
        is_correct = len(user_answer.strip()) > 0 if user_answer else False
        
        return AnswerEvaluation(
            user_answer=user_answer or '',
            is_correct=is_correct,
            correctness_score=0.7 if is_correct else 0.0,
            step_analysis=[],
            error_type=None,
            error_description=None,
            improvement_suggestions=[],
            partial_credit={}
        )


class ChemistryAnalyzer(SubjectAnalyzer):
    """化学分析器"""
    
    def analyze_question(self, question_text: str, grade: GradeLevel) -> QuestionAnalysis:
        """分析化学题目"""
        
        return QuestionAnalysis(
            question_number=1,
            question_text=question_text,
            question_type='chemistry_problem',
            subject='chemistry',
            grade_level=grade.value,
            knowledge_points=['化学基础'],
            difficulty_level='medium',
            expected_answer='参考答案',
            answer_format='text',
            step_by_step_solution=['根据化学原理求解'],
            common_mistakes=['化学式错误', '计算错误'],
            scoring_criteria={'accuracy': 0.8, 'method': 0.2}
        )
    
    def evaluate_answer(self, question_analysis: QuestionAnalysis, 
                       user_answer: str) -> AnswerEvaluation:
        """评估化学答案"""
        
        is_correct = len(user_answer.strip()) > 0 if user_answer else False
        
        return AnswerEvaluation(
            user_answer=user_answer or '',
            is_correct=is_correct,
            correctness_score=0.7 if is_correct else 0.0,
            step_analysis=[],
            error_type=None,
            error_description=None,
            improvement_suggestions=[],
            partial_credit={}
        )