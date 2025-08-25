#!/usr/bin/env python3
"""
直接查询数据库中的homework数据
"""

import sqlite3
import os

def check_database_homework():
    db_path = "D:/work/project/zyjc/backend/zyjc_platform.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
        
    print(f"=== 查询数据库文件: {db_path} ===")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询homework表结构
        print("\n1. Homework表结构:")
        cursor.execute("PRAGMA table_info(homework)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]}: {col[2]}")
        
        # 查询homework数据
        print("\n2. Homework表数据:")
        cursor.execute("SELECT id, user_id, total_questions, correct_count, wrong_count, accuracy_rate, status, created_at FROM homework ORDER BY created_at DESC LIMIT 10")
        rows = cursor.fetchall()
        
        if rows:
            print("  ID | UserID | Total | Correct | Wrong | AccuracyRate | Status | CreatedAt")
            print("  " + "-" * 80)
            for row in rows:
                print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]}")
        else:
            print("  没有homework数据")
            
        # 查询特定用户的数据
        print(f"\n3. 用户ID=19的homework数据:")
        cursor.execute("SELECT id, total_questions, correct_count, wrong_count, accuracy_rate, status FROM homework WHERE user_id = 19 ORDER BY created_at DESC LIMIT 5")
        user_rows = cursor.fetchall()
        
        if user_rows:
            for row in user_rows:
                print(f"  ID={row[0]}: 总题={row[1]}, 正确={row[2]}, 错误={row[3]}, 正确率={row[4]}, 状态={row[5]}")
        else:
            print("  用户19没有homework数据")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库查询失败: {e}")

if __name__ == "__main__":
    check_database_homework()