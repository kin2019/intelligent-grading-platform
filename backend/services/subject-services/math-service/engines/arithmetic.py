"""
四则运算批改引擎
"""
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal, InvalidOperation
import sympy as sp
from sympy import sympify, simplify
import structlog

logger = structlog.get_logger(__name__)


class ArithmeticEngine:
    """四则运算批改引擎"""
    
    def __init__(self):
        self.operation_patterns = {
            'addition': r'(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)',
            'subtraction': r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)',
            'multiplication': r'(\d+(?:\.\d+)?)\s*[×*]\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)',
            'division': r'(\d+(?:\.\d+)?)\s*[÷/]\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)',
            'mixed': r'(.+?)\s*=\s*(\d+(?:\.\d+)?)'
        }
        
        # 常见错误类型
        self.error_types = {
            'calculation': '计算错误',
            'careless': '粗心错误',
            'concept': '概念理解错误',
            'method': '方法错误'
        }
    
    def parse_expression(self, expression: str) -> Dict[str, Any]:
        """解析数学表达式"""
        try:
            # 清理表达式
            cleaned = self.clean_expression(expression)
            
            # 尝试不同的模式匹配
            for operation, pattern in self.operation_patterns.items():
                match = re.match(pattern, cleaned)
                if match:
                    if operation == 'mixed':
                        return self.parse_mixed_expression(match.groups())
                    else:
                        return self.parse_simple_operation(operation, match.groups())
            
            # 如果没有匹配到标准模式，尝试解析复合表达式
            return self.parse_complex_expression(cleaned)
            
        except Exception as e:
            logger.error(f"表达式解析失败: {e}")
            return {"error": f"无法解析表达式: {expression}"}
    
    def clean_expression(self, expression: str) -> str:
        """清理表达式中的空格和特殊字符"""
        # 替换中文符号
        expression = expression.replace('×', '*').replace('÷', '/')
        expression = expression.replace('（', '(').replace('）', ')')
        
        # 移除多余空格
        expression = re.sub(r'\s+', ' ', expression.strip())
        
        return expression
    
    def parse_simple_operation(self, operation: str, groups: tuple) -> Dict[str, Any]:
        """解析简单四则运算"""
        try:
            if len(groups) != 3:
                return {"error": "表达式格式错误"}
            
            num1 = float(groups[0])
            num2 = float(groups[1])
            user_answer = float(groups[2])
            
            # 计算正确答案
            if operation == 'addition':
                correct_answer = num1 + num2
                operator = '+'
            elif operation == 'subtraction':
                correct_answer = num1 - num2
                operator = '-'
            elif operation == 'multiplication':
                correct_answer = num1 * num2
                operator = '*'
            elif operation == 'division':
                if num2 == 0:
                    return {"error": "除数不能为零"}
                correct_answer = num1 / num2
                operator = '/'
            else:
                return {"error": f"未知运算类型: {operation}"}
            
            # 检查答案正确性
            is_correct = abs(correct_answer - user_answer) < 0.001
            
            return {
                "operation_type": operation,
                "operand1": num1,
                "operator": operator,
                "operand2": num2,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "error_analysis": self.analyze_error(operation, num1, num2, user_answer, correct_answer) if not is_correct else None
            }
            
        except ValueError as e:
            return {"error": f"数值解析错误: {e}"}
    
    def parse_mixed_expression(self, groups: tuple) -> Dict[str, Any]:
        """解析混合运算表达式"""
        try:
            expression_str = groups[0]
            user_answer = float(groups[1])
            
            # 使用sympy计算正确答案
            expr = sympify(expression_str)
            correct_answer = float(expr.evalf())
            
            is_correct = abs(correct_answer - user_answer) < 0.001
            
            return {
                "operation_type": "mixed",
                "expression": expression_str,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "steps": self.get_calculation_steps(expression_str),
                "error_analysis": self.analyze_mixed_error(expression_str, user_answer, correct_answer) if not is_correct else None
            }
            
        except Exception as e:
            return {"error": f"混合运算解析错误: {e}"}
    
    def parse_complex_expression(self, expression: str) -> Dict[str, Any]:
        """解析复杂表达式"""
        try:
            # 分离表达式和答案
            parts = expression.split('=')
            if len(parts) != 2:
                return {"error": "表达式格式错误，缺少等号"}
            
            expr_str = parts[0].strip()
            user_answer = float(parts[1].strip())
            
            # 计算正确答案
            expr = sympify(expr_str)
            correct_answer = float(expr.evalf())
            
            is_correct = abs(correct_answer - user_answer) < 0.001
            
            return {
                "operation_type": "complex",
                "expression": expr_str,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "steps": self.get_calculation_steps(expr_str),
                "error_analysis": self.analyze_complex_error(expr_str, user_answer, correct_answer) if not is_correct else None
            }
            
        except Exception as e:
            return {"error": f"复杂表达式解析错误: {e}"}
    
    def get_calculation_steps(self, expression: str) -> List[str]:
        """获取计算步骤"""
        try:
            expr = sympify(expression)
            steps = []
            
            # 简单的步骤分解（可以根据需要扩展）
            steps.append(f"原式: {expression}")
            
            # 如果有括号，先计算括号内的
            if '(' in expression:
                steps.append("先计算括号内的运算")
            
            # 按运算优先级进行计算
            simplified = simplify(expr)
            if str(simplified) != str(expr):
                steps.append(f"化简后: {simplified}")
            
            result = expr.evalf()
            steps.append(f"最终结果: {result}")
            
            return steps
            
        except Exception as e:
            logger.error(f"获取计算步骤失败: {e}")
            return [f"计算 {expression}"]
    
    def analyze_error(self, operation: str, num1: float, num2: float, user_answer: float, correct_answer: float) -> Dict[str, Any]:
        """分析简单运算错误"""
        error_analysis = {
            "error_type": "",
            "description": "",
            "suggestion": "",
            "common_mistakes": []
        }
        
        difference = user_answer - correct_answer
        
        # 分析错误类型
        if operation == 'addition':
            if abs(difference) == abs(num2 - num1):
                error_analysis["error_type"] = "method"
                error_analysis["description"] = "可能把加法当成了减法"
                error_analysis["suggestion"] = "注意区分加号和减号"
            elif abs(difference) < 10:
                error_analysis["error_type"] = "careless"
                error_analysis["description"] = "计算粗心，结果接近正确答案"
                error_analysis["suggestion"] = "计算时要仔细，可以验算检查"
            else:
                error_analysis["error_type"] = "calculation"
                error_analysis["description"] = "加法计算错误"
                error_analysis["suggestion"] = "复习加法运算法则"
        
        elif operation == 'subtraction':
            if user_answer == num2 - num1:
                error_analysis["error_type"] = "method"
                error_analysis["description"] = "被减数和减数位置搞反了"
                error_analysis["suggestion"] = "注意减法的顺序：被减数 - 减数"
            elif abs(difference) < 10:
                error_analysis["error_type"] = "careless"
                error_analysis["description"] = "计算粗心"
                error_analysis["suggestion"] = "减法要仔细计算，注意借位"
            else:
                error_analysis["error_type"] = "calculation"
                error_analysis["description"] = "减法计算错误"
                error_analysis["suggestion"] = "复习减法运算，特别注意借位"
        
        elif operation == 'multiplication':
            if user_answer == num1 + num2:
                error_analysis["error_type"] = "method"
                error_analysis["description"] = "把乘法当成了加法"
                error_analysis["suggestion"] = "注意区分乘号和加号"
            elif abs(difference / correct_answer) < 0.1:
                error_analysis["error_type"] = "careless"
                error_analysis["description"] = "乘法计算粗心"
                error_analysis["suggestion"] = "乘法要逐位计算，注意进位"
            else:
                error_analysis["error_type"] = "calculation"
                error_analysis["description"] = "乘法计算错误"
                error_analysis["suggestion"] = "复习乘法口诀表"
        
        elif operation == 'division':
            if user_answer == num1 / num2 and user_answer != correct_answer:
                error_analysis["error_type"] = "concept"
                error_analysis["description"] = "除法概念理解错误"
                error_analysis["suggestion"] = "复习除法的意义和计算方法"
            else:
                error_analysis["error_type"] = "calculation"
                error_analysis["description"] = "除法计算错误"
                error_analysis["suggestion"] = "注意除法的计算步骤"
        
        return error_analysis
    
    def analyze_mixed_error(self, expression: str, user_answer: float, correct_answer: float) -> Dict[str, Any]:
        """分析混合运算错误"""
        return {
            "error_type": "calculation",
            "description": f"混合运算计算错误，正确答案是{correct_answer}",
            "suggestion": "按照运算顺序：先乘除，后加减，有括号先算括号",
            "steps_reminder": "建议分步计算，每一步都要仔细检查"
        }
    
    def analyze_complex_error(self, expression: str, user_answer: float, correct_answer: float) -> Dict[str, Any]:
        """分析复杂表达式错误"""
        return {
            "error_type": "calculation",
            "description": f"复杂运算计算错误，正确答案是{correct_answer}",
            "suggestion": "将复杂运算分解为简单步骤，逐步计算",
            "method_hint": "可以使用列式计算或画图辅助理解"
        }
    
    def batch_check(self, expressions: List[str]) -> List[Dict[str, Any]]:
        """批量检查算式"""
        results = []
        for expr in expressions:
            result = self.parse_expression(expr)
            results.append(result)
        return results
    
    def generate_similar_problems(self, expression: str, count: int = 3) -> List[str]:
        """生成相似题目"""
        try:
            parsed = self.parse_expression(expression)
            if "error" in parsed:
                return []
            
            similar_problems = []
            
            if parsed["operation_type"] in ['addition', 'subtraction', 'multiplication', 'division']:
                # 对于简单运算，生成同类型的题目
                op_map = {
                    'addition': '+',
                    'subtraction': '-', 
                    'multiplication': '*',
                    'division': '/'
                }
                
                operator = op_map[parsed["operation_type"]]
                base_num1 = parsed["operand1"]
                base_num2 = parsed["operand2"]
                
                for i in range(count):
                    # 在原数字基础上进行小幅变化
                    num1 = base_num1 + (i - 1) * 5
                    num2 = base_num2 + (i - 1) * 3
                    
                    if parsed["operation_type"] == "division" and num2 == 0:
                        num2 = 1
                    
                    if operator == '*':
                        result = num1 * num2
                    elif operator == '+':
                        result = num1 + num2
                    elif operator == '-':
                        result = num1 - num2
                    elif operator == '/':
                        result = num1 / num2
                    
                    problem = f"{int(num1)} {operator} {int(num2)} = ?"
                    similar_problems.append(problem)
            
            return similar_problems
            
        except Exception as e:
            logger.error(f"生成相似题目失败: {e}")
            return []


# 全局引擎实例
arithmetic_engine = ArithmeticEngine()


def init_engine():
    """初始化引擎"""
    logger.info("四则运算引擎初始化完成")


def check_arithmetic(expression: str) -> Dict[str, Any]:
    """检查四则运算"""
    return arithmetic_engine.parse_expression(expression)


def batch_check_arithmetic(expressions: List[str]) -> List[Dict[str, Any]]:
    """批量检查四则运算"""
    return arithmetic_engine.batch_check(expressions)