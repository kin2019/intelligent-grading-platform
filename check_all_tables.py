#!/usr/bin/env python3
"""
检查数据库中的所有表结构
"""

import sqlite3
import os

def check_all_database_tables():
    db_path = "D:/work/project/zyjc/backend/test.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
        
    print(f"=== 检查所有数据库表: {db_path} ===")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"数据库中的所有表: {[table[0] for table in tables]}")
        
        # 检查每个表的结构和数据
        for table in tables:
            table_name = table[0]
            print(f"\n=== 表: {table_name} ===")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("表结构:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - PK: {col[5]}, NotNull: {col[3]}")
            
            # 获取表数据行数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"数据行数: {count}")
            
            # 如果数据较少，显示前几行
            if count > 0 and count <= 10:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                print("示例数据:")
                for row in rows:
                    print(f"  {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库检查失败: {e}")

if __name__ == "__main__":
    check_all_database_tables()