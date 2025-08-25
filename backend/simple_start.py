#!/usr/bin/env python3
"""
简化版启动脚本，用于快速演示
"""
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# 模拟FastAPI
class MockRequest:
    def __init__(self):
        self.method = "POST"
        self.url = "/api/v1/homework/correct"

# 模拟数学批改服务
class SimpleMathService:
    """简化版数学批改服务"""
    
    def correct_arithmetic(self, ocr_text: str) -> Dict[str, Any]:
        """批改小学口算题"""
        print(f"正在处理OCR文本: {ocr_text}")
        
        # 解析算式
        questions = self._parse_arithmetic_questions(ocr_text)
        print(f"识别到 {len(questions)} 道题目")
        
        if not questions:
            return {
                "error": "未识别到有效的算式题目",
                "total_questions": 0,
                "correct_count": 0,
                "wrong_count": 0,
                "accuracy_rate": 0,
                "results": []
            }
        
        # 批改每道题
        results = []
        for i, question in enumerate(questions):
            result = self._correct_single_question(question, i + 1)
            results.append(result)
            
            status = "[正确]" if result["is_correct"] else "[错误]"
            print(f"{status} 题目 {i+1}: {result['question']} | 你的答案: {result['user_answer']} | 正确答案: {result['correct_answer']}")
        
        # 统计结果
        total_questions = len(questions)
        correct_count = sum(1 for r in results if r["is_correct"])
        wrong_count = total_questions - correct_count
        accuracy_rate = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        print(f"\n批改结果:")
        print(f"   总题数: {total_questions}")
        print(f"   正确: {correct_count}")
        print(f"   错误: {wrong_count}")
        print(f"   准确率: {accuracy_rate:.1f}%")
        
        suggestions = self._generate_suggestions(results, accuracy_rate)
        if suggestions:
            print(f"\n学习建议:")
            for suggestion in suggestions:
                print(f"   {suggestion}")
        
        return {
            "total_questions": total_questions,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "accuracy_rate": round(accuracy_rate, 2),
            "results": results,
            "suggestions": suggestions
        }
    
    def _parse_arithmetic_questions(self, text: str) -> List[Dict[str, Any]]:
        """解析算术题目"""
        import re
        
        questions = []
        
        # 清理常见OCR错误
        text = text.replace('O', '0').replace('o', '0').replace('l', '1').replace('I', '1')
        text = text.replace('×', '*').replace('÷', '/').replace('－', '-').replace('＋', '+').replace('＝', '=')
        
        # 匹配算式
        patterns = [
            r'(\d+)\s*([+\-*/])\s*(\d+)\s*=\s*(\d+)',
            r'\(?\s*(\d+)\s*([+\-*/])\s*(\d+)\s*\)?\s*=\s*(\d+)',
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
            return num1 // num2
        else:
            raise ValueError(f"不支持的运算符: {operator}")
    
    def _analyze_error(self, num1: int, operator: str, num2: int, user_answer: Optional[int], correct_answer: int) -> Dict[str, str]:
        """分析错误类型"""
        if user_answer is None:
            return {
                "error_type": "格式错误",
                "error_reason": "答案格式不正确",
                "explanation": "请确保答案是纯数字格式"
            }
        
        error_analysis = {
            "error_type": "计算错误",
            "error_reason": "计算结果不正确",
            "explanation": f"正确计算: {num1} {operator} {num2} = {correct_answer}"
        }
        
        # 详细错误分析
        if operator == '+':
            if abs(user_answer - correct_answer) == 1:
                error_analysis["error_type"] = "粗心错误"
                error_analysis["error_reason"] = "计算结果差1，可能是粗心"
        elif operator == '-':
            if user_answer == num2 - num1:
                error_analysis["error_type"] = "顺序错误"
                error_analysis["error_reason"] = "减法顺序搞错了"
        
        return error_analysis
    
    def _generate_suggestions(self, results: List[Dict[str, Any]], accuracy_rate: float) -> List[str]:
        """生成学习建议"""
        suggestions = []
        
        if accuracy_rate == 100:
            suggestions.append("全部正确！继续保持，可以尝试更难的题目")
            return suggestions
        
        error_types = {}
        for result in results:
            if not result["is_correct"]:
                error_type = result.get("error_type", "计算错误")
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        if "粗心错误" in error_types:
            suggestions.append("注意细心计算，避免粗心出错")
        if "顺序错误" in error_types:
            suggestions.append("注意减法运算顺序，大数在前")
        
        if accuracy_rate < 60:
            suggestions.append("准确率较低，建议放慢速度仔细计算")
        elif accuracy_rate < 80:
            suggestions.append("有一定基础，继续练习可以提高")
        else:
            suggestions.append("准确率不错，再仔细一点就能满分")
        
        return suggestions

def demo_math_correction():
    """演示数学批改功能"""
    print("中小学智能批改平台 - 数学批改服务演示")
    print("=" * 60)
    
    service = SimpleMathService()
    
    # 测试数据
    test_cases = [
        "12 + 8 = 20\n15 - 7 = 8\n6 * 4 = 24\n18 / 3 = 6",
        "25 + 17 = 42\n30 - 12 = 18\n7 * 8 = 54\n36 / 6 = 6",
        "13 + 9 = 23\n20 - 8 = 12\n5 * 6 = 30\n24 / 4 = 6"  # 故意有错误
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"OCR识别文本:")
        for line in test_data.split('\n'):
            print(f"   {line}")
        print()
        
        result = service.correct_arithmetic(test_data)
        print()
        print("-" * 60)

def interactive_demo():
    """交互式演示"""
    import sys
    
    # 检查是否在交互式环境中运行
    if not sys.stdin.isatty():
        print("\n跳过交互式演示（非交互式环境）")
        return
        
    print("\n交互式批改演示")
    print("请输入算术题目，格式如: 12 + 8 = 20")
    print("多道题目请用换行分隔，输入 'quit' 退出\n")
    
    service = SimpleMathService()
    
    while True:
        try:
            user_input = input("请输入题目: ").strip()
            if user_input.lower() == 'quit':
                print("再见！")
                break
            
            if not user_input:
                continue
            
            print("\n" + "="*40)
            result = service.correct_arithmetic(user_input)
            print("="*40)
            
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except EOFError:
            print("\n检测到非交互式环境，退出演示")
            break
        except Exception as e:
            print(f"处理错误: {e}")

def main():
    """主函数"""
    print("中小学智能批改平台后端服务")
    print("FastAPI + PostgreSQL + Redis")
    print("版本: v1.0.0 (演示版)")
    print("=" * 60)
    
    print("\n功能特性:")
    print("- 小学数学口算批改")
    print("- 错误类型分析")  
    print("- 个性化学习建议")
    print("- 用户权限管理")
    print("- VIP额度管理")
    print("- API限流和日志")
    
    print("\n技术架构:")
    print("- Web框架: FastAPI")
    print("- 数据库: PostgreSQL")
    print("- 缓存: Redis")
    print("- 认证: JWT + 微信登录")
    print("- 部署: Docker + Docker Compose")
    
    # 运行演示
    demo_math_correction()
    
    # 交互式演示
    interactive_demo()

if __name__ == "__main__":
    main()