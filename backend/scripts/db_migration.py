#!/usr/bin/env python3
"""
智能教育平台 - 数据库迁移脚本
支持创建和更新数据库结构
"""

import sys
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

class DatabaseMigrator:
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn.cursor()
        
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            
    def create_tables(self):
        """创建所有必需的数据库表"""
        cursor = self.connect()
        
        try:
            print("🔧 创建数据库表结构...")
            
            # 1. 创建users表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    openid VARCHAR(100) UNIQUE NOT NULL,
                    unionid VARCHAR(100),
                    nickname VARCHAR(100),
                    avatar_url VARCHAR(500),
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    role VARCHAR(20) NOT NULL DEFAULT 'student',
                    grade VARCHAR(20),
                    is_vip BOOLEAN DEFAULT 0,
                    vip_expire_time DATETIME,
                    daily_quota INTEGER DEFAULT 3,
                    daily_used INTEGER DEFAULT 0,
                    last_quota_reset DATETIME DEFAULT CURRENT_DATE,
                    total_used INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    is_verified BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login_at DATETIME,
                    settings TEXT
                )
            """)
            print("✅ 用户表(users)创建完成")
            
            # 2. 创建parent_child表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parent_child (
                    id INTEGER PRIMARY KEY,
                    parent_id INTEGER NOT NULL,
                    child_id INTEGER NOT NULL,
                    relationship_type VARCHAR(20) DEFAULT 'parent',
                    nickname VARCHAR(50),
                    school VARCHAR(100),
                    class_name VARCHAR(50),
                    is_active BOOLEAN DEFAULT 1,
                    can_view_homework BOOLEAN DEFAULT 1,
                    can_view_reports BOOLEAN DEFAULT 1,
                    can_set_limits BOOLEAN DEFAULT 1,
                    daily_homework_limit INTEGER DEFAULT 10,
                    daily_time_limit INTEGER DEFAULT 120,
                    bedtime_reminder VARCHAR(5),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES users (id),
                    FOREIGN KEY (child_id) REFERENCES users (id)
                )
            """)
            print("✅ 家长子女关系表(parent_child)创建完成")
            
            # 3. 创建homework表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS homework (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    original_image_url VARCHAR(500),
                    processed_image_url VARCHAR(500),
                    subject VARCHAR(50),
                    subject_type VARCHAR(50),
                    grade_level VARCHAR(20),
                    ocr_result TEXT,
                    ocr_text TEXT,
                    correction_result TEXT,
                    total_questions INTEGER DEFAULT 0,
                    correct_count INTEGER DEFAULT 0,
                    wrong_count INTEGER DEFAULT 0,
                    accuracy_rate FLOAT DEFAULT 0.0,
                    status VARCHAR(20) DEFAULT 'pending',
                    error_message TEXT,
                    processing_time FLOAT DEFAULT 0.0,
                    ocr_time FLOAT DEFAULT 0.0,
                    correction_time FLOAT DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            print("✅ 作业表(homework)创建完成")
            
            # 4. 创建error_questions表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_questions (
                    id INTEGER PRIMARY KEY,
                    homework_id INTEGER,
                    user_id INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    user_answer TEXT,
                    correct_answer TEXT,
                    error_type VARCHAR(50),
                    error_reason TEXT,
                    explanation TEXT,
                    knowledge_points TEXT,
                    difficulty_level VARCHAR(20),
                    is_reviewed BOOLEAN DEFAULT 0,
                    review_count INTEGER DEFAULT 0,
                    last_review_at DATETIME,
                    audio_url VARCHAR(500),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (homework_id) REFERENCES homework (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            print("✅ 错题表(error_questions)创建完成")
            
            # 5. 创建study_plans表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS study_plans (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    priority VARCHAR(20) DEFAULT 'medium',
                    duration_days INTEGER DEFAULT 7,
                    daily_time INTEGER DEFAULT 30,
                    subjects TEXT,
                    total_tasks INTEGER DEFAULT 0,
                    completed_tasks INTEGER DEFAULT 0,
                    estimated_time INTEGER DEFAULT 0,
                    actual_time INTEGER DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'draft',
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    start_date DATE,
                    end_date DATE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            print("✅ 学习计划表(study_plans)创建完成")
            
            # 6. 创建study_tasks表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS study_tasks (
                    id INTEGER PRIMARY KEY,
                    study_plan_id INTEGER NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    subject VARCHAR(50),
                    estimated_time INTEGER DEFAULT 30,
                    actual_time INTEGER DEFAULT 0,
                    priority VARCHAR(20) DEFAULT 'medium',
                    difficulty VARCHAR(20) DEFAULT 'medium',
                    completed BOOLEAN DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'pending',
                    due_date DATE,
                    due_time TIME,
                    scheduled_date DATE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    started_at DATETIME,
                    FOREIGN KEY (study_plan_id) REFERENCES study_plans (id)
                )
            """)
            print("✅ 学习任务表(study_tasks)创建完成")
            
            # 7. 创建exercise_generations表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exercise_generations (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    subject VARCHAR(50) NOT NULL,
                    grade VARCHAR(20) NOT NULL,
                    title VARCHAR(200),
                    description TEXT,
                    question_count INTEGER DEFAULT 5,
                    difficulty_level VARCHAR(20) DEFAULT 'same',
                    question_types TEXT,
                    status VARCHAR(20) DEFAULT 'pending',
                    total_questions INTEGER DEFAULT 0,
                    generation_time FLOAT DEFAULT 0.0,
                    progress_percent FLOAT DEFAULT 0.0,
                    view_count INTEGER DEFAULT 0,
                    download_count INTEGER DEFAULT 0,
                    share_count INTEGER DEFAULT 0,
                    is_favorite BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    generated_at DATETIME,
                    error_message TEXT,
                    config TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            print("✅ 智能出题记录表(exercise_generations)创建完成")
            
            # 8. 创建exercises表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exercises (
                    id INTEGER PRIMARY KEY,
                    generation_id INTEGER NOT NULL,
                    number INTEGER NOT NULL,
                    subject VARCHAR(50) NOT NULL,
                    question_text TEXT NOT NULL,
                    question_type VARCHAR(50),
                    correct_answer TEXT,
                    analysis TEXT,
                    difficulty VARCHAR(20),
                    knowledge_points TEXT,
                    estimated_time INTEGER,
                    quality_score FLOAT,
                    view_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (generation_id) REFERENCES exercise_generations (id)
                )
            """)
            print("✅ 题目表(exercises)创建完成")
            
            # 提交事务
            self.conn.commit()
            print("🎉 所有数据库表创建完成！")
            
        except Exception as e:
            print(f"❌ 创建数据库表时出错: {e}")
            self.conn.rollback()
            raise
        finally:
            self.disconnect()
    
    def create_indexes(self):
        """创建数据库索引以优化性能"""
        cursor = self.connect()
        
        try:
            print("📊 创建数据库索引...")
            
            # 用户表索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_openid ON users(openid)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at)")
            
            # 家长子女关系表索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_parent_child_parent_id ON parent_child(parent_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_parent_child_child_id ON parent_child(child_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_parent_child_active ON parent_child(is_active)")
            
            # 作业表索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_homework_user_id ON homework(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_homework_status ON homework(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_homework_created_at ON homework(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_homework_subject ON homework(subject)")
            
            # 错题表索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_questions_user_id ON error_questions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_questions_homework_id ON error_questions(homework_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_questions_reviewed ON error_questions(is_reviewed)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_error_questions_created_at ON error_questions(created_at)")
            
            # 学习计划表索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_study_plans_user_id ON study_plans(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_study_plans_status ON study_plans(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_study_plans_active ON study_plans(is_active)")
            
            # 学习任务表索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_study_tasks_plan_id ON study_tasks(study_plan_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_study_tasks_status ON study_tasks(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_study_tasks_due_date ON study_tasks(due_date)")
            
            # 智能出题记录表索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exercise_generations_user_id ON exercise_generations(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exercise_generations_status ON exercise_generations(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exercise_generations_subject ON exercise_generations(subject)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exercise_generations_created_at ON exercise_generations(created_at)")
            
            # 题目表索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exercises_generation_id ON exercises(generation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exercises_subject ON exercises(subject)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exercises_difficulty ON exercises(difficulty)")
            
            self.conn.commit()
            print("✅ 数据库索引创建完成")
            
        except Exception as e:
            print(f"❌ 创建数据库索引时出错: {e}")
            self.conn.rollback()
            raise
        finally:
            self.disconnect()
    
    def insert_initial_data(self):
        """插入初始化数据"""
        cursor = self.connect()
        
        try:
            print("🌱 插入初始化数据...")
            
            # 检查是否已有数据
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                # 创建管理员用户
                admin_password_hash = hashlib.sha256('admin123456'.encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users 
                    (id, openid, unionid, nickname, role, is_vip, daily_quota, is_active, is_verified) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (999, 'admin_999', 'admin_union_999', '系统管理员', 'admin', 1, -1, 1, 1))
                
                # 创建演示学生用户
                cursor.execute("""
                    INSERT INTO users 
                    (id, openid, unionid, nickname, role, grade, daily_quota, is_active) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (1, 'demo_student_1', 'demo_union_1', '演示学生', 'student', '五年级', 3, 1))
                
                # 创建演示家长用户
                cursor.execute("""
                    INSERT INTO users 
                    (id, openid, unionid, nickname, role, daily_quota, is_active) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (2, 'demo_parent_2', 'demo_union_2', '演示家长', 'parent', 5, 1))
                
                # 创建家长-学生关系
                cursor.execute("""
                    INSERT INTO parent_child 
                    (parent_id, child_id, nickname, school, class_name, is_active) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (2, 1, '小宝贝', '实验小学', '五年级1班', 1))
                
                self.conn.commit()
                print("✅ 初始化数据插入完成")
                print("   - 管理员账户: admin (ID: 999)")
                print("   - 演示学生账户: 演示学生 (ID: 1)")
                print("   - 演示家长账户: 演示家长 (ID: 2)")
                print("   - 家长-学生关系已建立")
            else:
                print("📋 数据库中已存在用户数据，跳过初始化数据插入")
                
        except Exception as e:
            print(f"❌ 插入初始化数据时出错: {e}")
            self.conn.rollback()
            raise
        finally:
            self.disconnect()
    
    def run_migration(self):
        """运行完整的数据库迁移"""
        print("🚀 开始数据库迁移...")
        print(f"📍 数据库路径: {self.db_path}")
        print(f"🕒 迁移时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        try:
            self.create_tables()
            self.create_indexes()
            self.insert_initial_data()
            
            print("=" * 50)
            print("🎉 数据库迁移完成！")
            print("✅ 所有表结构已创建")
            print("✅ 性能索引已建立")
            print("✅ 初始数据已插入")
            print("\n📖 下一步:")
            print("   1. 启动后端服务: python main.py")
            print("   2. 访问管理员界面进行系统配置")
            print("   3. 开始使用智能教育平台")
            
        except Exception as e:
            print(f"❌ 数据库迁移失败: {e}")
            return False
        
        return True

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='智能教育平台数据库迁移工具')
    parser.add_argument('--db-path', default='app.db', help='数据库文件路径')
    parser.add_argument('--force', action='store_true', help='强制重新创建数据库')
    
    args = parser.parse_args()
    
    # 如果强制重建，先删除现有数据库文件
    if args.force and Path(args.db_path).exists():
        print(f"⚠️  强制模式：删除现有数据库文件 {args.db_path}")
        Path(args.db_path).unlink()
    
    # 运行迁移
    migrator = DatabaseMigrator(args.db_path)
    success = migrator.run_migration()
    
    if success:
        print("\n🎯 迁移成功！数据库已准备就绪。")
        sys.exit(0)
    else:
        print("\n💥 迁移失败！请检查错误信息并重试。")
        sys.exit(1)

if __name__ == "__main__":
    main()