"""
AI学习建议服务
基于学生的年级、错题数据、学习习惯等多维度数据生成个性化学习建议
"""
import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.user import User
from app.models.homework import Homework, ErrorQuestion
from app.models.study_plan import StudyPlan, StudyTask, StudyProgress
from app.models.parent_child import ParentChild


class StudentProfile:
    """学生画像"""
    def __init__(self, user_id: int, grade: str, total_homework: int, 
                 accuracy_rate: float, study_frequency: float, 
                 error_patterns: Dict[str, int], subject_performance: Dict[str, float],
                 learning_consistency: float):
        self.user_id = user_id
        self.grade = grade
        self.total_homework = total_homework
        self.accuracy_rate = accuracy_rate
        self.study_frequency = study_frequency  # 每周学习天数
        self.error_patterns = error_patterns
        self.subject_performance = subject_performance
        self.learning_consistency = learning_consistency  # 学习规律性评分 0-1


class LearningRecommendation:
    """学习建议"""
    def __init__(self, recommendation_type: str, priority: str, 
                 content: str, action_items: List[str], 
                 estimated_improvement: float):
        self.type = recommendation_type
        self.priority = priority  # high, medium, low
        self.content = content
        self.action_items = action_items
        self.estimated_improvement = estimated_improvement


class AIRecommendationService:
    """AI学习建议服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.subject_mapping = {
            "math": "数学", "chinese": "语文", "english": "英语", 
            "physics": "物理", "chemistry": "化学"
        }
        
        # 年级难度系数
        self.grade_difficulty = {
            "小学一年级": 1.0, "小学二年级": 1.2, "小学三年级": 1.4,
            "小学四年级": 1.6, "小学五年级": 1.8, "小学六年级": 2.0,
            "初中一年级": 2.5, "初中二年级": 3.0, "初中三年级": 3.5,
            "高中一年级": 4.0, "高中二年级": 4.5, "高中三年级": 5.0
        }
    
    def generate_ai_recommendations(self, child_id: int) -> List[Dict[str, Any]]:
        """
        生成AI驱动的学习建议
        """
        try:
            # 构建学生画像
            student_profile = self._build_student_profile(child_id)
            
            # 生成多维度建议
            recommendations = []
            
            # 1. 基础能力建议
            basic_recommendations = self._generate_basic_ability_recommendations(student_profile)
            recommendations.extend(basic_recommendations)
            
            # 2. 学科专项建议
            subject_recommendations = self._generate_subject_specific_recommendations(student_profile)
            recommendations.extend(subject_recommendations)
            
            # 3. 学习习惯建议
            habit_recommendations = self._generate_learning_habit_recommendations(student_profile)
            recommendations.extend(habit_recommendations)
            
            # 4. 错题复习策略
            error_recommendations = self._generate_error_review_strategies(student_profile)
            recommendations.extend(error_recommendations)
            
            # 5. 时间管理建议
            time_recommendations = self._generate_time_management_recommendations(student_profile)
            recommendations.extend(time_recommendations)
            
            # 按优先级排序并限制数量
            recommendations.sort(key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)
            
            return recommendations[:8]  # 返回前8条最重要的建议
            
        except Exception as e:
            print(f"AI建议生成错误: {e}")
            return self._get_fallback_recommendations()
    
    def _build_student_profile(self, child_id: int) -> StudentProfile:
        """构建学生画像"""
        # 获取基本信息
        user = self.db.query(User).filter(User.id == child_id).first()
        grade = user.grade if user else "未设置"
        
        # 获取作业数据（最近30天）
        thirty_days_ago = datetime.now() - timedelta(days=30)
        homework_records = self.db.query(Homework).filter(
            Homework.user_id == child_id,
            Homework.created_at >= thirty_days_ago
        ).all()
        
        total_homework = len(homework_records)
        
        # 计算平均准确率
        accuracy_rates = [hw.accuracy_rate for hw in homework_records if hw.accuracy_rate is not None]
        avg_accuracy = sum(accuracy_rates) / len(accuracy_rates) if accuracy_rates else 0
        
        # 计算学习频率（每周学习天数）
        study_days = set(hw.created_at.date() for hw in homework_records)
        weeks = max(1, len(study_days) // 7 if len(study_days) >= 7 else 1)
        study_frequency = len(study_days) / (4.3 * weeks)  # 转换为每周天数
        
        # 分析错题模式
        error_questions = self.db.query(ErrorQuestion).filter(
            ErrorQuestion.user_id == child_id,
            ErrorQuestion.created_at >= thirty_days_ago
        ).all()
        
        error_patterns = {}
        for eq in error_questions:
            if eq.error_type:
                error_patterns[eq.error_type] = error_patterns.get(eq.error_type, 0) + 1
        
        # 计算各学科表现
        subject_performance = {}
        for subject_code, subject_name in self.subject_mapping.items():
            subject_homework = [hw for hw in homework_records if hw.subject == subject_code]
            if subject_homework:
                subject_rates = [hw.accuracy_rate for hw in subject_homework if hw.accuracy_rate is not None]
                if subject_rates:
                    subject_performance[subject_name] = sum(subject_rates) / len(subject_rates)
        
        # 计算学习规律性
        if len(homework_records) > 1:
            # 计算学习时间间隔的标准差，越小越规律
            intervals = []
            sorted_records = sorted(homework_records, key=lambda x: x.created_at)
            for i in range(1, len(sorted_records)):
                interval = (sorted_records[i].created_at - sorted_records[i-1].created_at).days
                intervals.append(min(interval, 7))  # 限制最大间隔为7天
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
                std_dev = math.sqrt(variance)
                # 规律性评分：标准差越小，规律性越高
                learning_consistency = max(0, 1 - (std_dev / 7))
            else:
                learning_consistency = 0.5
        else:
            learning_consistency = 0.5
        
        return StudentProfile(
            user_id=child_id,
            grade=grade,
            total_homework=total_homework,
            accuracy_rate=avg_accuracy,
            study_frequency=study_frequency,
            error_patterns=error_patterns,
            subject_performance=subject_performance,
            learning_consistency=learning_consistency
        )
    
    def _generate_basic_ability_recommendations(self, profile: StudentProfile) -> List[Dict[str, Any]]:
        """生成基础能力建议"""
        recommendations = []
        
        # 根据整体准确率评估
        if profile.accuracy_rate < 0.6:
            recommendations.append({
                "type": "基础能力",
                "priority": "high",
                "icon": "🎯",
                "title": "加强基础训练",
                "content": f"当前正确率为{int(profile.accuracy_rate * 100)}%，需要重点加强基础知识练习。建议从简单题目开始，逐步提升难度，打好基础。",
                "action_items": [
                    "每天完成15-20道基础题",
                    "重做做错的题目直到完全掌握",
                    "建立错题本系统整理"
                ],
                "estimated_improvement": 15
            })
        elif profile.accuracy_rate < 0.8:
            recommendations.append({
                "type": "基础能力",
                "priority": "medium",
                "icon": "📈",
                "title": "稳步提升准确率",
                "content": f"当前正确率{int(profile.accuracy_rate * 100)}%表现良好，继续保持并适度增加练习难度，争取突破80%。",
                "action_items": [
                    "增加中等难度题目练习",
                    "注重解题方法和思路总结",
                    "定期进行综合性练习"
                ],
                "estimated_improvement": 10
            })
        else:
            recommendations.append({
                "type": "基础能力",
                "priority": "low",
                "icon": "🏆",
                "title": "挑战更高难度",
                "content": f"当前正确率{int(profile.accuracy_rate * 100)}%表现优秀！可以尝试挑战更高难度的题目，拓展知识面。",
                "action_items": [
                    "尝试奥数或竞赛题目",
                    "探索跨学科综合应用",
                    "担任小老师帮助同学"
                ],
                "estimated_improvement": 5
            })
        
        return recommendations
    
    def _generate_subject_specific_recommendations(self, profile: StudentProfile) -> List[Dict[str, Any]]:
        """生成学科专项建议"""
        recommendations = []
        
        if not profile.subject_performance:
            return recommendations
        
        # 找出表现最差的学科
        worst_subject = min(profile.subject_performance.keys(), 
                          key=lambda k: profile.subject_performance[k])
        worst_score = profile.subject_performance[worst_subject]
        
        # 找出表现最好的学科
        best_subject = max(profile.subject_performance.keys(), 
                         key=lambda k: profile.subject_performance[k])
        best_score = profile.subject_performance[best_subject]
        
        if worst_score < 0.7:
            subject_strategies = {
                "数学": {
                    "content": "建议加强计算能力和逻辑思维训练，多做基础运算练习。",
                    "actions": ["每天练习20道口算题", "重点复习四则运算规则", "使用数学思维导图整理知识点"]
                },
                "语文": {
                    "content": "需要加强阅读理解和词汇积累，提高语言文字运用能力。",
                    "actions": ["每天阅读30分钟课外书籍", "积累好词好句并应用", "多做阅读理解专项练习"]
                },
                "英语": {
                    "content": "建议加强词汇记忆和语法基础，多听多说提高语感。",
                    "actions": ["每天背诵10个新单词", "听英语歌曲或动画片", "与家长进行简单英语对话"]
                },
                "物理": {
                    "content": "需要加强概念理解和实验观察，培养物理思维。",
                    "actions": ["重点理解物理概念和公式", "多做实验观察生活现象", "画图分析物理过程"]
                },
                "化学": {
                    "content": "建议加强化学方程式记忆和实验理解。",
                    "actions": ["熟练掌握常见化学方程式", "理解化学反应原理", "观察日常化学现象"]
                }
            }
            
            strategy = subject_strategies.get(worst_subject, {
                "content": f"需要针对{worst_subject}进行专项强化练习。",
                "actions": ["增加该学科练习时间", "寻求老师或同学帮助", "制定专项学习计划"]
            })
            
            recommendations.append({
                "type": "学科专项",
                "priority": "high",
                "icon": "📚",
                "title": f"{worst_subject}专项提升",
                "content": f"{worst_subject}当前表现需要关注（正确率{int(worst_score * 100)}%）。{strategy['content']}",
                "action_items": strategy["actions"],
                "estimated_improvement": 20
            })
        
        if best_score > 0.85 and len(profile.subject_performance) > 1:
            recommendations.append({
                "type": "学科专项",
                "priority": "low",
                "icon": "⭐",
                "title": f"发挥{best_subject}优势",
                "content": f"{best_subject}表现优秀（正确率{int(best_score * 100)}%）！可以利用这个优势带动其他学科学习。",
                "action_items": [
                    f"参加{best_subject}竞赛或兴趣小组",
                    f"用{best_subject}的学习方法指导其他学科",
                    f"分享{best_subject}学习经验给同学"
                ],
                "estimated_improvement": 5
            })
        
        return recommendations
    
    def _generate_learning_habit_recommendations(self, profile: StudentProfile) -> List[Dict[str, Any]]:
        """生成学习习惯建议"""
        recommendations = []
        
        # 学习频率建议
        if profile.study_frequency < 3:
            recommendations.append({
                "type": "学习习惯",
                "priority": "high",
                "icon": "📅",
                "title": "建立规律学习节奏",
                "content": f"当前每周学习{profile.study_frequency:.1f}天，建议增加学习频率，保持每周至少4-5天的学习节奏。",
                "action_items": [
                    "制定每周学习计划",
                    "设定固定的学习时间",
                    "使用学习打卡工具"
                ],
                "estimated_improvement": 15
            })
        elif profile.study_frequency > 6.5:
            recommendations.append({
                "type": "学习习惯",
                "priority": "medium",
                "icon": "⚖️",
                "title": "注意学习与休息平衡",
                "content": f"学习很勤奋（每周{profile.study_frequency:.1f}天）！也要注意适当休息，保持学习效率。",
                "action_items": [
                    "每周安排1-2天休息时间",
                    "学习间隙进行适当运动",
                    "保证充足的睡眠时间"
                ],
                "estimated_improvement": 8
            })
        
        # 学习规律性建议
        if profile.learning_consistency < 0.6:
            recommendations.append({
                "type": "学习习惯",
                "priority": "medium",
                "icon": "🎯",
                "title": "提高学习规律性",
                "content": "建议制定更规律的学习时间表，养成固定时间学习的好习惯。",
                "action_items": [
                    "每天固定时间段学习",
                    "创建学习环境仪式感",
                    "使用番茄钟等时间管理工具"
                ],
                "estimated_improvement": 12
            })
        
        return recommendations
    
    def _generate_error_review_strategies(self, profile: StudentProfile) -> List[Dict[str, Any]]:
        """生成错题复习策略"""
        recommendations = []
        
        if not profile.error_patterns:
            return recommendations
        
        # 找出最常见的错误类型
        most_common_error = max(profile.error_patterns.keys(), 
                              key=lambda k: profile.error_patterns[k])
        error_count = profile.error_patterns[most_common_error]
        
        error_strategies = {
            "calculation": {
                "title": "计算错误专项训练",
                "content": "计算错误较多，建议加强基础运算练习和细心度培养。",
                "actions": ["每天练习口算10分钟", "检查计算步骤的习惯", "使用草稿纸规范计算"]
            },
            "comprehension": {
                "title": "理解能力提升训练",
                "content": "理解错误较多，建议加强阅读理解和审题能力。",
                "actions": ["仔细阅读题目2-3遍", "用自己的话重述题意", "画图或列表分析题目"]
            },
            "knowledge": {
                "title": "基础知识强化复习",
                "content": "知识点掌握不牢固，建议系统复习基础知识。",
                "actions": ["制作知识点思维导图", "定期回顾已学内容", "建立知识点关联网络"]
            },
            "careless": {
                "title": "细心度专项训练",
                "content": "粗心错误较多，建议培养仔细检查的好习惯。",
                "actions": ["做题后必须检查一遍", "标注容易出错的地方", "放慢做题速度保证质量"]
            },
            "method": {
                "title": "解题方法优化训练",
                "content": "方法选择有误，建议学习更多解题技巧和策略。",
                "actions": ["总结每种题型的解题方法", "多种方法解同一题目", "向老师请教最优解法"]
            }
        }
        
        if error_count >= 3:
            strategy = error_strategies.get(most_common_error, {
                "title": "错误类型专项改进",
                "content": "针对主要错误类型进行专项训练。",
                "actions": ["分析错误原因", "针对性练习", "定期自我检测"]
            })
            
            recommendations.append({
                "type": "错题复习",
                "priority": "high",
                "icon": "🔄",
                "title": strategy["title"],
                "content": f"最近{most_common_error}类错误出现{error_count}次。{strategy['content']}",
                "action_items": strategy["actions"],
                "estimated_improvement": 18
            })
        
        # 错题复习计划建议
        total_errors = sum(profile.error_patterns.values())
        if total_errors >= 5:
            recommendations.append({
                "type": "错题复习",
                "priority": "medium",
                "icon": "📖",
                "title": "错题本系统管理",
                "content": f"累计错题{total_errors}道，建议建立系统的错题管理和复习计划。",
                "action_items": [
                    "建立电子或纸质错题本",
                    "每周复习一次所有错题",
                    "掌握后的错题及时归档"
                ],
                "estimated_improvement": 12
            })
        
        return recommendations
    
    def _generate_time_management_recommendations(self, profile: StudentProfile) -> List[Dict[str, Any]]:
        """生成时间管理建议"""
        recommendations = []
        
        # 基于年级给出时间管理建议
        grade_difficulty = self.grade_difficulty.get(profile.grade, 2.0)
        
        if grade_difficulty <= 2.0:  # 小学阶段
            if profile.total_homework < 10:
                recommendations.append({
                    "type": "时间管理",
                    "priority": "medium",
                    "icon": "⏰",
                    "title": "建立学习时间概念",
                    "content": "小学阶段是培养学习习惯的关键期，建议设定固定的学习时间。",
                    "action_items": [
                        "每天安排30-45分钟学习时间",
                        "使用计时器帮助时间管理",
                        "学习完成后给予适当奖励"
                    ],
                    "estimated_improvement": 10
                })
        else:  # 中学阶段
            if profile.study_frequency < 4:
                recommendations.append({
                    "type": "时间管理",
                    "priority": "high",
                    "icon": "📊",
                    "title": "优化学习时间分配",
                    "content": "中学学习任务较重，需要更科学的时间管理策略。",
                    "action_items": [
                        "制定详细的每周学习计划",
                        "按学科重要程度分配时间",
                        "预留复习和总结时间"
                    ],
                    "estimated_improvement": 15
                })
        
        return recommendations
    
    def _get_fallback_recommendations(self) -> List[Dict[str, Any]]:
        """获取默认建议（当AI分析失败时使用）"""
        return [
            {
                "type": "基础建议",
                "priority": "medium",
                "icon": "💪",
                "title": "保持学习积极性",
                "content": "学习是一个持续的过程，保持积极的学习态度最重要。",
                "action_items": [
                    "制定合理的学习目标",
                    "庆祝每一个小进步",
                    "遇到困难时及时寻求帮助"
                ],
                "estimated_improvement": 10
            },
            {
                "type": "基础建议", 
                "priority": "medium",
                "icon": "🎯",
                "title": "培养良好学习习惯",
                "content": "良好的学习习惯是成功的基础，建议从规律作息开始。",
                "action_items": [
                    "每天固定时间学习",
                    "保持学习环境整洁",
                    "及时复习当天所学内容"
                ],
                "estimated_improvement": 8
            }
        ]