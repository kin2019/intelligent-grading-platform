"""
题目配置服务
负责管理题目生成配置、验证参数、模板管理等
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.user import User
from app.models.exercise import ExerciseTemplate, ExerciseGeneration


class ExerciseConfigService:
    """题目配置管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # 支持的学科列表
        self.supported_subjects = [
            '数学', '语文', '英语', '物理', '化学', 
            '生物', '历史', '地理', '政治', '科学'
        ]
        
        # 支持的年级列表
        self.supported_grades = [
            '一年级', '二年级', '三年级', '四年级', '五年级', '六年级',
            '七年级', '八年级', '九年级', '高一', '高二', '高三'
        ]
        
        # 难度等级配置
        self.difficulty_levels = {
            'easier': {
                'name': '简单',
                'description': '适合基础较弱的学生，题目难度降低',
                'coefficient': 0.7
            },
            'same': {
                'name': '相同',
                'description': '与原题难度相同',
                'coefficient': 1.0
            },
            'harder': {
                'name': '困难',
                'description': '适合基础较好的学生，题目难度提升',
                'coefficient': 1.3
            },
            'mixed': {
                'name': '混合',
                'description': '包含不同难度的题目',
                'coefficient': 'variable'
            }
        }
        
        # 题目类型配置
        self.question_types = {
            'similar': {
                'name': '相似题目',
                'description': '与原题结构相似的练习题',
                'weight': 0.5
            },
            'extended': {
                'name': '拓展变式',
                'description': '在原题基础上的变式和扩展',
                'weight': 0.3
            },
            'comprehensive': {
                'name': '综合应用',
                'description': '结合多个知识点的综合题',
                'weight': 0.2
            },
            'mixed': {
                'name': '混合类型',
                'description': '包含多种类型的题目',
                'weight': 'variable'
            }
        }
        
        # 年级-学科默认配置
        self.default_configs = self._init_default_configs()
    
    def validate_generation_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证题目生成配置
        
        Args:
            config: 生成配置参数
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 验证必需参数
        required_fields = ['subject', 'grade', 'question_count']
        for field in required_fields:
            if field not in config:
                errors.append(f'缺少必需参数: {field}')
            elif not config[field]:
                errors.append(f'参数不能为空: {field}')
        
        # 验证学科
        if 'subject' in config and config['subject'] not in self.supported_subjects:
            errors.append(f'不支持的学科: {config["subject"]}')
        
        # 验证年级
        if 'grade' in config and config['grade'] not in self.supported_grades:
            errors.append(f'不支持的年级: {config["grade"]}')
        
        # 验证题目数量
        if 'question_count' in config:
            try:
                count = int(config['question_count'])
                if count < 1 or count > 50:
                    errors.append('题目数量必须在1-50之间')
            except (ValueError, TypeError):
                errors.append('题目数量必须是有效数字')
        
        # 验证难度等级
        if 'difficulty_level' in config:
            if config['difficulty_level'] not in self.difficulty_levels:
                errors.append(f'不支持的难度等级: {config["difficulty_level"]}')
        
        # 验证题目类型
        if 'question_types' in config:
            if isinstance(config['question_types'], list):
                for qtype in config['question_types']:
                    if qtype not in self.question_types:
                        errors.append(f'不支持的题目类型: {qtype}')
            elif isinstance(config['question_types'], str):
                if config['question_types'] not in self.question_types:
                    errors.append(f'不支持的题目类型: {config["question_types"]}')
        
        return len(errors) == 0, errors
    
    def get_generation_config(self, user_id: int, subject: str, grade: str, 
                            custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取题目生成配置
        
        Args:
            user_id: 用户ID
            subject: 学科
            grade: 年级
            custom_config: 自定义配置
            
        Returns:
            完整的生成配置
        """
        try:
            # 获取用户信息
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f'用户不存在: {user_id}')
            
            # 获取默认配置
            default_config = self.get_default_config(subject, grade)
            
            # 合并自定义配置
            if custom_config:
                config = {**default_config, **custom_config}
            else:
                config = default_config.copy()
            
            # 根据用户特征调整配置
            config = self._adjust_config_for_user(config, user)
            
            # 验证最终配置
            is_valid, errors = self.validate_generation_config(config)
            if not is_valid:
                raise ValueError(f'配置验证失败: {", ".join(errors)}')
            
            return config
            
        except Exception as e:
            print(f'获取生成配置失败: {e}')
            # 返回基本配置作为后备
            return self.get_fallback_config(subject, grade)
    
    def get_default_config(self, subject: str, grade: str) -> Dict[str, Any]:
        """获取指定学科和年级的默认配置"""
        config_key = f'{grade}_{subject}'
        return self.default_configs.get(config_key, self._get_basic_config(subject, grade))
    
    def get_fallback_config(self, subject: str, grade: str) -> Dict[str, Any]:
        """获取后备配置（当其他配置获取失败时使用）"""
        return {
            'subject': subject,
            'grade': grade,
            'question_count': 5,
            'difficulty_level': 'same',
            'question_types': ['similar'],
            'include_answers': True,
            'include_analysis': True,
            'generation_source': 'ai',
            'timeout': 30
        }
    
    def get_subject_config(self, subject: str) -> Dict[str, Any]:
        """获取学科特定配置"""
        subject_configs = {
            '数学': {
                'default_question_types': ['calculation', 'word_problem', 'geometry'],
                'difficulty_adjustment': 0.1,
                'estimated_time_per_question': 3,
                'preferred_formats': ['选择题', '填空题', '计算题', '应用题']
            },
            '语文': {
                'default_question_types': ['reading', 'grammar', 'writing'],
                'difficulty_adjustment': 0.05,
                'estimated_time_per_question': 5,
                'preferred_formats': ['选择题', '填空题', '阅读理解', '作文题']
            },
            '英语': {
                'default_question_types': ['grammar', 'vocabulary', 'reading'],
                'difficulty_adjustment': 0.08,
                'estimated_time_per_question': 4,
                'preferred_formats': ['选择题', '填空题', '翻译题', '作文题']
            }
        }
        
        return subject_configs.get(subject, {
            'default_question_types': ['general'],
            'difficulty_adjustment': 0.1,
            'estimated_time_per_question': 4,
            'preferred_formats': ['选择题', '简答题']
        })
    
    def get_grade_config(self, grade: str) -> Dict[str, Any]:
        """获取年级特定配置"""
        # 将年级映射到配置级别
        grade_levels = {
            '一年级': 1, '二年级': 2, '三年级': 3,
            '四年级': 4, '五年级': 5, '六年级': 6,
            '七年级': 7, '八年级': 8, '九年级': 9,
            '高一': 10, '高二': 11, '高三': 12
        }
        
        level = grade_levels.get(grade, 6)  # 默认为6年级水平
        
        if level <= 3:  # 低年级
            return {
                'max_question_count': 10,
                'default_difficulty': 'easier',
                'include_pictures': True,
                'font_size': 'large',
                'complexity_limit': 'low'
            }
        elif level <= 6:  # 中年级
            return {
                'max_question_count': 15,
                'default_difficulty': 'same',
                'include_pictures': False,
                'font_size': 'medium',
                'complexity_limit': 'medium'
            }
        elif level <= 9:  # 初中
            return {
                'max_question_count': 20,
                'default_difficulty': 'same',
                'include_pictures': False,
                'font_size': 'medium',
                'complexity_limit': 'medium'
            }
        else:  # 高中
            return {
                'max_question_count': 25,
                'default_difficulty': 'harder',
                'include_pictures': False,
                'font_size': 'small',
                'complexity_limit': 'high'
            }
    
    def create_template(self, template_data: Dict[str, Any], created_by: int) -> ExerciseTemplate:
        """
        创建题目模板
        
        Args:
            template_data: 模板数据
            created_by: 创建者ID
            
        Returns:
            创建的模板对象
        """
        try:
            # 验证必需字段
            required_fields = ['name', 'subject', 'grade_range', 'topic', 'template_content']
            for field in required_fields:
                if field not in template_data or not template_data[field]:
                    raise ValueError(f'缺少必需字段: {field}')
            
            # 创建模板对象
            template = ExerciseTemplate(
                name=template_data['name'],
                subject=template_data['subject'],
                grade_range=template_data['grade_range'],
                topic=template_data['topic'],
                template_content=template_data['template_content'],
                answer_pattern=template_data.get('answer_pattern'),
                difficulty_level=template_data.get('difficulty_level', 'same'),
                question_type=template_data.get('question_type', 'similar'),
                estimated_time=template_data.get('estimated_time'),
                is_active=template_data.get('is_active', True),
                is_public=template_data.get('is_public', False),
                created_by=created_by
            )
            
            # 设置变化参数
            if 'variations' in template_data:
                template.set_variations(template_data['variations'])
            
            # 保存到数据库
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            
            return template
            
        except Exception as e:
            self.db.rollback()
            print(f'创建模板失败: {e}')
            raise
    
    def get_templates(self, subject: Optional[str] = None, grade: Optional[str] = None,
                     is_active: bool = True, limit: int = 20) -> List[ExerciseTemplate]:
        """获取题目模板列表"""
        try:
            query = self.db.query(ExerciseTemplate).filter(
                ExerciseTemplate.is_active == is_active
            )
            
            if subject:
                query = query.filter(ExerciseTemplate.subject == subject)
            
            if grade:
                # 检查年级是否在适用范围内
                query = query.filter(
                    or_(
                        ExerciseTemplate.grade_range.contains(grade),
                        ExerciseTemplate.grade_range == '通用'
                    )
                )
            
            # 按使用次数和成功率排序
            query = query.order_by(
                desc(ExerciseTemplate.success_rate),
                desc(ExerciseTemplate.usage_count)
            ).limit(limit)
            
            return query.all()
            
        except Exception as e:
            print(f'获取模板列表失败: {e}')
            return []
    
    def update_template_stats(self, template_id: int, success: bool, quality_score: Optional[float] = None):
        """更新模板使用统计"""
        try:
            template = self.db.query(ExerciseTemplate).filter(
                ExerciseTemplate.id == template_id
            ).first()
            
            if template:
                template.usage_count += 1
                
                if success:
                    # 更新成功率
                    if template.usage_count == 1:
                        template.success_rate = 1.0
                    else:
                        # 计算新的成功率
                        old_successes = template.success_rate * (template.usage_count - 1)
                        new_successes = old_successes + 1
                        template.success_rate = new_successes / template.usage_count
                else:
                    # 更新成功率（失败情况）
                    if template.usage_count > 1:
                        old_successes = template.success_rate * (template.usage_count - 1)
                        template.success_rate = old_successes / template.usage_count
                
                # 更新平均质量评分
                if quality_score is not None:
                    if template.avg_quality_score is None:
                        template.avg_quality_score = quality_score
                    else:
                        # 计算移动平均
                        template.avg_quality_score = (
                            template.avg_quality_score * 0.8 + quality_score * 0.2
                        )
                
                self.db.commit()
                
        except Exception as e:
            self.db.rollback()
            print(f'更新模板统计失败: {e}')
    
    def get_generation_history(self, user_id: int, limit: int = 10) -> List[ExerciseGeneration]:
        """获取用户的题目生成历史"""
        try:
            return self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.user_id == user_id,
                ExerciseGeneration.is_active == True
            ).order_by(
                desc(ExerciseGeneration.created_at)
            ).limit(limit).all()
            
        except Exception as e:
            print(f'获取生成历史失败: {e}')
            return []
    
    def _adjust_config_for_user(self, config: Dict[str, Any], user: User) -> Dict[str, Any]:
        """根据用户特征调整配置"""
        # 根据用户VIP状态调整
        if hasattr(user, 'is_vip') and user.is_vip:
            config['max_question_count'] = 50
            config['priority'] = 'high'
        else:
            config['max_question_count'] = 20
            config['priority'] = 'normal'
        
        # 根据用户年级调整
        if hasattr(user, 'grade') and user.grade:
            grade_config = self.get_grade_config(user.grade)
            config.update(grade_config)
        
        return config
    
    def _init_default_configs(self) -> Dict[str, Dict[str, Any]]:
        """初始化默认配置"""
        configs = {}
        
        # 为每个年级和学科组合创建默认配置
        for grade in self.supported_grades:
            for subject in self.supported_subjects:
                key = f'{grade}_{subject}'
                configs[key] = self._get_basic_config(subject, grade)
        
        return configs
    
    def _get_basic_config(self, subject: str, grade: str) -> Dict[str, Any]:
        """获取基本配置"""
        subject_config = self.get_subject_config(subject)
        grade_config = self.get_grade_config(grade)
        
        return {
            'subject': subject,
            'grade': grade,
            'question_count': min(10, grade_config.get('max_question_count', 10)),
            'difficulty_level': grade_config.get('default_difficulty', 'same'),
            'question_types': subject_config.get('default_question_types', ['similar']),
            'include_answers': True,
            'include_analysis': True,
            'estimated_time': subject_config.get('estimated_time_per_question', 4),
            'generation_source': 'ai',
            'timeout': 30
        }


class ExerciseConfigValidator:
    """题目配置验证器"""
    
    @staticmethod
    def validate_config_format(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证配置格式"""
        errors = []
        
        # 验证数据类型
        type_checks = {
            'question_count': int,
            'include_answers': bool,
            'include_analysis': bool,
            'timeout': (int, float)
        }
        
        for field, expected_type in type_checks.items():
            if field in config:
                if not isinstance(config[field], expected_type):
                    errors.append(f'{field} 类型错误，期望 {expected_type}')
        
        # 验证取值范围
        range_checks = {
            'question_count': (1, 50),
            'timeout': (5, 300)
        }
        
        for field, (min_val, max_val) in range_checks.items():
            if field in config:
                try:
                    val = float(config[field])
                    if not (min_val <= val <= max_val):
                        errors.append(f'{field} 取值应在 {min_val}-{max_val} 之间')
                except (ValueError, TypeError):
                    errors.append(f'{field} 不是有效数值')
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_template_content(template_content: str) -> Tuple[bool, List[str]]:
        """验证模板内容格式"""
        errors = []
        
        if not template_content or not template_content.strip():
            errors.append('模板内容不能为空')
            return False, errors
        
        # 检查基本格式
        if len(template_content.strip()) < 10:
            errors.append('模板内容过短')
        
        if len(template_content) > 2000:
            errors.append('模板内容过长（超过2000字符）')
        
        # 检查是否包含变量占位符
        if '{{' not in template_content or '}}' not in template_content:
            errors.append('模板内容应包含变量占位符 {{变量名}}')
        
        return len(errors) == 0, errors