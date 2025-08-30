"""
题目管理服务
负责管理题目生成记录、查询历史、统计分析等
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, extract

from app.models.user import User
from app.models.exercise import (
    ExerciseGeneration, GeneratedExercise, ExerciseTemplate,
    ExerciseDownload, ExerciseUsageStats
)


class ExerciseManagementService:
    """题目管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_generation_record(self, user_id: int, generation_config: Dict[str, Any]) -> ExerciseGeneration:
        """
        创建题目生成记录
        
        Args:
            user_id: 用户ID
            generation_config: 生成配置
            
        Returns:
            创建的生成记录
        """
        try:
            # 验证用户是否存在
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"用户不存在: {user_id}")
            
            # 创建生成记录
            generation = ExerciseGeneration(
                user_id=user_id,
                subject=generation_config.get('subject', '未知'),
                grade=generation_config.get('grade', '未知'),
                title=generation_config.get('title', f"{generation_config.get('subject', '未知')}练习题"),
                description=generation_config.get('description'),
                question_count=generation_config.get('question_count', 5),
                difficulty_level=generation_config.get('difficulty_level', 'same'),
                status='pending'
            )
            
            # 设置生成配置
            generation.set_config(generation_config)
            
            # 保存到数据库
            self.db.add(generation)
            self.db.commit()
            self.db.refresh(generation)
            
            return generation
            
        except Exception as e:
            self.db.rollback()
            print(f"创建生成记录失败: {e}")
            raise
    
    def start_generation(self, generation_id: int) -> bool:
        """
        开始题目生成
        
        Args:
            generation_id: 生成记录ID
            
        Returns:
            是否成功开始
        """
        try:
            generation = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.id == generation_id
            ).first()
            
            if not generation:
                return False
            
            if generation.status != 'pending':
                return False
            
            generation.status = 'generating'
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"开始生成失败: {e}")
            return False
    
    def complete_generation(self, generation_id: int, exercises: List[Dict[str, Any]], 
                          generation_time: float) -> bool:
        """
        完成题目生成
        
        Args:
            generation_id: 生成记录ID
            exercises: 生成的题目列表
            generation_time: 生成耗时
            
        Returns:
            是否成功完成
        """
        try:
            generation = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.id == generation_id
            ).first()
            
            if not generation:
                return False
            
            # 保存生成的题目
            for exercise_data in exercises:
                exercise = GeneratedExercise(
                    generation_id=generation_id,
                    number=exercise_data.get('number', 1),
                    subject=exercise_data.get('subject', generation.subject),
                    question_text=exercise_data.get('question_text', ''),
                    question_type=exercise_data.get('question_type', 'similar'),
                    correct_answer=exercise_data.get('correct_answer', ''),
                    analysis=exercise_data.get('analysis', ''),
                    difficulty=exercise_data.get('difficulty', generation.difficulty_level),
                    generation_source='ai'
                )
                
                # 设置知识点
                if 'knowledge_points' in exercise_data:
                    exercise.set_knowledge_points(exercise_data['knowledge_points'])
                
                self.db.add(exercise)
            
            # 更新生成记录状态
            generation.mark_completed(len(exercises), generation_time)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"完成生成失败: {e}")
            return False
    
    def fail_generation(self, generation_id: int, error_message: str) -> bool:
        """
        标记生成失败
        
        Args:
            generation_id: 生成记录ID
            error_message: 错误信息
            
        Returns:
            是否成功标记
        """
        try:
            generation = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.id == generation_id
            ).first()
            
            if not generation:
                return False
            
            generation.mark_failed(error_message)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"标记失败状态失败: {e}")
            return False
    
    def get_generation_info(self, generation_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """获取生成记录信息"""
        try:
            generation = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.id == generation_id,
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            ).first()
            
            if not generation:
                return None
            
            # 获取题目数量
            exercise_count = self.db.query(GeneratedExercise).filter(
                GeneratedExercise.generation_id == generation_id
            ).count()
            
            return {
                'id': generation.id,
                'subject': generation.subject,
                'grade': generation.grade,
                'title': generation.title,
                'description': generation.description,
                'question_count': generation.question_count,
                'difficulty_level': generation.difficulty_level,
                'status': generation.status,
                'total_questions': exercise_count,
                'generation_time': generation.generation_time,
                'progress_percent': generation.progress_percent,
                'view_count': generation.view_count,
                'download_count': generation.download_count,
                'share_count': generation.share_count,
                'is_favorite': generation.is_favorite,
                'created_at': generation.created_at.isoformat(),
                'generated_at': generation.generated_at.isoformat() if generation.generated_at else None,
                'error_message': generation.error_message,
                'config': generation.config_dict
            }
            
        except Exception as e:
            print(f"获取生成信息失败: {e}")
            return None
    
    def get_user_generations(self, user_id: int, filters: Optional[Dict[str, Any]] = None,
                           limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        获取用户的题目生成记录列表
        
        Args:
            user_id: 用户ID
            filters: 过滤条件
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            生成记录列表和统计信息
        """
        try:
            query = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            )
            
            # 应用过滤条件
            if filters:
                if 'subject' in filters:
                    query = query.filter(ExerciseGeneration.subject == filters['subject'])
                
                if 'grade' in filters:
                    query = query.filter(ExerciseGeneration.grade == filters['grade'])
                
                if 'status' in filters:
                    query = query.filter(ExerciseGeneration.status == filters['status'])
                
                if 'difficulty_level' in filters:
                    query = query.filter(ExerciseGeneration.difficulty_level == filters['difficulty_level'])
                
                if 'date_from' in filters:
                    try:
                        date_from = datetime.fromisoformat(filters['date_from'])
                        query = query.filter(ExerciseGeneration.created_at >= date_from)
                    except ValueError:
                        pass
                
                if 'date_to' in filters:
                    try:
                        date_to = datetime.fromisoformat(filters['date_to'])
                        query = query.filter(ExerciseGeneration.created_at <= date_to)
                    except ValueError:
                        pass
                
                if 'is_favorite' in filters:
                    query = query.filter(ExerciseGeneration.is_favorite == filters['is_favorite'])
            
            # 获取总数
            total_count = query.count()
            
            # 获取记录列表
            generations = query.order_by(
                desc(ExerciseGeneration.created_at)
            ).offset(offset).limit(limit).all()
            
            # 构建结果列表
            records = []
            for gen in generations:
                records.append({
                    'id': gen.id,
                    'subject': gen.subject,
                    'grade': gen.grade,
                    'title': gen.title,
                    'question_count': gen.question_count,
                    'difficulty_level': gen.difficulty_level,
                    'status': gen.status,
                    'total_questions': gen.total_questions,
                    'progress_percent': gen.progress_percent,
                    'view_count': gen.view_count,
                    'download_count': gen.download_count,
                    'share_count': gen.share_count,
                    'is_favorite': gen.is_favorite,
                    'created_at': gen.created_at.isoformat(),
                    'generated_at': gen.generated_at.isoformat() if gen.generated_at else None
                })
            
            return {
                'records': records,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                }
            }
            
        except Exception as e:
            print(f"获取用户生成记录失败: {e}")
            return {'records': [], 'pagination': {'total_count': 0, 'limit': limit, 'offset': offset, 'has_more': False}}
    
    def get_exercises(self, generation_id: int, user_id: int) -> List[Dict[str, Any]]:
        """获取题目列表"""
        try:
            # 验证用户权限
            generation = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.id == generation_id,
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            ).first()
            
            if not generation:
                return []
            
            exercises = self.db.query(GeneratedExercise).filter(
                GeneratedExercise.generation_id == generation_id
            ).order_by(GeneratedExercise.number).all()
            
            result = []
            for exercise in exercises:
                result.append({
                    'id': exercise.id,
                    'number': exercise.number,
                    'subject': exercise.subject,
                    'question_text': exercise.question_text,
                    'question_type': exercise.question_type,
                    'correct_answer': exercise.correct_answer,
                    'analysis': exercise.analysis,
                    'difficulty': exercise.difficulty,
                    'knowledge_points': exercise.knowledge_points_list,
                    'estimated_time': exercise.estimated_time,
                    'quality_score': exercise.quality_score,
                    'view_count': exercise.view_count,
                    'created_at': exercise.created_at.isoformat()
                })
            
            # 更新查看次数
            generation.view_count += 1
            self.db.commit()
            
            return result
            
        except Exception as e:
            print(f"获取题目列表失败: {e}")
            return []
    
    def update_favorite_status(self, generation_id: int, user_id: int, is_favorite: bool) -> bool:
        """更新收藏状态"""
        try:
            generation = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.id == generation_id,
                ExerciseGeneration.user_id == user_id
            ).first()
            
            if not generation:
                return False
            
            generation.is_favorite = is_favorite
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"更新收藏状态失败: {e}")
            return False
    
    def delete_generation(self, generation_id: int, user_id: int) -> bool:
        """删除题目生成记录（软删除）"""
        try:
            generation = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.id == generation_id,
                ExerciseGeneration.user_id == user_id
            ).first()
            
            if not generation:
                return False
            
            generation.is_active = False
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"删除生成记录失败: {e}")
            return False
    
    def get_user_statistics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 基础统计
            total_generations = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            ).count()
            
            completed_generations = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.status == 'completed',
                ExerciseGeneration.is_active == True
            ).count()
            
            recent_generations = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.created_at >= start_date,
                ExerciseGeneration.is_active == True
            ).count()
            
            # 题目数量统计
            total_questions = self.db.query(func.sum(ExerciseGeneration.total_questions)).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.status == 'completed',
                ExerciseGeneration.is_active == True
            ).scalar() or 0
            
            # 学科统计
            subject_stats = self.db.query(
                ExerciseGeneration.subject,
                func.count(ExerciseGeneration.id).label('count')
            ).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            ).group_by(ExerciseGeneration.subject).all()
            
            # 难度统计
            difficulty_stats = self.db.query(
                ExerciseGeneration.difficulty_level,
                func.count(ExerciseGeneration.id).label('count')
            ).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            ).group_by(ExerciseGeneration.difficulty_level).all()
            
            # 下载和分享统计
            total_downloads = self.db.query(func.sum(ExerciseGeneration.download_count)).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            ).scalar() or 0
            
            total_shares = self.db.query(func.sum(ExerciseGeneration.share_count)).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            ).scalar() or 0
            
            # 计算成功率
            success_rate = (completed_generations / total_generations * 100) if total_generations > 0 else 0
            
            # 平均生成时间
            avg_generation_time = self.db.query(func.avg(ExerciseGeneration.generation_time)).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.status == 'completed',
                ExerciseGeneration.generation_time.isnot(None)
            ).scalar() or 0
            
            return {
                'summary': {
                    'total_generations': total_generations,
                    'completed_generations': completed_generations,
                    'recent_generations': recent_generations,
                    'total_questions': total_questions,
                    'success_rate': round(success_rate, 2),
                    'avg_generation_time': round(avg_generation_time, 2),
                    'total_downloads': total_downloads,
                    'total_shares': total_shares
                },
                'subject_distribution': [
                    {'subject': stat[0], 'count': stat[1]}
                    for stat in subject_stats
                ],
                'difficulty_distribution': [
                    {'difficulty': stat[0], 'count': stat[1]}
                    for stat in difficulty_stats
                ],
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                }
            }
            
        except Exception as e:
            print(f"获取用户统计失败: {e}")
            return {
                'summary': {},
                'subject_distribution': [],
                'difficulty_distribution': [],
                'date_range': {}
            }
    
    def get_daily_activity(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """获取每日活动统计"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            # 获取每日生成统计
            daily_stats = self.db.query(
                func.date(ExerciseGeneration.created_at).label('date'),
                func.count(ExerciseGeneration.id).label('generation_count'),
                func.sum(ExerciseGeneration.total_questions).label('question_count')
            ).filter(
                ExerciseGeneration.user_id == user_id,
                func.date(ExerciseGeneration.created_at) >= start_date,
                ExerciseGeneration.is_active == True
            ).group_by(
                func.date(ExerciseGeneration.created_at)
            ).all()
            
            # 创建完整的日期序列
            result = []
            current_date = start_date
            stats_dict = {stat[0]: {'generation_count': stat[1], 'question_count': stat[2] or 0} 
                         for stat in daily_stats}
            
            while current_date <= end_date:
                date_str = current_date.isoformat()
                stats = stats_dict.get(current_date, {'generation_count': 0, 'question_count': 0})
                
                result.append({
                    'date': date_str,
                    'generation_count': stats['generation_count'],
                    'question_count': stats['question_count']
                })
                
                current_date += timedelta(days=1)
            
            return result
            
        except Exception as e:
            print(f"获取每日活动统计失败: {e}")
            return []
    
    def cleanup_old_records(self, days: int = 90) -> int:
        """清理旧的记录（可选功能）"""
        try:
            # 这里可以实现清理逻辑，比如删除90天以前的失败记录
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 只清理失败的记录
            old_records = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.created_at < cutoff_date,
                ExerciseGeneration.status == 'failed',
                ExerciseGeneration.is_active == True
            ).all()
            
            count = 0
            for record in old_records:
                record.is_active = False
                count += 1
            
            if count > 0:
                self.db.commit()
            
            return count
            
        except Exception as e:
            self.db.rollback()
            print(f"清理旧记录失败: {e}")
            return 0


