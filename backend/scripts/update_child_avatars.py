#!/usr/bin/env python3
"""
为现有的孩子用户更新头像
"""

import sqlite3
import random
from pathlib import Path

# 获取数据库路径
DB_PATH = Path(__file__).parent.parent / "app.db"

def update_child_avatars():
    """为现有孩子更新头像"""
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
        "/uploads/avatars/child1.png",
        "/uploads/avatars/child2.png",
        "/uploads/avatars/child3.png",
    ]
    
    try:
        # 获取所有角色为student的用户，这些是孩子账号
        cursor.execute("SELECT id, nickname FROM users WHERE role = 'student'")
        students = cursor.fetchall()
        
        if not students:
            print("没有找到学生用户")
            return
            
        print(f"找到 {len(students)} 个学生用户，开始更新头像...")
        
        # 为每个学生随机分配头像
        for student_id, student_name in students:
            avatar = random.choice(sample_avatars)
            cursor.execute("UPDATE users SET avatar_url = ? WHERE id = ?", (avatar, student_id))
            print(f"  - 学生ID {student_id} ({student_name}): {avatar}")
        
        conn.commit()
        print("✅ 学生头像更新完成")
        
    except Exception as e:
        print(f"❌ 更新学生头像失败: {e}")
    finally:
        conn.close()

def check_current_data():
    """检查当前数据库状态"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查用户表结构
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        print("users表的列:", columns)
        
        # 检查是否有学生用户
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
        student_count = cursor.fetchone()[0]
        print(f"学生用户数量: {student_count}")
        
        # 检查parent_child关系
        cursor.execute("SELECT COUNT(*) FROM parent_child WHERE is_active = 1")
        relation_count = cursor.fetchone()[0]
        print(f"活跃的家长-孩子关系: {relation_count}")
        
        # 检查现有头像情况
        cursor.execute("SELECT id, nickname, avatar_url FROM users WHERE role = 'student' LIMIT 5")
        sample_students = cursor.fetchall()
        print("示例学生数据:")
        for student in sample_students:
            print(f"  - ID: {student[0]}, 昵称: {student[1]}, 头像: {student[2]}")
            
    except Exception as e:
        print(f"检查数据失败: {e}")
    finally:
        conn.close()

def main():
    """主函数"""
    print("开始检查和更新学生头像...")
    
    if not DB_PATH.exists():
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return
    
    # 1. 检查当前数据
    print("\n=== 当前数据状态 ===")
    check_current_data()
    
    # 2. 更新头像
    print("\n=== 更新头像 ===")
    update_child_avatars()
    
    print("\n🎉 头像更新完成！")

if __name__ == "__main__":
    main()