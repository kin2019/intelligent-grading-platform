import re
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.homework import Homework, ErrorQuestion
from app.models.user import User
from app.services.user_service import UserService
import json

class MathService:
    """数学批改服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)
    
    async def correct_arithmetic(
        self,
        user_id: int,
        image_url: str,
        ocr_text: str,
        grade_level: str = "elementary"
    ) -> Dict[str, Any]:
        """批改小学口算题"""
        start_time = time.time()
        
        # 检查用户权限和额度
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 消费用户额度
        await self.user_service.consume_quota(user_id)
        
        # 创建作业记录
        homework = Homework(
            user_id=user_id,
            original_image_url=image_url,
            subject="math",
            subject_type="arithmetic",
            grade_level=grade_level,
            ocr_text=ocr_text,
            status="processing"
        )
        
        self.db.add(homework)
        await self.db.commit()
        await self.db.refresh(homework)
        
        try:
            # OCR预处理
            ocr_start_time = time.time()
            processed_text = self._preprocess_ocr_text(ocr_text)
            ocr_time = time.time() - ocr_start_time
            
            # 解析算式
            correction_start_time = time.time()
            questions = self._parse_arithmetic_questions(processed_text)
            
            if not questions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="未识别到有效的算式题目"
                )
            
            # 批改每道题
            correction_results = []
            error_questions = []
            
            for i, question in enumerate(questions):
                result = self._correct_single_question(question, i + 1)
                correction_results.append(result)
                
                if not result["is_correct"]:
                    error_question = ErrorQuestion(
                        homework_id=homework.id,
                        user_id=user_id,
                        question_text=result["question"],
                        user_answer=result["user_answer"],
                        correct_answer=result["correct_answer"],
                        error_type=result.get("error_type", "计算错误"),
                        error_reason=result.get("error_reason", "计算结果不正确"),
                        explanation=result.get("explanation", ""),
                        difficulty_level=self._get_question_difficulty(question)
                    )
                    error_questions.append(error_question)
            
            correction_time = time.time() - correction_start_time
            
            # 计算统计信息
            total_questions = len(questions)
            correct_count = sum(1 for r in correction_results if r["is_correct"])
            wrong_count = total_questions - correct_count
            accuracy_rate = (correct_count / total_questions) * 100 if total_questions > 0 else 0
            
            # 保存错题记录
            if error_questions:
                self.db.add_all(error_questions)
            
            # 更新作业记录
            processing_time = time.time() - start_time
            
            homework.correction_result = json.dumps(correction_results, ensure_ascii=False)
            homework.total_questions = total_questions
            homework.correct_count = correct_count
            homework.wrong_count = wrong_count
            homework.accuracy_rate = accuracy_rate
            homework.status = "completed"
            homework.processing_time = processing_time
            homework.ocr_time = ocr_time
            homework.correction_time = correction_time
            homework.completed_at = datetime.utcnow()
            
            await self.db.commit()
            
            return {
                "homework_id": homework.id,
                "total_questions": total_questions,
                "correct_count": correct_count,
                "wrong_count": wrong_count,
                "accuracy_rate": round(accuracy_rate, 2),
                "processing_time": round(processing_time, 3),
                "results": correction_results,
                "error_count": len(error_questions),
                "suggestions": self._generate_suggestions(correction_results, accuracy_rate)
            }
            
        except Exception as e:
            # 更新作业状态为失败
            homework.status = "failed"
            homework.error_message = str(e)
            await self.db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"批改处理失败: {str(e)}"
            )
    
    def _preprocess_ocr_text(self, text: str) -> str:
        """预处理OCR识别文本"""
        if not text:
            return ""
        
        # 清理常见OCR错误
        replacements = {
            'O': '0',  # 字母O替换为数字0
            'o': '0',  # 小写字母o替换为数字0
            'l': '1',  # 小写字母l替换为数字1
            'I': '1',  # 大写字母I替换为数字1
            '×': '*',  # 乘号标准化
            '÷': '/',  # 除号标准化
            '－': '-', # 中文横线替换为减号
            '＋': '+', # 全角加号替换为半角
            '＝': '=', # 全角等号替换为半角
        }
        
        processed_text = text
        for old, new in replacements.items():
            processed_text = processed_text.replace(old, new)
        
        return processed_text
    
    def _parse_arithmetic_questions(self, text: str) -> List[Dict[str, Any]]:
        """解析算术题目"""
        questions = []
        
        # 匹配算式的正则表达式
        patterns = [
            # 标准格式: 12 + 34 = 46
            r'(\d+)\s*([+\-*/])\s*(\d+)\s*=\s*(\d+)',
            # 有括号的格式: (12 + 34) = 46
            r'\(?\s*(\d+)\s*([+\-*/])\s*(\d+)\s*\)?\s*=\s*(\d+)',
            # 缺少等号的格式: 12 + 34  46
            r'(\d+)\s*([+\-*/])\s*(\d+)\s+(\d+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 4:
                    num1, operator, num2, user_answer = match
                    questions.append({
                        'num1': int(num1),
                        'operator': operator,
                        'num2': int(num2),
                        'user_answer': user_answer,
                        'original_text': f"{num1} {operator} {num2} = {user_answer}"
                    })
        
        return questions
    
    def _correct_single_question(self, question: Dict[str, Any], question_number: int) -> Dict[str, Any]:
        """批改单个题目"""
        num1 = question['num1']
        num2 = question['num2']
        operator = question['operator']
        user_answer = question['user_answer']
        
        # 计算正确答案
        correct_answer = self._calculate_answer(num1, operator, num2)
        
        # 检查答案是否正确
        try:
            user_answer_int = int(user_answer)
            is_correct = user_answer_int == correct_answer
        except ValueError:
            is_correct = False
            user_answer_int = None
        
        result = {
            "question_number": question_number,
            "question": question['original_text'],
            "user_answer": user_answer,
            "correct_answer": str(correct_answer),
            "is_correct": is_correct,
            "operation": f"{num1} {operator} {num2}"
        }
        
        if not is_correct:
            result.update(self._analyze_error(num1, operator, num2, user_answer_int, correct_answer))
        
        return result
    
    def _calculate_answer(self, num1: int, operator: str, num2: int) -> int:
        """计算正确答案"""
        if operator == '+':
            return num1 + num2
        elif operator == '-':
            return num1 - num2
        elif operator == '*':
            return num1 * num2
        elif operator == '/':
            if num2 == 0:
                raise ValueError("除数不能为0")
            return num1 // num2  # 整数除法
        else:
            raise ValueError(f"不支持的运算符: {operator}")
    
    def _analyze_error(self, num1: int, operator: str, num2: int, user_answer: Optional[int], correct_answer: int) -> Dict[str, str]:
        """分析错误类型"""
        if user_answer is None:
            return {
                "error_type": "格式错误",
                "error_reason": "答案格式不正确，无法识别为数字",
                "explanation": "请确保答案是纯数字格式"
            }
        
        error_analysis = {
            "error_type": "计算错误",
            "error_reason": "计算结果不正确",
            "explanation": f"正确的计算过程是：{num1} {operator} {num2} = {correct_answer}"
        }
        
        # 详细错误分析
        if operator == '+':
            if abs(user_answer - correct_answer) == 1:
                error_analysis["error_type"] = "粗心错误"
                error_analysis["error_reason"] = "计算结果差1，可能是粗心所致"
            elif user_answer == num1 + num2 - 10 or user_answer == num1 + num2 + 10:
                error_analysis["error_type"] = "进位错误"
                error_analysis["error_reason"] = "加法进位计算错误"
        
        elif operator == '-':
            if user_answer == num2 - num1:
                error_analysis["error_type"] = "顺序错误" 
                error_analysis["error_reason"] = "减法顺序搞错，应该是大数减小数"
            elif abs(user_answer - correct_answer) == 1:
                error_analysis["error_type"] = "粗心错误"
                error_analysis["error_reason"] = "计算结果差1，可能是粗心所致"
        
        elif operator == '*':
            # 检查是否是乘法口诀错误
            if user_answer in [num1 * (num2 + 1), num1 * (num2 - 1)]:
                error_analysis["error_type"] = "乘法表错误"
                error_analysis["error_reason"] = "乘法口诀记忆错误"
        
        return error_analysis
    
    def _get_question_difficulty(self, question: Dict[str, Any]) -> int:
        """评估题目难度等级(1-10)"""
        num1, num2 = question['num1'], question['num2']
        operator = question['operator']
        
        # 基础难度
        difficulty = 1
        
        # 根据数字大小调整难度
        max_num = max(num1, num2)
        if max_num <= 10:
            difficulty += 0
        elif max_num <= 20:
            difficulty += 1
        elif max_num <= 100:
            difficulty += 2
        else:
            difficulty += 3
        
        # 根据运算类型调整难度
        if operator == '+':
            if num1 + num2 > 20:
                difficulty += 1  # 需要进位
        elif operator == '-':
            if num1 < num2:
                difficulty += 2  # 涉及负数
            elif num1 % 10 < num2 % 10:
                difficulty += 1  # 需要借位
        elif operator == '*':
            difficulty += 2  # 乘法比加减法难
            if max_num > 10:
                difficulty += 1
        elif operator == '/':
            difficulty += 3  # 除法最难
            if num1 % num2 != 0:
                difficulty += 1  # 有余数
        
        return min(10, max(1, difficulty))
    
    def _generate_suggestions(self, results: List[Dict[str, Any]], accuracy_rate: float) -> List[str]:
        """生成学习建议"""
        suggestions = []
        
        if accuracy_rate == 100:
            suggestions.append("🎉 全部正确！继续保持，可以尝试更难的题目")
            return suggestions
        
        # 分析错误类型
        error_types = {}
        for result in results:
            if not result["is_correct"]:
                error_type = result.get("error_type", "计算错误")
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        if "进位错误" in error_types:
            suggestions.append("📝 需要加强加法进位练习，建议多练习两位数加法")
        
        if "借位错误" in error_types:
            suggestions.append("📝 需要加强减法借位练习，建议多练习退位减法")
        
        if "乘法表错误" in error_types:
            suggestions.append("📝 需要熟记乘法口诀表，建议每天背诵")
        
        if "顺序错误" in error_types:
            suggestions.append("⚠️ 注意减法运算顺序，大数在前，小数在后")
        
        if accuracy_rate < 60:
            suggestions.append("💪 准确率较低，建议放慢速度，仔细计算每一步")
        elif accuracy_rate < 80:
            suggestions.append("👍 有一定基础，继续练习可以提高准确率")
        else:
            suggestions.append("✨ 准确率不错，再仔细一点就能达到满分")
        
        return suggestions