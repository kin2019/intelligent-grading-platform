#!/usr/bin/env python3
"""
为当前用户创建测试学习计划数据
"""

import requests
import json

def create_test_study_plan():
    print("=== 创建测试学习计划 ===")
    
    # 登录用户
    login_data = {"code": "test_user_13", "role": "student"}
    response = requests.post("http://localhost:8000/api/v1/auth/wechat/login", json=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    user_id = response.json()["user"]["id"]
    print(f"登录成功，用户ID: {user_id}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 创建学习计划
    plan_data = {
        "title": "测试任务切换汇总",
        "description": "用于测试任务切换API汇总数据更新",
        "subjects": ["math", "chinese", "english"],
        "priority": "high",
        "duration_days": 7,
        "daily_time": 60,
        "estimated_time": 150,
        "tasks": [
            {
                "title": "数学基础练习",
                "subject": "math",
                "estimatedTime": 30
            },
            {
                "title": "数学进阶练习", 
                "subject": "math",
                "estimatedTime": 40
            },
            {
                "title": "语文阅读理解",
                "subject": "chinese", 
                "estimatedTime": 35
            },
            {
                "title": "英语单词记忆",
                "subject": "english",
                "estimatedTime": 25
            },
            {
                "title": "英语语法练习",
                "subject": "english", 
                "estimatedTime": 20
            }
        ]
    }
    
    print("\n创建学习计划...")
    response = requests.post("http://localhost:8000/api/v1/student/study-plan-create", 
                           json=plan_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"学习计划创建成功:")
        print(f"  计划ID: {result.get('plan_id')}")
        print(f"  标题: {result.get('title')}")
        print(f"  总任务数: {result.get('total_tasks')}")
        print(f"  预计时间: {result.get('estimated_time')}分钟")
        
        # 验证学习计划
        print(f"\n验证学习计划...")
        response = requests.get("http://localhost:8000/api/v1/student/study-plan", headers=headers)
        if response.status_code == 200:
            plan_data = response.json()
            print(f"验证结果:")
            print(f"  总任务数: {plan_data.get('total_tasks', 0)}")
            print(f"  已完成: {plan_data.get('completed_tasks', 0)}")
            print(f"  今日任务数: {len(plan_data.get('tasks', []))}")
            print(f"  学科数: {len(plan_data.get('subjects', []))}")
            
            tasks = plan_data.get('tasks', [])
            if tasks:
                print(f"\n今日任务列表:")
                for i, task in enumerate(tasks[:3], 1):  # 只显示前3个任务
                    print(f"  {i}. {task.get('title')} (ID: {task.get('id')}) - {'已完成' if task.get('completed') else '未完成'}")
        else:
            print(f"验证学习计划失败: {response.status_code}")
    else:
        print(f"创建学习计划失败: {response.status_code}")
        if response.text:
            print(f"错误信息: {response.text}")

if __name__ == "__main__":
    create_test_study_plan()