class ExerciseAnalyticsService:
    """题目分析服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_user_preference(self, user_id: int) -> Dict[str, Any]:
        """分析用户偏好"""
        try:
            # 最常用的学科
            favorite_subjects = self.db.query(
                ExerciseGeneration.subject,
                func.count(ExerciseGeneration.id).label('count')
            ).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            ).group_by(
                ExerciseGeneration.subject
            ).order_by(desc('count')).limit(3).all()
            
            # 最常用的难度
            favorite_difficulties = self.db.query(
                ExerciseGeneration.difficulty_level,
                func.count(ExerciseGeneration.id).label('count')
            ).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            ).group_by(
                ExerciseGeneration.difficulty_level
            ).order_by(desc('count')).limit(3).all()
            
            # 平均题目数量
            avg_question_count = self.db.query(
                func.avg(ExerciseGeneration.question_count)
            ).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            ).scalar() or 0
            
            # 活跃时段分析
            hourly_stats = self.db.query(
                extract('hour', ExerciseGeneration.created_at).label('hour'),
                func.count(ExerciseGeneration.id).label('count')
            ).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            ).group_by(
                extract('hour', ExerciseGeneration.created_at)
            ).order_by(desc('count')).limit(3).all()
            
            return {
                'favorite_subjects': [
                    {'subject': s[0], 'count': s[1], 'percentage': 0}
                    for s in favorite_subjects
                ],
                'favorite_difficulties': [
                    {'difficulty': d[0], 'count': d[1], 'percentage': 0}
                    for d in favorite_difficulties
                ],
                'avg_question_count': round(avg_question_count, 1),
                'active_hours': [
                    {'hour': int(h[0]), 'count': h[1]}
                    for h in hourly_stats
                ]
            }
            
        except Exception as e:
            print(f"分析用户偏好失败: {e}")
            return {
                'favorite_subjects': [],
                'favorite_difficulties': [],
                'avg_question_count': 0,
                'active_hours': []
            }
    
    def get_recommendation(self, user_id: int) -> Dict[str, Any]:
        """获取推荐配置"""
        try:
            # 基于用户历史生成推荐
            preference = self.analyze_user_preference(user_id)
            
            recommendations = {
                'subjects': [],
                'difficulty_levels': [],
                'question_counts': [],
                'optimal_time': None
            }
            
            # 推荐学科
            if preference['favorite_subjects']:
                recommendations['subjects'] = [s['subject'] for s in preference['favorite_subjects'][:2]]
            
            # 推荐难度
            if preference['favorite_difficulties']:
                recommendations['difficulty_levels'] = [d['difficulty'] for d in preference['favorite_difficulties'][:2]]
            
            # 推荐题目数量
            avg_count = preference['avg_question_count']
            if avg_count > 0:
                recommendations['question_counts'] = [
                    int(avg_count),
                    max(3, int(avg_count) - 2),
                    min(20, int(avg_count) + 3)
                ]
            
            # 推荐最佳时间
            if preference['active_hours']:
                recommendations['optimal_time'] = f"{preference['active_hours'][0]['hour']:02d}:00"
            
            return recommendations
            
        except Exception as e:
            print(f"获取推荐失败: {e}")
            return {
                'subjects': [],
                'difficulty_levels': [],
                'question_counts': [],
                'optimal_time': None
            }