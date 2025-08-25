#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试学科映射问题 - 检查新建语文学科是否正确保存和显示
"""

import requests
import json
import sys
import os

# 设置控制台编码以支持中文和特殊字符
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def debug_subject_mapping():
    print("=== 调试学科映射问题 ===")
    
    # 使用固定的测试token
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTYxMDAwMjMsInN1YiI6IjEifQ.R_dHdA1lUTRzyBIGxCPk6UrO7kiucBwSl3R_PHieRn8'
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    base_url = "http://localhost:8000/api/v1"
    
    # 1. 测试语文学习计划（模拟前端修复后的效果）
    print("1. 创建语文学习计划（模拟前端修复后）...")
    create_data = {
        "title": "语文阅读理解提升计划",
        "description": "专注语文阅读理解能力提升",
        "subjects": ["chinese"],  # 选择语文学科
        "priority": "medium",
        "duration_days": 7,
        "daily_time": 30,
        "estimated_time": 210,
        "tasks": [
            {
                "title": "语文阅读理解",
                "subject": "chinese",  # 修复后：使用英文学科代码
                "estimatedTime": 15
            },
            {
                "title": "语文文言文理解", 
                "subject": "chinese",  # 修复后：使用英文学科代码
                "estimatedTime": 15
            }
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/student/study-plan-create", 
                               json=create_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"   [成功] 创建成功: {result.get('title')}")
            print(f"   计划ID: {result.get('plan_id')}")
            
            # 检查创建的任务学科
            for task in result.get('tasks', []):
                print(f"   任务: {task['title']} - 学科: {task['subject']}")
        else:
            print(f"   [失败] 创建失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return
    except Exception as e:
        print(f"   [失败] 创建请求失败: {e}")
        return
    
    # 2. 获取学习计划，检查学科统计
    print("\n2. 获取学习计划，检查学科统计...")
    try:
        response = requests.get(f"{base_url}/student/study-plan", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   总任务数: {data.get('total_tasks', 0)}")
            print(f"   已完成: {data.get('completed_tasks', 0)}")
            
            # 检查学科统计
            subjects = data.get('subjects', [])
            print(f"   学科统计数量: {len(subjects)}")
            for subject in subjects:
                print(f"   学科: {subject['subject']} - 总任务: {subject['total']} - 已完成: {subject['completed']}")
                
            # 检查任务列表
            tasks = data.get('tasks', [])
            print(f"   今日任务数量: {len(tasks)}")
            for task in tasks:
                print(f"   任务: {task['title']} - 学科: {task['subject']}")
                
        else:
            print(f"   [失败] 获取失败: {response.status_code}")
    except Exception as e:
        print(f"   [失败] 获取请求失败: {e}")
    
    # 3. 直接查看数据库中的任务数据
    print("\n3. 查看数据库中最新创建的任务...")
    try:
        import sqlite3
        conn = sqlite3.connect("D:/work/project/zyjc/backend/test.db")
        cursor = conn.cursor()
        
        # 查询最新的study_tasks记录
        cursor.execute("""
            SELECT id, title, subject, study_plan_id, created_at 
            FROM study_tasks 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        tasks = cursor.fetchall()
        
        print(f"   数据库中最新的任务:")
        for task in tasks:
            print(f"   任务ID: {task[0]}, 标题: {task[1]}, 学科: {task[2]}, 计划ID: {task[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"   [失败] 数据库查询失败: {e}")

if __name__ == "__main__":
    debug_subject_mapping()