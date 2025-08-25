-- 中小学全学科智能批改平台数据库初始化脚本

-- 创建数据库
CREATE DATABASE zyjc_db;

-- 使用数据库
\c zyjc_db;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    openid VARCHAR(100) UNIQUE NOT NULL,
    nickname VARCHAR(100),
    avatar_url VARCHAR(255),
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(100) UNIQUE,
    role VARCHAR(20) DEFAULT 'parent' CHECK (role IN ('student', 'parent', 'teacher', 'admin')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'banned')),
    vip_type VARCHAR(20) DEFAULT 'free' CHECK (vip_type IN ('free', 'basic', 'premium', 'family')),
    vip_expire_time TIMESTAMP WITH TIME ZONE,
    daily_quota INTEGER DEFAULT 3,
    daily_used INTEGER DEFAULT 0,
    last_quota_reset DATE DEFAULT CURRENT_DATE,
    total_corrections INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 学生表
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    grade VARCHAR(20) NOT NULL CHECK (grade IN ('grade_1', 'grade_2', 'grade_3', 'grade_4', 'grade_5', 'grade_6', 'grade_7', 'grade_8', 'grade_9')),
    school VARCHAR(100),
    class_name VARCHAR(50),
    parent_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    teacher_id INTEGER,
    total_homework INTEGER DEFAULT 0,
    completed_homework INTEGER DEFAULT 0,
    average_score DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 教师表
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    real_name VARCHAR(50) NOT NULL,
    id_card VARCHAR(18) UNIQUE NOT NULL,
    teaching_subjects TEXT NOT NULL,
    teaching_grades TEXT NOT NULL,
    qualification_cert VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP WITH TIME ZONE,
    total_students INTEGER DEFAULT 0,
    total_corrections INTEGER DEFAULT 0,
    rating DECIMAL(3,2),
    total_income DECIMAL(10,2) DEFAULT 0,
    withdraw_amount DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 作业表
CREATE TABLE IF NOT EXISTS homework (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES students(id) ON DELETE SET NULL,
    original_image_url VARCHAR(255) NOT NULL,
    processed_image_url VARCHAR(255),
    subject VARCHAR(20) NOT NULL CHECK (subject IN ('math', 'chinese', 'english', 'physics', 'chemistry', 'biology', 'geography', 'history')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    ocr_result JSONB,
    correction_result JSONB,
    total_questions INTEGER DEFAULT 0,
    correct_questions INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(5,2),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 错题表
CREATE TABLE IF NOT EXISTS error_questions (
    id SERIAL PRIMARY KEY,
    homework_id INTEGER REFERENCES homework(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(30) NOT NULL,
    difficulty_level VARCHAR(10) CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    user_answer TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    error_type VARCHAR(50),
    explanation TEXT,
    hint TEXT,
    solution_steps JSONB,
    audio_url VARCHAR(255),
    video_url VARCHAR(255),
    practiced_count INTEGER DEFAULT 0,
    mastered BOOLEAN DEFAULT FALSE,
    last_practiced_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 相似题目表
CREATE TABLE IF NOT EXISTS similar_questions (
    id SERIAL PRIMARY KEY,
    error_question_id INTEGER REFERENCES error_questions(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(30) NOT NULL,
    difficulty_level VARCHAR(10) CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    solution_steps JSONB,
    similarity_score DECIMAL(3,2),
    attempted_count INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 知识点表
CREATE TABLE IF NOT EXISTS knowledge_points (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    subject VARCHAR(20) NOT NULL,
    grade VARCHAR(20) NOT NULL,
    parent_id INTEGER REFERENCES knowledge_points(id),
    level INTEGER DEFAULT 1,
    "order" INTEGER DEFAULT 0,
    description TEXT,
    learning_objectives TEXT,
    key_concepts JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    difficulty_weight DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 用户知识点进度表
CREATE TABLE IF NOT EXISTS user_knowledge_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    knowledge_point_id INTEGER REFERENCES knowledge_points(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'not_started' CHECK (status IN ('not_started', 'learning', 'mastered', 'needs_review')),
    mastery_level DECIMAL(3,2) DEFAULT 0.0,
    total_exercises INTEGER DEFAULT 0,
    correct_exercises INTEGER DEFAULT 0,
    last_exercise_at TIMESTAMP WITH TIME ZONE,
    total_study_time INTEGER DEFAULT 0,
    first_learned_at TIMESTAMP WITH TIME ZONE,
    last_reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, knowledge_point_id)
);

-- 支付订单表
CREATE TABLE IF NOT EXISTS payment_orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    order_no VARCHAR(100) UNIQUE NOT NULL,
    product_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed', 'refunded')),
    payment_method VARCHAR(20),
    transaction_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP WITH TIME ZONE
);

-- 创建索引
CREATE INDEX idx_users_openid ON users(openid);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_vip_type ON users(vip_type);
CREATE INDEX idx_students_parent_id ON students(parent_id);
CREATE INDEX idx_students_teacher_id ON students(teacher_id);
CREATE INDEX idx_students_grade ON students(grade);
CREATE INDEX idx_teachers_user_id ON teachers(user_id);
CREATE INDEX idx_teachers_verified ON teachers(is_verified);
CREATE INDEX idx_homework_user_id ON homework(user_id);
CREATE INDEX idx_homework_subject ON homework(subject);
CREATE INDEX idx_homework_status ON homework(status);
CREATE INDEX idx_homework_created_at ON homework(created_at);
CREATE INDEX idx_error_questions_homework_id ON error_questions(homework_id);
CREATE INDEX idx_error_questions_user_id ON error_questions(user_id);
CREATE INDEX idx_error_questions_type ON error_questions(question_type);
CREATE INDEX idx_knowledge_points_subject ON knowledge_points(subject);
CREATE INDEX idx_knowledge_points_grade ON knowledge_points(grade);
CREATE INDEX idx_user_knowledge_progress_user_id ON user_knowledge_progress(user_id);
CREATE INDEX idx_payment_orders_user_id ON payment_orders(user_id);
CREATE INDEX idx_payment_orders_status ON payment_orders(status);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为相关表添加更新时间触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_teachers_updated_at BEFORE UPDATE ON teachers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_homework_updated_at BEFORE UPDATE ON homework FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_error_questions_updated_at BEFORE UPDATE ON error_questions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_similar_questions_updated_at BEFORE UPDATE ON similar_questions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_points_updated_at BEFORE UPDATE ON knowledge_points FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_knowledge_progress_updated_at BEFORE UPDATE ON user_knowledge_progress FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入初始数据
-- 管理员用户
INSERT INTO users (openid, nickname, role, vip_type) VALUES 
('admin_openid', '系统管理员', 'admin', 'premium');

-- 示例知识点数据
INSERT INTO knowledge_points (name, code, subject, grade, description) VALUES
('四则运算', 'MATH_G1_001', 'math', 'grade_1', '基础的加减乘除运算'),
('分数运算', 'MATH_G3_001', 'math', 'grade_3', '分数的加减乘除运算'),
('拼音识别', 'CHINESE_G1_001', 'chinese', 'grade_1', '声母韵母的识别和拼读'),
('汉字书写', 'CHINESE_G1_002', 'chinese', 'grade_1', '基础汉字的笔顺和书写'),
('英语字母', 'ENGLISH_G1_001', 'english', 'grade_1', '26个英语字母的认识和书写'),
('英语单词', 'ENGLISH_G2_001', 'english', 'grade_2', '基础英语单词的学习和记忆');

COMMIT;