"""
题目导出服务
负责将生成的题目导出为各种格式（Word/PDF/Text）
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.exercise import ExerciseGeneration, GeneratedExercise, ExerciseDownload
from app.models.user import User


class ExerciseExportService:
    """题目导出服务"""
    
    def __init__(self, db: Session, export_dir: str = "exports"):
        self.db = db
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
        
        # 支持的导出格式
        self.supported_formats = {
            'word': {
                'extension': '.docx',
                'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'description': 'Microsoft Word文档'
            },
            'pdf': {
                'extension': '.pdf',
                'mime_type': 'application/pdf',
                'description': 'PDF文档'
            },
            'text': {
                'extension': '.txt',
                'mime_type': 'text/plain',
                'description': '纯文本文件'
            }
        }
    
    def export_exercises(self, generation_id: int, user_id: int, 
                        export_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        导出题目集
        
        Args:
            generation_id: 生成记录ID
            user_id: 用户ID
            export_config: 导出配置
            
        Returns:
            导出结果信息
        """
        try:
            # 获取生成记录
            generation = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.id == generation_id,
                ExerciseGeneration.user_id == user_id
            ).first()
            
            if not generation:
                raise ValueError(f"生成记录不存在: {generation_id}")
            
            if generation.status != "completed":
                raise ValueError(f"题目生成尚未完成: {generation.status}")
            
            # 获取题目列表
            exercises = self.db.query(GeneratedExercise).filter(
                GeneratedExercise.generation_id == generation_id
            ).order_by(GeneratedExercise.number).all()
            
            if not exercises:
                raise ValueError("没有找到生成的题目")
            
            # 验证导出配置
            format_type = export_config.get('format', 'word')
            if format_type not in self.supported_formats:
                raise ValueError(f"不支持的导出格式: {format_type}")
            
            # 创建下载记录
            download_record = self._create_download_record(
                generation_id, user_id, export_config
            )
            
            start_time = datetime.now()
            
            try:
                # 根据格式类型导出
                if format_type == 'word':
                    file_path, file_size = self._export_to_word(
                        generation, exercises, export_config, download_record.file_name
                    )
                elif format_type == 'pdf':
                    file_path, file_size = self._export_to_pdf(
                        generation, exercises, export_config, download_record.file_name
                    )
                else:  # text
                    file_path, file_size = self._export_to_text(
                        generation, exercises, export_config, download_record.file_name
                    )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # 生成下载URL（这里使用相对路径，实际部署时需要配置为完整URL）
                download_url = f"/api/v1/exercises/download/{download_record.id}"
                
                # 更新下载记录
                download_record.mark_completed(
                    file_path, file_size, download_url, processing_time
                )
                self.db.commit()
                
                # 更新生成记录的下载次数
                generation.download_count += 1
                self.db.commit()
                
                return {
                    'success': True,
                    'download_id': download_record.id,
                    'download_url': download_url,
                    'file_name': download_record.file_name,
                    'file_size': file_size,
                    'processing_time': processing_time,
                    'expires_at': download_record.expires_at.isoformat(),
                    'format': format_type
                }
                
            except Exception as e:
                # 标记下载失败
                download_record.mark_failed(str(e))
                self.db.commit()
                raise
                
        except Exception as e:
            print(f"导出题目失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_download_record(self, generation_id: int, user_id: int, 
                              export_config: Dict[str, Any]) -> ExerciseDownload:
        """创建下载记录"""
        format_type = export_config.get('format', 'word')
        extension = self.supported_formats[format_type]['extension']
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        file_name = f"exercises_{timestamp}_{unique_id}{extension}"
        
        download_record = ExerciseDownload(
            generation_id=generation_id,
            user_id=user_id,
            download_format=format_type,
            file_name=file_name,
            include_answers=export_config.get('include_answers', True),
            include_analysis=export_config.get('include_analysis', True),
            custom_header=export_config.get('custom_header'),
            paper_size=export_config.get('paper_size', 'A4'),
            status='processing'
        )
        
        self.db.add(download_record)
        self.db.commit()
        self.db.refresh(download_record)
        
        return download_record
    
    def _export_to_word(self, generation: ExerciseGeneration, 
                       exercises: List[GeneratedExercise],
                       export_config: Dict[str, Any], 
                       file_name: str) -> Tuple[str, int]:
        """导出为Word文档"""
        try:
            # 注意：这里使用简单的文本格式模拟Word导出
            # 实际项目中应该使用python-docx库来生成真正的Word文档
            
            file_path = self.export_dir / file_name
            content = self._generate_document_content(
                generation, exercises, export_config, 'word'
            )
            
            # 写入文件（以UTF-8编码）
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_size = os.path.getsize(file_path)
            return str(file_path), file_size
            
        except Exception as e:
            print(f"Word导出失败: {e}")
            raise Exception(f"Word文档导出失败: {e}")
    
    def _export_to_pdf(self, generation: ExerciseGeneration, 
                      exercises: List[GeneratedExercise],
                      export_config: Dict[str, Any], 
                      file_name: str) -> Tuple[str, int]:
        """导出为PDF文档"""
        try:
            # 注意：这里使用简单的文本格式模拟PDF导出
            # 实际项目中应该使用reportlab或其他PDF库来生成真正的PDF
            
            file_path = self.export_dir / file_name
            content = self._generate_document_content(
                generation, exercises, export_config, 'pdf'
            )
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_size = os.path.getsize(file_path)
            return str(file_path), file_size
            
        except Exception as e:
            print(f"PDF导出失败: {e}")
            raise Exception(f"PDF文档导出失败: {e}")
    
    def _export_to_text(self, generation: ExerciseGeneration, 
                       exercises: List[GeneratedExercise],
                       export_config: Dict[str, Any], 
                       file_name: str) -> Tuple[str, int]:
        """导出为文本文件"""
        try:
            file_path = self.export_dir / file_name
            content = self._generate_document_content(
                generation, exercises, export_config, 'text'
            )
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_size = os.path.getsize(file_path)
            return str(file_path), file_size
            
        except Exception as e:
            print(f"文本导出失败: {e}")
            raise Exception(f"文本文件导出失败: {e}")
    
    def _generate_document_content(self, generation: ExerciseGeneration,
                                 exercises: List[GeneratedExercise],
                                 export_config: Dict[str, Any],
                                 format_type: str) -> str:
        """生成文档内容"""
        lines = []
        
        # 文档标题和页眉
        custom_header = export_config.get('custom_header')
        if custom_header:
            lines.append(custom_header)
            lines.append("=" * 50)
        else:
            lines.append(f"{generation.subject} {generation.grade} 练习题")
            lines.append("=" * 50)
        
        lines.append("")
        lines.append(f"标题：{generation.title}")
        if generation.description:
            lines.append(f"说明：{generation.description}")
        lines.append(f"难度等级：{generation.difficulty_level}")
        lines.append(f"题目数量：{len(exercises)} 题")
        lines.append(f"生成时间：{generation.created_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        lines.append("-" * 50)
        lines.append("")
        
        # 题目内容
        for i, exercise in enumerate(exercises, 1):
            lines.append(f"【第 {i} 题】（{exercise.difficulty} - {exercise.question_type}）")
            lines.append("")
            lines.append(exercise.question_text)
            lines.append("")
            
            # 如果包含答案
            if export_config.get('include_answers', True) and exercise.correct_answer:
                lines.append(f"答案：{exercise.correct_answer}")
                lines.append("")
            
            # 如果包含解析
            if export_config.get('include_analysis', True) and exercise.analysis:
                lines.append(f"解析：{exercise.analysis}")
                lines.append("")
            
            # 知识点
            if exercise.knowledge_points_list:
                knowledge_points = "、".join(exercise.knowledge_points_list)
                lines.append(f"知识点：{knowledge_points}")
                lines.append("")
            
            lines.append("-" * 30)
            lines.append("")
        
        # 页脚信息
        lines.append("")
        lines.append("=" * 50)
        lines.append("本练习题由智能AI系统生成")
        lines.append(f"导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)
    
    def get_download_info(self, download_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """获取下载信息"""
        try:
            download = self.db.query(ExerciseDownload).filter(
                ExerciseDownload.id == download_id,
                ExerciseDownload.user_id == user_id
            ).first()
            
            if not download:
                return None
            
            return {
                'id': download.id,
                'status': download.status,
                'file_name': download.file_name,
                'download_url': download.download_url,
                'file_size': download.file_size,
                'download_format': download.download_format,
                'expires_at': download.expires_at.isoformat() if download.expires_at else None,
                'is_expired': download.is_expired,
                'created_at': download.created_at.isoformat(),
                'error_message': download.error_message
            }
            
        except Exception as e:
            print(f"获取下载信息失败: {e}")
            return None
    
    def get_file_path(self, download_id: int, user_id: int) -> Optional[str]:
        """获取文件路径（用于实际下载）"""
        try:
            download = self.db.query(ExerciseDownload).filter(
                ExerciseDownload.id == download_id,
                ExerciseDownload.user_id == user_id,
                ExerciseDownload.status == 'completed'
            ).first()
            
            if not download or download.is_expired:
                return None
            
            # 记录下载时间
            if not download.downloaded_at:
                download.downloaded_at = datetime.now()
                self.db.commit()
            
            return download.file_path
            
        except Exception as e:
            print(f"获取文件路径失败: {e}")
            return None
    
    def cleanup_expired_files(self) -> int:
        """清理过期的导出文件"""
        try:
            # 获取过期的下载记录
            expired_downloads = self.db.query(ExerciseDownload).filter(
                ExerciseDownload.expires_at < datetime.now(),
                ExerciseDownload.status == 'completed'
            ).all()
            
            cleaned_count = 0
            
            for download in expired_downloads:
                try:
                    # 删除文件
                    if download.file_path and os.path.exists(download.file_path):
                        os.remove(download.file_path)
                    
                    # 更新记录状态
                    download.status = 'expired'
                    cleaned_count += 1
                    
                except Exception as e:
                    print(f"清理文件失败 {download.file_path}: {e}")
            
            if cleaned_count > 0:
                self.db.commit()
            
            return cleaned_count
            
        except Exception as e:
            print(f"清理过期文件失败: {e}")
            return 0
    
    def get_user_downloads(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户的下载历史"""
        try:
            downloads = self.db.query(ExerciseDownload).filter(
                ExerciseDownload.user_id == user_id
            ).order_by(
                ExerciseDownload.created_at.desc()
            ).limit(limit).all()
            
            result = []
            for download in downloads:
                result.append({
                    'id': download.id,
                    'file_name': download.file_name,
                    'download_format': download.download_format,
                    'status': download.status,
                    'file_size': download.file_size,
                    'created_at': download.created_at.isoformat(),
                    'expires_at': download.expires_at.isoformat() if download.expires_at else None,
                    'is_expired': download.is_expired
                })
            
            return result
            
        except Exception as e:
            print(f"获取下载历史失败: {e}")
            return []


class WeChatExportService:
    """微信分享服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def format_for_wechat(self, generation_id: int, user_id: int,
                         share_config: Optional[Dict[str, Any]] = None) -> str:
        """
        格式化题目内容用于微信分享
        
        Args:
            generation_id: 生成记录ID
            user_id: 用户ID
            share_config: 分享配置
            
        Returns:
            格式化的文本内容
        """
        try:
            # 获取生成记录和题目
            generation = self.db.query(ExerciseGeneration).filter(
                ExerciseGeneration.id == generation_id,
                ExerciseGeneration.user_id == user_id
            ).first()
            
            if not generation:
                raise ValueError("生成记录不存在")
            
            exercises = self.db.query(GeneratedExercise).filter(
                GeneratedExercise.generation_id == generation_id
            ).order_by(GeneratedExercise.number).all()
            
            if not exercises:
                raise ValueError("没有找到题目")
            
            # 设置默认分享配置
            if not share_config:
                share_config = {
                    'include_answers': False,
                    'include_analysis': False,
                    'max_questions': 5
                }
            
            lines = []
            
            # 标题
            lines.append(f"📚 {generation.subject} {generation.grade} 练习题")
            lines.append(f"📝 {generation.title}")
            lines.append("")
            
            # 限制题目数量
            max_questions = share_config.get('max_questions', len(exercises))
            selected_exercises = exercises[:max_questions]
            
            # 题目内容
            for i, exercise in enumerate(selected_exercises, 1):
                lines.append(f"【题目 {i}】")
                lines.append(exercise.question_text)
                
                # 可选包含答案
                if share_config.get('include_answers', False) and exercise.correct_answer:
                    lines.append(f"💡 答案：{exercise.correct_answer}")
                
                lines.append("")
            
            # 如果有更多题目
            if len(exercises) > max_questions:
                remaining = len(exercises) - max_questions
                lines.append(f"... 还有 {remaining} 道题目")
                lines.append("")
            
            # 底部信息
            lines.append("🤖 由智能AI系统生成")
            lines.append("📱 更多练习题请使用智慧教育平台")
            
            # 更新分享次数
            generation.share_count += 1
            self.db.commit()
            
            return "\n".join(lines)
            
        except Exception as e:
            print(f"微信格式化失败: {e}")
            return f"分享失败: {e}"
    
    def create_share_link(self, generation_id: int, user_id: int) -> Optional[str]:
        """创建分享链接"""
        try:
            # 这里可以生成一个临时的分享链接
            # 实际项目中需要实现链接生成逻辑
            share_token = str(uuid.uuid4())
            
            # 可以存储分享记录到数据库
            # 这里暂时返回一个模拟链接
            return f"https://your-domain.com/share/exercises/{share_token}"
            
        except Exception as e:
            print(f"创建分享链接失败: {e}")
            return None