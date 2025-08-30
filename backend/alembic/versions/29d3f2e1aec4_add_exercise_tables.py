"""add_exercise_tables

Revision ID: 29d3f2e1aec4
Revises: 
Create Date: 2025-08-30 15:40:32.979433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29d3f2e1aec4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 exercise_generations 表
    op.create_table(
        'exercise_generations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户ID'),
        sa.Column('subject', sa.String(50), nullable=False, comment='学科'),
        sa.Column('grade', sa.String(20), nullable=False, comment='年级'),
        sa.Column('title', sa.String(200), nullable=False, comment='题目集标题'),
        sa.Column('description', sa.Text(), nullable=True, comment='题目集描述'),
        sa.Column('question_count', sa.Integer(), nullable=False, comment='题目数量'),
        sa.Column('difficulty_level', sa.String(20), nullable=False, comment='难度等级'),
        sa.Column('question_types', sa.TEXT(), nullable=True, comment='题目类型配置'),
        sa.Column('generation_config', sa.TEXT(), nullable=True, comment='生成配置详情'),
        sa.Column('status', sa.String(20), server_default='pending', comment='生成状态'),
        sa.Column('total_questions', sa.Integer(), server_default='0', comment='实际生成题目数'),
        sa.Column('generation_time', sa.Float(), nullable=True, comment='生成耗时'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('view_count', sa.Integer(), server_default='0', comment='查看次数'),
        sa.Column('download_count', sa.Integer(), server_default='0', comment='下载次数'),
        sa.Column('share_count', sa.Integer(), server_default='0', comment='分享次数'),
        sa.Column('is_favorite', sa.Boolean(), server_default='false', comment='是否收藏'),
        sa.Column('is_public', sa.Boolean(), server_default='false', comment='是否公开'),
        sa.Column('is_active', sa.Boolean(), server_default='true', comment='是否激活'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('generated_at', sa.DateTime(), nullable=True, comment='生成完成时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_exercise_generations_id', 'exercise_generations', ['id'])
    
    # 创建 generated_exercises 表
    op.create_table(
        'generated_exercises',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('generation_id', sa.Integer(), nullable=False, comment='生成记录ID'),
        sa.Column('number', sa.Integer(), nullable=False, comment='题目序号'),
        sa.Column('subject', sa.String(50), nullable=False, comment='学科'),
        sa.Column('question_text', sa.Text(), nullable=False, comment='题目内容'),
        sa.Column('question_type', sa.String(50), nullable=False, comment='题目类型'),
        sa.Column('correct_answer', sa.Text(), nullable=False, comment='正确答案'),
        sa.Column('analysis', sa.Text(), nullable=True, comment='解题分析'),
        sa.Column('solution_steps', sa.TEXT(), nullable=True, comment='解题步骤'),
        sa.Column('difficulty', sa.String(20), nullable=False, comment='难度等级'),
        sa.Column('knowledge_points', sa.TEXT(), nullable=True, comment='知识点列表'),
        sa.Column('estimated_time', sa.Integer(), nullable=True, comment='预计用时'),
        sa.Column('generation_source', sa.String(50), server_default='ai', comment='生成来源'),
        sa.Column('generation_prompt', sa.Text(), nullable=True, comment='生成提示词'),
        sa.Column('template_id', sa.Integer(), nullable=True, comment='模板ID'),
        sa.Column('quality_score', sa.Float(), nullable=True, comment='题目质量评分'),
        sa.Column('is_validated', sa.Boolean(), server_default='false', comment='是否已验证'),
        sa.Column('validation_notes', sa.Text(), nullable=True, comment='验证备注'),
        sa.Column('view_count', sa.Integer(), server_default='0', comment='查看次数'),
        sa.Column('correct_rate', sa.Float(), nullable=True, comment='正确率'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.ForeignKeyConstraint(['generation_id'], ['exercise_generations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_generated_exercises_id', 'generated_exercises', ['id'])
    
    # 创建 exercise_templates 表
    op.create_table(
        'exercise_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False, comment='模板名称'),
        sa.Column('subject', sa.String(50), nullable=False, comment='学科'),
        sa.Column('grade_range', sa.String(50), nullable=False, comment='适用年级范围'),
        sa.Column('topic', sa.String(100), nullable=False, comment='知识点/主题'),
        sa.Column('template_content', sa.Text(), nullable=False, comment='模板内容'),
        sa.Column('answer_pattern', sa.String(200), nullable=True, comment='答案模式'),
        sa.Column('variations', sa.TEXT(), nullable=True, comment='变化参数'),
        sa.Column('difficulty_level', sa.String(20), nullable=False, comment='难度等级'),
        sa.Column('question_type', sa.String(50), nullable=False, comment='题目类型'),
        sa.Column('estimated_time', sa.Integer(), nullable=True, comment='预计用时'),
        sa.Column('usage_count', sa.Integer(), server_default='0', comment='使用次数'),
        sa.Column('success_rate', sa.Float(), server_default='0.0', comment='成功率'),
        sa.Column('avg_quality_score', sa.Float(), nullable=True, comment='平均质量评分'),
        sa.Column('is_active', sa.Boolean(), server_default='true', comment='是否启用'),
        sa.Column('is_public', sa.Boolean(), server_default='false', comment='是否公开'),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='创建者ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_exercise_templates_id', 'exercise_templates', ['id'])
    
    # 创建 exercise_downloads 表
    op.create_table(
        'exercise_downloads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('generation_id', sa.Integer(), nullable=False, comment='生成记录ID'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='下载用户ID'),
        sa.Column('download_format', sa.String(20), nullable=False, comment='下载格式'),
        sa.Column('file_name', sa.String(200), nullable=False, comment='文件名'),
        sa.Column('file_path', sa.String(500), nullable=True, comment='文件路径'),
        sa.Column('file_size', sa.Integer(), nullable=True, comment='文件大小'),
        sa.Column('include_answers', sa.Boolean(), server_default='true', comment='是否包含答案'),
        sa.Column('include_analysis', sa.Boolean(), server_default='true', comment='是否包含解析'),
        sa.Column('custom_header', sa.String(200), nullable=True, comment='自定义页眉'),
        sa.Column('paper_size', sa.String(10), server_default='A4', comment='纸张大小'),
        sa.Column('status', sa.String(20), server_default='pending', comment='状态'),
        sa.Column('download_url', sa.String(500), nullable=True, comment='下载链接'),
        sa.Column('expires_at', sa.DateTime(), nullable=True, comment='链接过期时间'),
        sa.Column('processing_time', sa.Float(), nullable=True, comment='处理耗时'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('downloaded_at', sa.DateTime(), nullable=True, comment='下载时间'),
        sa.ForeignKeyConstraint(['generation_id'], ['exercise_generations.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_exercise_downloads_id', 'exercise_downloads', ['id'])
    
    # 创建 exercise_usage_stats 表
    op.create_table(
        'exercise_usage_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False, comment='统计日期'),
        sa.Column('user_id', sa.Integer(), nullable=True, comment='用户ID'),
        sa.Column('subject', sa.String(50), nullable=True, comment='学科'),
        sa.Column('grade', sa.String(20), nullable=True, comment='年级'),
        sa.Column('generation_count', sa.Integer(), server_default='0', comment='生成次数'),
        sa.Column('total_questions', sa.Integer(), server_default='0', comment='生成题目总数'),
        sa.Column('download_count', sa.Integer(), server_default='0', comment='下载次数'),
        sa.Column('view_count', sa.Integer(), server_default='0', comment='查看次数'),
        sa.Column('share_count', sa.Integer(), server_default='0', comment='分享次数'),
        sa.Column('avg_generation_time', sa.Float(), nullable=True, comment='平均生成时间'),
        sa.Column('success_rate', sa.Float(), nullable=True, comment='生成成功率'),
        sa.Column('avg_quality_score', sa.Float(), nullable=True, comment='平均质量评分'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_exercise_usage_stats_id', 'exercise_usage_stats', ['id'])


def downgrade() -> None:
    # 删除表，顺序与创建相反
    op.drop_index('ix_exercise_usage_stats_id', table_name='exercise_usage_stats')
    op.drop_table('exercise_usage_stats')
    
    op.drop_index('ix_exercise_downloads_id', table_name='exercise_downloads')
    op.drop_table('exercise_downloads')
    
    op.drop_index('ix_exercise_templates_id', table_name='exercise_templates')
    op.drop_table('exercise_templates')
    
    op.drop_index('ix_generated_exercises_id', table_name='generated_exercises')
    op.drop_table('generated_exercises')
    
    op.drop_index('ix_exercise_generations_id', table_name='exercise_generations')
    op.drop_table('exercise_generations')