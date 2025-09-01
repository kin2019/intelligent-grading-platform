#!/usr/bin/env python3
"""
添加学生头像字段并设置示例数据
"""

import sqlite3
import os
import random
from pathlib import Path

# 获取数据库路径
DB_PATH = Path(__file__).parent.parent / "zyjc_platform.db"

def add_avatar_column():
    """添加头像字段到students表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查是否已经有avatar字段
        cursor.execute("PRAGMA table_info(students)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'avatar' not in columns:
            print("添加avatar字段到students表...")
            cursor.execute("ALTER TABLE students ADD COLUMN avatar TEXT")
            conn.commit()
            print("✅ avatar字段添加成功")
        else:
            print("avatar字段已存在，跳过添加")
            
    except Exception as e:
        print(f"❌ 添加字段失败: {e}")
        return False
    finally:
        conn.close()
    
    return True

def update_student_avatars():
    """为现有学生设置头像"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 一些示例头像（emoji格式和图片URL格式）
    sample_avatars = [
        "emoji:👦",
        "emoji:👧", 
        "emoji:🧒",
        "emoji:👶",
        "emoji:🎓",
        "emoji:📚",
        "emoji:🤗",
        "emoji:😊",
        "emoji:🌟",
        "emoji:🎨",
    ]
    
    try:
        # 获取没有头像的学生
        cursor.execute("SELECT id, name FROM students WHERE avatar IS NULL OR avatar = ''")
        students = cursor.fetchall()
        
        if not students:
            print("所有学生已有头像")
            return
            
        print(f"为 {len(students)} 个学生设置头像...")
        
        # 为每个学生随机分配头像
        for student_id, student_name in students:
            avatar = random.choice(sample_avatars)
            cursor.execute("UPDATE students SET avatar = ? WHERE id = ?", (avatar, student_id))
            print(f"  - {student_name}: {avatar}")
        
        conn.commit()
        print("✅ 学生头像更新完成")
        
    except Exception as e:
        print(f"❌ 更新学生头像失败: {e}")
    finally:
        conn.close()

def main():
    """主函数"""
    print("开始添加学生头像支持...")
    
    if not DB_PATH.exists():
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return
    
    # 1. 添加头像字段
    if not add_avatar_column():
        return
    
    # 2. 更新现有学生头像
    update_student_avatars()
    
    print("🎉 学生头像设置完成！")

if __name__ == "__main__":
    main()