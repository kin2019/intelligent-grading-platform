#!/usr/bin/env python3
"""
创建错题本测试数据
包含已复习和未复习的错题记录
"""

import sqlite3
from datetime import datetime, timedelta
import json

def create_test_data():
    """创建测试数据"""
    # 连接SQLite数据库
    db_path = "backend/app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("开始创建错题本测试数据...")
        
        # 1. 创建错题表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                homework_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                user_answer TEXT,
                correct_answer TEXT NOT NULL,
                error_type TEXT,
                error_reason TEXT,
                explanation TEXT,
                knowledge_points TEXT,
                difficulty_level INTEGER DEFAULT 1,
                is_reviewed BOOLEAN DEFAULT 0,
                review_count INTEGER DEFAULT 0,
                last_review_at TEXT,
                audio_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. 清除现有测试数据
        cursor.execute("DELETE FROM error_questions WHERE user_id = 1")
        print("清除现有测试数据...")
        
        conn.commit()
        print("数据库表准备完成")
        
        # 3. 创建错题记录
        error_questions_data = [
            # 数学错题 - 未复习
            (1, 1000, 1, "计算：125 + 78 = ?", "193", "203", "计算错误", 
             "加法运算时进位错误", "125 + 78 的正确计算:\\n个位：5 + 8 = 13，写3进1\\n十位：2 + 7 + 1 = 10，写0进1\\n百位：1 + 0 + 1 = 2\\n正确答案是203",
             json.dumps(["三位数加法", "进位运算"]), 2, 0, 0, None),
            
            # 数学错题 - 已复习1次
            (2, 1000, 1, "计算：456 - 189 = ?", "277", "267", "借位错误",
             "减法运算时借位计算错误", "456 - 189 的正确计算:\\n个位：6 - 9 不够减，从十位借1\\n16 - 9 = 7\\n十位：4 - 1 - 8 不够减，从百位借1\\n14 - 1 - 8 = 5\\n百位：3 - 1 = 2\\n正确答案是267",
             json.dumps(["三位数减法", "借位运算"]), 3, 1, 1, (datetime.now() - timedelta(hours=2)).isoformat()),
            
            # 语文错题 - 未复习  
            (3, 1001, 1, "请默写：春眠不觉晓，处处闻啼鸟", "春眠不觉晓，处处闻啼乌", "春眠不觉晓，处处闻啼鸟", "字词错误",
             "将'鸟'字写成了'乌'字", "这是孟浩然的《春晓》，'啼鸟'指的是鸣叫的鸟儿，不是'乌鸦'的'乌'。要注意区分同音字的写法。",
             json.dumps(["古诗默写", "同音字辨析"]), 2, 0, 0, None),
            
            # 语文错题 - 已复习2次
            (4, 1001, 1, "请解释词语：络绎不绝", "一个接一个，连续不停", "形容来往车马或人等连续不断", "理解不准确",
             "对词语含义理解过于简化", "'络绎不绝'专指来往的车马、人等连续不断，不是泛指所有连续的事物。要注意词语的具体使用场景。",
             json.dumps(["成语理解", "词语辨析"]), 3, 1, 2, (datetime.now() - timedelta(minutes=30)).isoformat()),
            
            # 英语错题 - 未复习
            (5, 1002, 1, "翻译：I have an apple.", "我有一个苹果。", "我有一个苹果。", "冠词使用",
             "虽然翻译正确，但需要注意冠词'an'的使用", "这道题翻译是正确的。需要注意的是'an'用在元音开头的单词前，'apple'以元音'a'开头，所以用'an'而不是'a'。",
             json.dumps(["冠词使用", "基础翻译"]), 2, 0, 0, None),
             
            # 英语错题 - 已复习3次
            (6, 1002, 1, "选择：She __ a teacher. (is/are)", "are", "is", "主谓一致",
             "主语'She'是第三人称单数，应该用'is'", "在英语中，第三人称单数（he, she, it）作主语时，be动词要用'is'。复数或者I、you作主语时才用'are'。",
             json.dumps(["be动词", "主谓一致"]), 4, 1, 3, (datetime.now() - timedelta(minutes=10)).isoformat())
        ]
        
        print(f"准备插入 {len(error_questions_data)} 条错题记录...")
        
        # 插入数据
        for data in error_questions_data:
            cursor.execute('''
                INSERT INTO error_questions 
                (id, homework_id, user_id, question_text, user_answer, correct_answer, error_type, 
                 error_reason, explanation, knowledge_points, difficulty_level, is_reviewed, review_count, last_review_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
            print(f"  错题 {data[0]}: {data[3][:30]}... ({'已复习' if data[11] else '未复习'})")
        
        conn.commit()
        print("错题记录创建完成")
        
        # 4. 验证数据
        cursor.execute("SELECT COUNT(*) FROM error_questions WHERE user_id = 1")
        total_errors = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM error_questions WHERE user_id = 1 AND is_reviewed = 1")
        reviewed_count = cursor.fetchone()[0]
        
        unreviewed_count = total_errors - reviewed_count
        
        print(f"\n数据统计:")
        print(f"  总错题数: {total_errors}")
        print(f"  已复习: {reviewed_count}")
        print(f"  未复习: {unreviewed_count}")
        
        print(f"\n测试建议:")
        print(f"  1. 访问错题本列表页面: http://localhost:8000/frontend/error-book.html")
        print(f"  2. 点击错题进入详情页面")
        print(f"  3. 测试'标记为已复习'功能")
        print(f"  4. 验证复习状态和次数的更新")
        
        print(f"\n错题本测试数据创建完成！")
        
    except Exception as e:
        print(f"创建测试数据失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_data()