"""
AI智能练习题生成服务
基于错题分析和学生学习数据，智能生成相似练习题
"""
import json
import re
import math
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.homework import Homework, ErrorQuestion
from app.models.study_plan import StudyPlan
from app.models.exercise import ExerciseGeneration, GeneratedExercise as DBGeneratedExercise, ExerciseTemplate as DBExerciseTemplate
from app.services.ai_recommendation_service import StudentProfile


class ExerciseTemplate:
    """练习题模板"""
    def __init__(self, subject: str, topic: str, difficulty: str, template: str, 
                 answer_pattern: str, variations: List[Dict]):
        self.subject = subject
        self.topic = topic
        self.difficulty = difficulty
        self.template = template
        self.answer_pattern = answer_pattern
        self.variations = variations


class GeneratedExercise:
    """生成的练习题"""
    def __init__(self, number: int, subject: str, question_text: str, 
                 correct_answer: str, analysis: str, difficulty: str,
                 knowledge_points: List[str], question_type: str):
        self.number = number
        self.subject = subject
        self.question_text = question_text
        self.correct_answer = correct_answer
        self.analysis = analysis
        self.difficulty = difficulty
        self.knowledge_points = knowledge_points
        self.question_type = question_type


class AIExerciseGenerator:
    """AI练习题生成器"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # 初始化各学科题目模板库
        self.templates = {
            '数学': self._init_math_templates(),
            '语文': self._init_chinese_templates(),
            '英语': self._init_english_templates(),
            '物理': self._init_physics_templates(),
            '化学': self._init_chemistry_templates()
        }
        
        # 难度系数映射
        self.difficulty_mapping = {
            'easier': 0.7,   # 简单：原题难度的70%
            'same': 1.0,     # 相同：原题难度
            'harder': 1.3,   # 困难：原题难度的130%
            'mixed': 'mixed' # 混合：随机分布
        }
        
        # 题型权重配置
        self.question_type_weights = {
            'similar': 0.5,      # 相似题目：50%
            'extended': 0.3,     # 拓展变式：30%  
            'comprehensive': 0.2  # 综合应用：20%
        }
    
    def generate_exercises(self, original_error: Dict[str, Any], 
                         generation_config: Dict[str, Any]) -> List[GeneratedExercise]:
        """
        基于原始错题生成练习题集
        
        Args:
            original_error: 原始错题信息
            generation_config: 生成配置
            
        Returns:
            生成的练习题列表
        """
        try:
            # 解析生成配置
            question_count = generation_config.get('question_count', 5)
            difficulty_level = generation_config.get('difficulty_level', 'same')
            question_type = generation_config.get('question_type', 'similar')
            include_answers = generation_config.get('include_answers', True)
            include_analysis = generation_config.get('include_analysis', True)
            
            # 分析原题特征
            error_analysis = self._analyze_error_question(original_error)
            
            # 获取学生学习画像
            student_profile = self._get_student_profile(original_error.get('user_id'))
            
            # 生成练习题
            exercises = []
            
            for i in range(question_count):
                exercise_num = i + 1
                
                # 根据配置确定此题的难度
                current_difficulty = self._determine_question_difficulty(
                    difficulty_level, exercise_num, question_count
                )
                
                # 根据配置确定此题的类型
                current_type = self._determine_question_type(
                    question_type, exercise_num, question_count
                )
                
                # 生成具体题目
                exercise = self._generate_single_exercise(
                    original_error, error_analysis, student_profile,
                    exercise_num, current_difficulty, current_type,
                    include_answers, include_analysis
                )
                
                if exercise:
                    exercises.append(exercise)
            
            return exercises
            
        except Exception as e:
            print(f"练习题生成失败: {e}")
            return self._generate_fallback_exercises(
                original_error, generation_config
            )
    
    def _analyze_error_question(self, error: Dict[str, Any]) -> Dict[str, Any]:
        """分析错题特征"""
        analysis = {
            'subject': error.get('subject', '未知'),
            'question_text': error.get('question_text', ''),
            'error_type': error.get('error_type', ''),
            'knowledge_points': error.get('knowledge_points', []),
            'difficulty_indicators': [],
            'question_patterns': [],
            'key_concepts': []
        }
        
        question_text = analysis['question_text']
        subject = analysis['subject']
        
        # 数学题目分析
        if subject in ['数学', 'math']:
            analysis.update(self._analyze_math_question(question_text))
        
        # 语文题目分析
        elif subject in ['语文', 'chinese']:
            analysis.update(self._analyze_chinese_question(question_text))
        
        # 英语题目分析
        elif subject in ['英语', 'english']:
            analysis.update(self._analyze_english_question(question_text))
        
        # 其他学科
        else:
            analysis.update(self._analyze_general_question(question_text, subject))
        
        return analysis
    
    def _analyze_math_question(self, question_text: str) -> Dict[str, Any]:
        """分析数学题目特征"""
        patterns = {
            'calculation': ['计算', '×', '÷', '+', '-', '='],
            'equation': ['方程', '解', 'x', '未知数'],
            'geometry': ['面积', '周长', '体积', '三角形', '圆', '正方形'],
            'fraction': ['分数', '/', '分母', '分子'],
            'percentage': ['百分', '%', '折', '利率'],
            'word_problem': ['买', '卖', '速度', '时间', '路程'],
            'function': ['函数', 'f(x)', 'y='],
            'algebra': ['代数', '因式分解', '展开']
        }
        
        detected_patterns = []
        difficulty_indicators = []
        
        for pattern_type, keywords in patterns.items():
            if any(keyword in question_text for keyword in keywords):
                detected_patterns.append(pattern_type)
        
        # 难度指标分析
        if '×' in question_text or '÷' in question_text:
            numbers = re.findall(r'\d+', question_text)
            if numbers:
                max_num = max(int(n) for n in numbers if n.isdigit())
                if max_num > 1000:
                    difficulty_indicators.append('large_numbers')
                elif max_num < 100:
                    difficulty_indicators.append('small_numbers')
        
        if 'x' in question_text.lower():
            difficulty_indicators.append('variables')
        
        return {
            'question_patterns': detected_patterns,
            'difficulty_indicators': difficulty_indicators,
            'key_concepts': detected_patterns[:3]  # 取前3个主要概念
        }
    
    def _analyze_chinese_question(self, question_text: str) -> Dict[str, Any]:
        """分析语文题目特征"""
        patterns = {
            'author_work': ['作者', '作品', '诗人', '写的'],
            'reading_comprehension': ['阅读', '理解', '文章', '短文'],
            'poetry': ['古诗', '诗', '词', '句'],
            'grammar': ['词语', '语法', '句子', '标点'],
            'writing': ['写作', '作文', '表达', '修辞'],
            'classical_chinese': ['文言文', '翻译', '古文'],
            'pronunciation': ['拼音', '读音', '声调']
        }
        
        detected_patterns = []
        difficulty_indicators = []
        
        for pattern_type, keywords in patterns.items():
            if any(keyword in question_text for keyword in keywords):
                detected_patterns.append(pattern_type)
        
        # 难度分析
        if len(question_text) > 100:
            difficulty_indicators.append('long_text')
        if '文言文' in question_text or '古诗' in question_text:
            difficulty_indicators.append('classical_literature')
        if '理解' in question_text or '分析' in question_text:
            difficulty_indicators.append('comprehension_required')
        
        return {
            'question_patterns': detected_patterns,
            'difficulty_indicators': difficulty_indicators,
            'key_concepts': detected_patterns[:3]
        }
    
    def _analyze_english_question(self, question_text: str) -> Dict[str, Any]:
        """分析英语题目特征"""
        patterns = {
            'grammar': ['choose', 'correct', 'fill', 'blank'],
            'vocabulary': ['meaning', 'word', 'synonym', 'antonym'],
            'reading': ['reading', 'passage', 'article', 'text'],
            'translation': ['translate', 'translation', '翻译'],
            'writing': ['write', 'composition', 'essay'],
            'listening': ['listen', 'hear', 'sound'],
            'tense': ['past', 'present', 'future', 'tense']
        }
        
        detected_patterns = []
        difficulty_indicators = []
        
        question_lower = question_text.lower()
        
        for pattern_type, keywords in patterns.items():
            if any(keyword in question_lower for keyword in keywords):
                detected_patterns.append(pattern_type)
        
        # 难度分析
        word_count = len(question_text.split())
        if word_count > 50:
            difficulty_indicators.append('long_passage')
        elif word_count < 20:
            difficulty_indicators.append('simple_question')
        
        if any(word in question_lower for word in ['complex', 'difficult', 'advanced']):
            difficulty_indicators.append('advanced_level')
        
        return {
            'question_patterns': detected_patterns,
            'difficulty_indicators': difficulty_indicators,
            'key_concepts': detected_patterns[:3]
        }
    
    def _analyze_general_question(self, question_text: str, subject: str) -> Dict[str, Any]:
        """分析通用题目特征"""
        return {
            'question_patterns': ['general'],
            'difficulty_indicators': ['medium'],
            'key_concepts': [subject]
        }
    
    def _get_student_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取学生学习画像"""
        try:
            # 获取用户信息
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # 获取最近30天的学习数据
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_homework = self.db.query(Homework).filter(
                Homework.user_id == user_id,
                Homework.created_at >= thirty_days_ago
            ).all()
            
            # 计算学习能力评估
            if recent_homework:
                accuracy_rates = [hw.accuracy_rate for hw in recent_homework if hw.accuracy_rate]
                avg_accuracy = sum(accuracy_rates) / len(accuracy_rates) if accuracy_rates else 0.7
                
                # 学习频率
                study_days = len(set(hw.created_at.date() for hw in recent_homework))
                study_frequency = study_days / 30.0  # 每天学习频率
                
                # 错误类型分析
                error_questions = self.db.query(ErrorQuestion).filter(
                    ErrorQuestion.user_id == user_id,
                    ErrorQuestion.created_at >= thirty_days_ago
                ).all()
                
                common_errors = {}
                for eq in error_questions:
                    error_type = eq.error_type or '其他'
                    common_errors[error_type] = common_errors.get(error_type, 0) + 1
                
                return {
                    'user_id': user_id,
                    'grade': user.grade,
                    'average_accuracy': avg_accuracy,
                    'study_frequency': study_frequency,
                    'common_errors': common_errors,
                    'total_homework': len(recent_homework),
                    'learning_ability': self._assess_learning_ability(avg_accuracy, study_frequency)
                }
            
            return {
                'user_id': user_id,
                'grade': user.grade,
                'average_accuracy': 0.7,
                'study_frequency': 0.5,
                'common_errors': {},
                'total_homework': 0,
                'learning_ability': 'medium'
            }
            
        except Exception as e:
            print(f"获取学生画像失败: {e}")
            return None
    
    def _assess_learning_ability(self, accuracy: float, frequency: float) -> str:
        """评估学习能力等级"""
        if accuracy >= 0.85 and frequency >= 0.8:
            return 'high'
        elif accuracy >= 0.7 and frequency >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _determine_question_difficulty(self, difficulty_config: str, 
                                     question_num: int, total_count: int) -> str:
        """确定题目难度"""
        if difficulty_config == 'mixed':
            # 混合难度：前1/3简单，中1/3相同，后1/3困难
            if question_num <= total_count / 3:
                return 'easier'
            elif question_num <= total_count * 2 / 3:
                return 'same'
            else:
                return 'harder'
        else:
            return difficulty_config
    
    def _determine_question_type(self, type_config: str, 
                               question_num: int, total_count: int) -> str:
        """确定题目类型"""
        if type_config == 'mixed':
            # 混合类型：按权重随机分配
            rand = random.random()
            if rand < 0.5:
                return 'similar'
            elif rand < 0.8:
                return 'extended'
            else:
                return 'comprehensive'
        else:
            return type_config
    
    def _generate_single_exercise(self, original_error: Dict[str, Any], 
                                error_analysis: Dict[str, Any],
                                student_profile: Optional[Dict[str, Any]],
                                question_num: int, difficulty: str, 
                                question_type: str, include_answers: bool,
                                include_analysis: bool) -> Optional[GeneratedExercise]:
        """生成单个练习题"""
        
        subject = error_analysis['subject']
        
        # 根据学科调用不同的生成器
        if subject in ['数学', 'math']:
            return self._generate_math_exercise(
                original_error, error_analysis, student_profile,
                question_num, difficulty, question_type, 
                include_answers, include_analysis
            )
        elif subject in ['语文', 'chinese']:
            return self._generate_chinese_exercise(
                original_error, error_analysis, student_profile,
                question_num, difficulty, question_type,
                include_answers, include_analysis
            )
        elif subject in ['英语', 'english']:
            return self._generate_english_exercise(
                original_error, error_analysis, student_profile,
                question_num, difficulty, question_type,
                include_answers, include_analysis
            )
        else:
            return self._generate_general_exercise(
                original_error, error_analysis, student_profile,
                question_num, difficulty, question_type,
                include_answers, include_analysis
            )
    
    def _generate_math_exercise(self, original_error: Dict[str, Any],
                              error_analysis: Dict[str, Any],
                              student_profile: Optional[Dict[str, Any]],
                              question_num: int, difficulty: str,
                              question_type: str, include_answers: bool,
                              include_analysis: bool) -> GeneratedExercise:
        """生成数学练习题"""
        
        patterns = error_analysis.get('question_patterns', [])
        original_question = original_error.get('question_text', '')
        
        # 根据题目模式生成
        if 'calculation' in patterns:
            question, answer = self._generate_calculation_question(
                original_question, difficulty, student_profile
            )
        elif 'equation' in patterns:
            question, answer = self._generate_equation_question(
                original_question, difficulty, student_profile  
            )
        elif 'geometry' in patterns:
            question, answer = self._generate_geometry_question(
                original_question, difficulty, student_profile
            )
        elif 'word_problem' in patterns:
            question, answer = self._generate_word_problem(
                original_question, difficulty, student_profile
            )
        else:
            # 默认算术题
            question, answer = self._generate_default_math_question(
                original_question, difficulty, student_profile
            )
        
        # 生成解题分析
        analysis = ""
        if include_analysis:
            analysis = self._generate_math_analysis(patterns, difficulty, question_type)
        
        return GeneratedExercise(
            number=question_num,
            subject='数学',
            question_text=question,
            correct_answer=answer if include_answers else "",
            analysis=analysis,
            difficulty=difficulty,
            knowledge_points=error_analysis.get('key_concepts', []),
            question_type=question_type
        )
    
    def _generate_calculation_question(self, original: str, difficulty: str, 
                                     student_profile: Optional[Dict]) -> Tuple[str, str]:
        """生成计算题"""
        
        # 从原题中提取数字模式
        numbers = re.findall(r'\d+', original)
        operators = re.findall(r'[×÷+\-]', original)
        
        if not numbers:
            numbers = ['12', '8']  # 默认数字
        if not operators:
            operators = ['×']  # 默认运算符
        
        # 根据难度调整数字范围
        if difficulty == 'easier':
            base_range = (10, 50)
            mult_range = (2, 9)
        elif difficulty == 'harder':
            base_range = (100, 999)
            mult_range = (11, 25)
        else:  # same
            base_range = (50, 200)
            mult_range = (6, 15)
        
        # 生成新的计算题
        if '×' in operators:
            num1 = random.randint(*base_range)
            num2 = random.randint(*mult_range)
            question = f"计算：{num1} × {num2} = ?"
            answer = str(num1 * num2)
        elif '÷' in operators:
            # 确保能整除
            num2 = random.randint(*mult_range)
            result = random.randint(10, 100)
            num1 = num2 * result
            question = f"计算：{num1} ÷ {num2} = ?"
            answer = str(result)
        elif '+' in operators:
            num1 = random.randint(*base_range)
            num2 = random.randint(*base_range)
            question = f"计算：{num1} + {num2} = ?"
            answer = str(num1 + num2)
        else:  # 减法
            num1 = random.randint(*base_range)
            num2 = random.randint(10, num1)  # 确保结果为正
            question = f"计算：{num1} - {num2} = ?"
            answer = str(num1 - num2)
        
        return question, answer
    
    def _generate_equation_question(self, original: str, difficulty: str,
                                  student_profile: Optional[Dict]) -> Tuple[str, str]:
        """生成方程题"""
        
        if difficulty == 'easier':
            # 简单一元一次方程
            a = random.randint(5, 20)
            x = random.randint(2, 10)
            b = a + x
            question = f"解方程：x + {a} = {b}"
            answer = f"x = {x}"
        elif difficulty == 'harder':
            # 复杂方程
            a = random.randint(2, 5)
            b = random.randint(3, 12)
            x = random.randint(3, 8)
            c = a * x + b
            question = f"解方程：{a}x + {b} = {c}"
            answer = f"x = {x}"
        else:
            # 中等难度
            a = random.randint(2, 4)
            b = random.randint(5, 15)
            x = random.randint(2, 8)
            c = a * x + b
            question = f"解方程：{a}x + {b} = {c}"
            answer = f"x = {x}"
        
        return question, answer
    
    def _generate_geometry_question(self, original: str, difficulty: str,
                                  student_profile: Optional[Dict]) -> Tuple[str, str]:
        """生成几何题"""
        
        shapes = ['正方形', '长方形', '圆形', '三角形']
        shape = random.choice(shapes)
        
        if difficulty == 'easier':
            if shape == '正方形':
                side = random.randint(3, 8)
                question = f"一个正方形的边长是{side}cm，求它的面积。"
                answer = f"{side * side}平方厘米"
            else:
                length = random.randint(4, 10)
                width = random.randint(3, 8)
                question = f"一个长方形的长是{length}cm，宽是{width}cm，求它的面积。"
                answer = f"{length * width}平方厘米"
        else:
            if shape == '圆形':
                radius = random.randint(3, 7)
                question = f"一个圆的半径是{radius}cm，求它的面积。（π取3.14）"
                area = 3.14 * radius * radius
                answer = f"{area}平方厘米"
            else:
                side = random.randint(5, 12)
                question = f"一个正方形的周长是{side * 4}cm，求它的面积。"
                answer = f"{side * side}平方厘米"
        
        return question, answer
    
    def _generate_word_problem(self, original: str, difficulty: str,
                             student_profile: Optional[Dict]) -> Tuple[str, str]:
        """生成应用题"""
        
        problem_types = ['购物', '行程', '工程']
        problem_type = random.choice(problem_types)
        
        if problem_type == '购物':
            if difficulty == 'easier':
                price = random.randint(5, 20)
                quantity = random.randint(2, 5)
                question = f"小明买了{quantity}本笔记本，每本{price}元，一共花了多少钱？"
                answer = f"{price * quantity}元"
            else:
                price = random.randint(15, 50)
                quantity = random.randint(3, 8)
                discount = random.randint(5, 15)
                total = price * quantity
                final_price = total - discount
                question = f"小明买了{quantity}本书，每本{price}元，打折优惠{discount}元，实际付了多少钱？"
                answer = f"{final_price}元"
        
        elif problem_type == '行程':
            speed = random.randint(50, 80)
            time = random.randint(2, 5)
            distance = speed * time
            question = f"一辆汽车以每小时{speed}公里的速度行驶了{time}小时，行驶了多少公里？"
            answer = f"{distance}公里"
        
        else:  # 工程问题
            days1 = random.randint(8, 15)
            days2 = random.randint(12, 20)
            question = f"甲单独完成一项工作需要{days1}天，乙单独完成需要{days2}天，两人合作多少天能完成？"
            result = (days1 * days2) / (days1 + days2)
            answer = f"{result:.1f}天"
        
        return question, answer
    
    def _generate_default_math_question(self, original: str, difficulty: str,
                                      student_profile: Optional[Dict]) -> Tuple[str, str]:
        """生成默认数学题"""
        return self._generate_calculation_question(original, difficulty, student_profile)
    
    def _generate_chinese_exercise(self, original_error: Dict[str, Any],
                                 error_analysis: Dict[str, Any],
                                 student_profile: Optional[Dict[str, Any]],
                                 question_num: int, difficulty: str,
                                 question_type: str, include_answers: bool,
                                 include_analysis: bool) -> GeneratedExercise:
        """生成语文练习题"""
        
        patterns = error_analysis.get('question_patterns', [])
        
        if 'author_work' in patterns:
            question, answer = self._generate_author_question(difficulty)
        elif 'poetry' in patterns:
            question, answer = self._generate_poetry_question(difficulty)
        elif 'grammar' in patterns:
            question, answer = self._generate_grammar_question(difficulty)
        else:
            question, answer = self._generate_general_chinese_question(difficulty)
        
        analysis = ""
        if include_analysis:
            analysis = self._generate_chinese_analysis(patterns, difficulty)
        
        return GeneratedExercise(
            number=question_num,
            subject='语文',
            question_text=question,
            correct_answer=answer if include_answers else "",
            analysis=analysis,
            difficulty=difficulty,
            knowledge_points=error_analysis.get('key_concepts', []),
            question_type=question_type
        )
    
    def _generate_author_question(self, difficulty: str) -> Tuple[str, str]:
        """生成作者作品题"""
        
        if difficulty == 'easier':
            works_authors = {
                '《静夜思》': '李白',
                '《春晓》': '孟浩然',
                '《登鹳雀楼》': '王之涣',
                '《咏鹅》': '骆宾王'
            }
        elif difficulty == 'harder':
            works_authors = {
                '《岳阳楼记》': '范仲淹',
                '《醉翁亭记》': '欧阳修',
                '《小石潭记》': '柳宗元',
                '《桃花源记》': '陶渊明'
            }
        else:
            works_authors = {
                '《春望》': '杜甫',
                '《望岳》': '杜甫',
                '《茅屋为秋风所破歌》': '杜甫',
                '《将进酒》': '李白'
            }
        
        work = random.choice(list(works_authors.keys()))
        author = works_authors[work]
        question = f"请写出{work}的作者"
        
        return question, author
    
    def _generate_poetry_question(self, difficulty: str) -> Tuple[str, str]:
        """生成古诗题"""
        
        if difficulty == 'easier':
            poems = {
                "床前明月光，疑是地上霜": "举头望明月，低头思故乡",
                "春眠不觉晓，处处闻啼鸟": "夜来风雨声，花落知多少",
                "白日依山尽，黄河入海流": "欲穷千里目，更上一层楼"
            }
        else:
            poems = {
                "国破山河在，城春草木深": "感时花溅泪，恨别鸟惊心",
                "会当凌绝顶，一览众山小": "造化钟神秀，阴阳割昏晓",
                "安得广厦千万间，大庇天下寒士俱欢颜": "风雨不动安如山"
            }
        
        first_line = random.choice(list(poems.keys()))
        next_line = poems[first_line]
        question = f"请写出下句：{first_line}，_______"
        
        return question, next_line
    
    def _generate_grammar_question(self, difficulty: str) -> Tuple[str, str]:
        """生成语法题"""
        
        if difficulty == 'easier':
            question = "下列词语中，没有错别字的是（）\nA. 变本加利  B. 再接再励  C. 一如既往  D. 走投无路"
            answer = "D"
        else:
            question = "下列句子中，语法正确的是（）\nA. 通过这次活动，使我受到了很大教育  B. 这本书对我很有价值  C. 能否提高学习成绩的关键是学习方法  D. 我们必须认真克服并及时发现工作中的缺点"
            answer = "B"
        
        return question, answer
    
    def _generate_general_chinese_question(self, difficulty: str) -> Tuple[str, str]:
        """生成通用语文题"""
        return self._generate_grammar_question(difficulty)
    
    def _generate_english_exercise(self, original_error: Dict[str, Any],
                                 error_analysis: Dict[str, Any],
                                 student_profile: Optional[Dict[str, Any]],
                                 question_num: int, difficulty: str,
                                 question_type: str, include_answers: bool,
                                 include_analysis: bool) -> GeneratedExercise:
        """生成英语练习题"""
        
        patterns = error_analysis.get('question_patterns', [])
        
        if 'grammar' in patterns:
            question, answer = self._generate_english_grammar_question(difficulty)
        elif 'vocabulary' in patterns:
            question, answer = self._generate_vocabulary_question(difficulty)
        elif 'translation' in patterns:
            question, answer = self._generate_translation_question(difficulty)
        else:
            question, answer = self._generate_general_english_question(difficulty)
        
        analysis = ""
        if include_analysis:
            analysis = self._generate_english_analysis(patterns, difficulty)
        
        return GeneratedExercise(
            number=question_num,
            subject='英语',
            question_text=question,
            correct_answer=answer if include_answers else "",
            analysis=analysis,
            difficulty=difficulty,
            knowledge_points=error_analysis.get('key_concepts', []),
            question_type=question_type
        )
    
    def _generate_english_grammar_question(self, difficulty: str) -> Tuple[str, str]:
        """生成英语语法题"""
        
        if difficulty == 'easier':
            subjects = ['I', 'You', 'We', 'They']
            verbs = ['go', 'come', 'play', 'study']
            subject = random.choice(subjects)
            verb = random.choice(verbs)
            question = f"Choose the correct form: {subject} _____ to school every day. (A. go B. goes C. going D. went)"
            if subject in ['I', 'You', 'We', 'They']:
                answer = "A. go"
            else:
                answer = "B. goes"
        else:
            question = "Choose the correct answer: If I _____ you, I would study harder. (A. am B. was C. were D. be)"
            answer = "C. were"
        
        return question, answer
    
    def _generate_vocabulary_question(self, difficulty: str) -> Tuple[str, str]:
        """生成词汇题"""
        
        if difficulty == 'easier':
            question = "What does 'happy' mean? (A. 悲伤 B. 高兴 C. 生气 D. 害怕)"
            answer = "B. 高兴"
        else:
            question = "Choose the synonym of 'enormous': (A. tiny B. huge C. medium D. small)"
            answer = "B. huge"
        
        return question, answer
    
    def _generate_translation_question(self, difficulty: str) -> Tuple[str, str]:
        """生成翻译题"""
        
        if difficulty == 'easier':
            question = "Translate: I like reading books."
            answer = "我喜欢读书。"
        else:
            question = "Translate: Despite the difficulties, she never gave up her dream."
            answer = "尽管困难重重，她从未放弃过自己的梦想。"
        
        return question, answer
    
    def _generate_general_english_question(self, difficulty: str) -> Tuple[str, str]:
        """生成通用英语题"""
        return self._generate_english_grammar_question(difficulty)
    
    def _generate_general_exercise(self, original_error: Dict[str, Any],
                                 error_analysis: Dict[str, Any],
                                 student_profile: Optional[Dict[str, Any]],
                                 question_num: int, difficulty: str,
                                 question_type: str, include_answers: bool,
                                 include_analysis: bool) -> GeneratedExercise:
        """生成通用练习题"""
        
        subject = error_analysis.get('subject', '通用')
        question = f"{subject}练习题 {question_num}：基于错误类型【{original_error.get('error_type', '未知')}】的{difficulty}级别练习"
        answer = f"参考答案 {question_num}"
        analysis = f"这是一道{subject}基础练习题，重点训练相关概念和方法。" if include_analysis else ""
        
        return GeneratedExercise(
            number=question_num,
            subject=subject,
            question_text=question,
            correct_answer=answer if include_answers else "",
            analysis=analysis,
            difficulty=difficulty,
            knowledge_points=[subject],
            question_type=question_type
        )
    
    def _generate_math_analysis(self, patterns: List[str], difficulty: str, question_type: str) -> str:
        """生成数学解题分析"""
        
        if 'calculation' in patterns:
            if difficulty == 'easier':
                return "本题考查基础运算能力，注意计算的准确性，可以通过口算或列竖式计算。"
            elif difficulty == 'harder':
                return "本题考查复杂运算，需要注意运算顺序和进位借位，建议分步计算并验证结果。"
            else:
                return "本题考查四则运算，掌握运算法则，注意计算过程中的细节。"
        
        elif 'equation' in patterns:
            return "解一元一次方程的步骤：移项、合并同类项、系数化为1。注意等号两边同时进行相同运算。"
        
        elif 'geometry' in patterns:
            return "几何题重点是理解图形性质和面积公式，注意单位统一，画图有助于理解题意。"
        
        else:
            return "本题综合考查数学基础知识，需要仔细审题，选择合适的解题方法。"
    
    def _generate_chinese_analysis(self, patterns: List[str], difficulty: str) -> str:
        """生成语文解题分析"""
        
        if 'author_work' in patterns:
            return "古诗文作者作品是语文基础知识，需要日常积累记忆，建议按朝代或主题整理。"
        
        elif 'poetry' in patterns:
            return "古诗填空重在理解诗意和掌握名句，建议熟读背诵，理解诗人情感和时代背景。"
        
        elif 'grammar' in patterns:
            return "语法题需要掌握词汇正确写法和语法规则，注意词语搭配和句式结构。"
        
        else:
            return "语文综合题考查语言文字运用能力，需要培养良好的语感和表达习惯。"
    
    def _generate_english_analysis(self, patterns: List[str], difficulty: str) -> str:
        """生成英语解题分析"""
        
        if 'grammar' in patterns:
            return "英语语法题需要掌握时态、语态、主谓一致等基本规则，建议多做练习巩固。"
        
        elif 'vocabulary' in patterns:
            return "词汇题考查单词意思和用法，需要在语境中理解记忆，注意词汇的多义性。"
        
        elif 'translation' in patterns:
            return "翻译题要理解原文意思，注意中英文表达习惯的差异，保持译文自然流畅。"
        
        else:
            return "英语综合练习需要词汇、语法、阅读理解等多方面能力，建议均衡发展。"
    
    def _generate_fallback_exercises(self, original_error: Dict[str, Any],
                                   generation_config: Dict[str, Any]) -> List[GeneratedExercise]:
        """生成后备练习题（当AI生成失败时使用）"""
        
        exercises = []
        question_count = generation_config.get('question_count', 5)
        subject = original_error.get('subject', '数学')
        difficulty = generation_config.get('difficulty_level', 'same')
        
        for i in range(question_count):
            exercise = GeneratedExercise(
                number=i + 1,
                subject=subject,
                question_text=f"{subject}练习题 {i + 1}：基于错误分析的{difficulty}难度练习",
                correct_answer=f"参考答案 {i + 1}",
                analysis=f"这是一道{subject}基础练习题，请仔细审题并运用相关知识点解答。",
                difficulty=difficulty,
                knowledge_points=[subject],
                question_type='similar'
            )
            exercises.append(exercise)
        
        return exercises
    
    def _init_math_templates(self) -> List[ExerciseTemplate]:
        """初始化数学题模板"""
        return [
            # 可以在这里添加更多复杂的题目模板
        ]
    
    def _init_chinese_templates(self) -> List[ExerciseTemplate]:
        """初始化语文题模板"""
        return []
    
    def _init_english_templates(self) -> List[ExerciseTemplate]:
        """初始化英语题模板"""
        return []
    
    def _init_physics_templates(self) -> List[ExerciseTemplate]:
        """初始化物理题模板"""
        return []
    
    def _init_chemistry_templates(self) -> List[ExerciseTemplate]:
        """初始化化学题模板"""
        return []
    
    # ==================== 新增方法：基于年级和学科生成题目 ====================
    
    def generate_by_grade_and_subject(self, user_id: int, grade: str, subject: str, 
                                    generation_config: Dict[str, Any]) -> List[GeneratedExercise]:
        """
        基于年级和学科生成练习题集
        
        Args:
            user_id: 用户ID
            grade: 年级
            subject: 学科
            generation_config: 生成配置
            
        Returns:
            生成的练习题列表
        """
        try:
            # 获取用户学习画像
            user_profile = self._get_user_profile_by_id(user_id)
            
            # 构建虚拟的"原始错题"用于分析
            virtual_error = {
                'user_id': user_id,
                'subject': subject,
                'grade': grade,
                'question_text': f'{subject}基础练习',
                'error_type': 'practice',
                'knowledge_points': self._get_grade_subject_knowledge_points(grade, subject)
            }
            
            # 使用现有的生成逻辑
            return self.generate_exercises(virtual_error, generation_config)
            
        except Exception as e:
            print(f"基于年级学科生成题目失败: {e}")
            return self._generate_fallback_exercises_by_subject(grade, subject, generation_config)
    
    def generate_exercise_set(self, user_profile: Dict[str, Any], 
                            exercise_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成完整的练习题集
        
        Args:
            user_profile: 用户画像
            exercise_config: 练习配置
            
        Returns:
            包含题目列表和元数据的字典
        """
        try:
            start_time = datetime.now()
            
            # 提取配置参数
            subject = exercise_config.get('subject')
            grade = exercise_config.get('grade')
            question_count = exercise_config.get('question_count', 10)
            difficulty_level = exercise_config.get('difficulty_level', 'same')
            question_types = exercise_config.get('question_types', ['similar'])
            
            # 生成题目
            exercises = self.generate_by_grade_and_subject(
                user_profile.get('user_id'),
                grade,
                subject,
                exercise_config
            )
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # 返回完整结果
            return {
                'exercises': exercises,
                'metadata': {
                    'generation_time': generation_time,
                    'total_questions': len(exercises),
                    'subject': subject,
                    'grade': grade,
                    'difficulty_level': difficulty_level,
                    'success_rate': 1.0 if exercises else 0.0,
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            print(f"生成练习题集失败: {e}")
            return {
                'exercises': [],
                'metadata': {
                    'generation_time': 0,
                    'total_questions': 0,
                    'subject': exercise_config.get('subject'),
                    'grade': exercise_config.get('grade'),
                    'success_rate': 0.0,
                    'error_message': str(e),
                    'generated_at': datetime.now().isoformat()
                }
            }
    
    def validate_generated_exercises(self, exercises: List[GeneratedExercise]) -> Dict[str, Any]:
        """
        验证生成题目的质量
        
        Args:
            exercises: 生成的题目列表
            
        Returns:
            验证结果
        """
        validation_result = {
            'is_valid': True,
            'total_count': len(exercises),
            'valid_count': 0,
            'quality_score': 0.0,
            'issues': []
        }
        
        if not exercises:
            validation_result['is_valid'] = False
            validation_result['issues'].append('没有生成任何题目')
            return validation_result
        
        valid_exercises = 0
        total_quality = 0.0
        
        for i, exercise in enumerate(exercises):
            issues = []
            
            # 检查必需字段
            if not exercise.question_text or not exercise.question_text.strip():
                issues.append(f'题目{i+1}: 题目内容为空')
            
            if not exercise.correct_answer or not exercise.correct_answer.strip():
                issues.append(f'题目{i+1}: 答案为空')
            
            if len(exercise.question_text) < 10:
                issues.append(f'题目{i+1}: 题目内容过短')
            
            if len(exercise.question_text) > 500:
                issues.append(f'题目{i+1}: 题目内容过长')
            
            # 计算质量分数
            quality_score = 10.0
            if issues:
                quality_score = max(0, quality_score - len(issues) * 2)
            
            if not issues:
                valid_exercises += 1
            else:
                validation_result['issues'].extend(issues)
            
            total_quality += quality_score
        
        validation_result['valid_count'] = valid_exercises
        validation_result['quality_score'] = total_quality / len(exercises) if exercises else 0
        validation_result['is_valid'] = valid_exercises >= len(exercises) * 0.8  # 80%以上有效
        
        return validation_result
    
    def _get_user_profile_by_id(self, user_id: int) -> Dict[str, Any]:
        """根据用户ID获取用户画像"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {'user_id': user_id, 'grade': '三年级', 'learning_ability': 'medium'}
            
            # 获取用户的学习数据
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_homework = self.db.query(Homework).filter(
                Homework.user_id == user_id,
                Homework.created_at >= thirty_days_ago
            ).all()
            
            # 计算学习能力
            if recent_homework:
                accuracy_rates = [hw.accuracy_rate for hw in recent_homework if hw.accuracy_rate]
                avg_accuracy = sum(accuracy_rates) / len(accuracy_rates) if accuracy_rates else 0.7
                learning_ability = self._assess_learning_ability(avg_accuracy, len(recent_homework) / 30.0)
            else:
                learning_ability = 'medium'
            
            return {
                'user_id': user_id,
                'grade': user.grade or '三年级',
                'learning_ability': learning_ability,
                'recent_homework_count': len(recent_homework)
            }
            
        except Exception as e:
            print(f"获取用户画像失败: {e}")
            return {'user_id': user_id, 'grade': '三年级', 'learning_ability': 'medium'}
    
    def _get_grade_subject_knowledge_points(self, grade: str, subject: str) -> List[str]:
        """获取年级学科的知识点"""
        knowledge_points_map = {
            '一年级': {
                '数学': ['10以内加减法', '认识图形', '比较大小', '数的组成'],
                '语文': ['拼音认读', '简单汉字', '词语搭配', '短句理解'],
                '英语': ['字母认识', '基本单词', '简单问候']
            },
            '二年级': {
                '数学': ['100以内加减法', '乘法口诀', '长度单位', '时间认识'],
                '语文': ['词语理解', '句子补充', '短文阅读', '标点使用'],
                '英语': ['单词认读', '简单对话', '颜色数字']
            },
            '三年级': {
                '数学': ['万以内加减法', '两三位数乘除法', '分数初步', '面积周长'],
                '语文': ['段落理解', '词语辨析', '作文片段', '古诗背诵'],
                '英语': ['语法基础', '时态认识', '日常对话']
            },
            '四年级': {
                '数学': ['大数认识', '小数概念', '图形计算', '统计图表'],
                '语文': ['阅读理解', '写作技巧', '修辞手法', '文言启蒙'],
                '英语': ['句型变换', '阅读理解', '写作基础']
            },
            '五年级': {
                '数学': ['分数运算', '小数运算', '几何图形', '应用题综合'],
                '语文': ['现代文阅读', '作文提升', '语法知识', '古诗词'],
                '英语': ['语法深化', '完形填空', '写作提升']
            },
            '六年级': {
                '数学': ['分数百分数', '比例应用', '立体图形', '概率统计'],
                '语文': ['文学常识', '议论说明', '综合写作', '古文理解'],
                '英语': ['阅读技巧', '写作高级', '语法综合']
            }
        }
        
        return knowledge_points_map.get(grade, {}).get(subject, ['基础知识', '基本技能'])
    
    def _generate_fallback_exercises_by_subject(self, grade: str, subject: str, 
                                              generation_config: Dict[str, Any]) -> List[GeneratedExercise]:
        """基于学科的后备题目生成"""
        exercises = []
        question_count = generation_config.get('question_count', 5)
        difficulty = generation_config.get('difficulty_level', 'same')
        
        knowledge_points = self._get_grade_subject_knowledge_points(grade, subject)
        
        for i in range(question_count):
            exercise_num = i + 1
            knowledge_point = knowledge_points[i % len(knowledge_points)]
            
            if subject == '数学':
                question, answer = self._generate_math_fallback_question(grade, knowledge_point, difficulty)
            elif subject == '语文':
                question, answer = self._generate_chinese_fallback_question(grade, knowledge_point, difficulty)
            elif subject == '英语':
                question, answer = self._generate_english_fallback_question(grade, knowledge_point, difficulty)
            else:
                question = f"{subject} {grade} 练习题 {exercise_num}：请完成关于 {knowledge_point} 的练习。"
                answer = f"{knowledge_point} 参考答案 {exercise_num}"
            
            exercise = GeneratedExercise(
                number=exercise_num,
                subject=subject,
                question_text=question,
                correct_answer=answer,
                analysis=f"这道题考查 {knowledge_point}，属于{grade}阶段的基础知识。",
                difficulty=difficulty,
                knowledge_points=[knowledge_point],
                question_type='practice'
            )
            exercises.append(exercise)
        
        return exercises
    
    def _generate_math_fallback_question(self, grade: str, knowledge_point: str, difficulty: str) -> Tuple[str, str]:
        """生成数学后备题目"""
        if '加减法' in knowledge_point:
            if grade in ['一年级', '二年级']:
                a = random.randint(1, 50)
                b = random.randint(1, 50)
                if random.choice([True, False]):
                    question = f"计算：{a} + {b} = ?"
                    answer = str(a + b)
                else:
                    if a < b:
                        a, b = b, a
                    question = f"计算：{a} - {b} = ?"
                    answer = str(a - b)
            else:
                a = random.randint(100, 999)
                b = random.randint(100, 999)
                question = f"计算：{a} + {b} = ?"
                answer = str(a + b)
        elif '乘法' in knowledge_point:
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            question = f"计算：{a} × {b} = ?"
            answer = str(a * b)
        else:
            question = f"请完成关于 {knowledge_point} 的数学练习。"
            answer = "参考答案"
        
        return question, answer
    
    def _generate_chinese_fallback_question(self, grade: str, knowledge_point: str, difficulty: str) -> Tuple[str, str]:
        """生成语文后备题目"""
        if '拼音' in knowledge_point:
            words = ['学校', '老师', '同学', '书包', '铅笔']
            word = random.choice(words)
            question = f"请给下面的汉字标注拼音：{word}"
            answer = "请查字典标注正确拼音"
        elif '词语' in knowledge_point:
            question = "请写出下列词语的反义词：高兴"
            answer = "难过"
        elif '古诗' in knowledge_point:
            question = "请默写《静夜思》的前两句"
            answer = "床前明月光，疑是地上霜"
        else:
            question = f"请完成关于 {knowledge_point} 的语文练习。"
            answer = "参考答案"
        
        return question, answer
    
    def _generate_english_fallback_question(self, grade: str, knowledge_point: str, difficulty: str) -> Tuple[str, str]:
        """生成英语后备题目"""
        if '单词' in knowledge_point:
            question = "请写出下列单词的中文意思：apple"
            answer = "苹果"
        elif '字母' in knowledge_point:
            question = "请按顺序写出英文字母A-E"
            answer = "A B C D E"
        elif '语法' in knowledge_point:
            question = "请选择正确答案：I _____ a student. (A. am B. is C. are)"
            answer = "A. am"
        else:
            question = f"请完成关于 {knowledge_point} 的英语练习。"
            answer = "参考答案"
        
        return question, answer