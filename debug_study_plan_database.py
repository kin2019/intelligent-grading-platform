#!/usr/bin/env python3
"""
检查数据库中的学习计划数据
"""

import sqlite3
import os

def check_study_plan_database():
    db_path = "D:/work/project/zyjc/backend/test.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
        
    print(f"=== 查询学习计划数据库: {db_path} ===")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%study%'")
        tables = cursor.fetchall()
        print(f"学习计划相关表: {tables}")
        
        if not tables:
            print("没有找到学习计划相关的表")
            return
        
        # 检查study_plans表
        print("\n=== StudyPlans表数据 ===")
        try:
            cursor.execute("SELECT id, user_id, title, total_tasks, completed_tasks, status, is_active FROM study_plans ORDER BY created_at DESC LIMIT 10")
            plans = cursor.fetchall()
            
            if plans:
                print("ID | UserID | Title | Total | Completed | Status | Active")
                print("-" * 60)
                for plan in plans:
                    print(f"{plan[0]} | {plan[1]} | {plan[2]} | {plan[3]} | {plan[4]} | {plan[5]} | {plan[6]}")
            else:
                print("没有学习计划数据")
        except Exception as e:
            print(f"查询study_plans表失败: {e}")
        
        # 检查study_tasks表  
        print("\n=== StudyTasks表数据 ===")
        try:
            cursor.execute("SELECT id, study_plan_id, title, subject, completed, status FROM study_tasks ORDER BY created_at DESC LIMIT 15")
            tasks = cursor.fetchall()
            
            if tasks:
                print("ID | PlanID | Title | Subject | Completed | Status")
                print("-" * 50)
                for task in tasks:
                    print(f"{task[0]} | {task[1]} | {task[2]} | {task[3]} | {task[4]} | {task[5]}")
            else:
                print("没有学习任务数据")
        except Exception as e:
            print(f"查询study_tasks表失败: {e}")
        
        # 统计每个计划的任务数
        print("\n=== 每个计划的任务数统计 ===")
        try:
            cursor.execute("""
                SELECT sp.id, sp.title, sp.total_tasks as stored_total, 
                       COUNT(st.id) as actual_total,
                       sp.completed_tasks as stored_completed,
                       SUM(CASE WHEN st.completed = 1 THEN 1 ELSE 0 END) as actual_completed
                FROM study_plans sp 
                LEFT JOIN study_tasks st ON sp.id = st.study_plan_id 
                WHERE sp.is_active = 1
                GROUP BY sp.id, sp.title, sp.total_tasks, sp.completed_tasks
            """)
            stats = cursor.fetchall()
            
            if stats:
                print("PlanID | Title | StoredTotal | ActualTotal | StoredComp | ActualComp")
                print("-" * 70)
                for stat in stats:
                    print(f"{stat[0]} | {stat[1]} | {stat[2]} | {stat[3]} | {stat[4]} | {stat[5]}")
                    if stat[2] != stat[3] or stat[4] != stat[5]:
                        print(f"  ⚠️  数据不一致!")
            else:
                print("没有活跃的学习计划")
        except Exception as e:
            print(f"统计计划任务数失败: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库查询失败: {e}")

if __name__ == "__main__":
    check_study_plan_database()