#!/usr/bin/env python3
"""
测试用户13的学习计划任务数一致性
"""

import requests

def test_user13_study_plan():
    print("=== 测试用户13的学习计划任务数一致性 ===")
    
    # 使用用户13的登录信息
    login_data = {"code": "test_user_13", "role": "student"}
    response = requests.post("http://localhost:8000/api/v1/auth/wechat/login", json=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    user_id = response.json()["user"]["id"]
    print(f"登录成功，用户ID: {user_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 获取学习计划列表
    print("\n1. 获取学习计划列表...")
    response = requests.get("http://localhost:8000/api/v1/student/study-plan", headers=headers)
    if response.status_code != 200:
        print(f"获取学习计划列表失败: {response.status_code} - {response.text}")
        return
    
    plan_data = response.json()
    print(f"学习计划总体信息:")
    print(f"  总任务数: {plan_data.get('total_tasks', 0)}")
    print(f"  已完成: {plan_data.get('completed_tasks', 0)}")
    print(f"  学科数: {len(plan_data.get('subjects', []))}")
    
    # 显示每个学科的任务数
    subjects = plan_data.get('subjects', [])
    total_subject_tasks = 0
    
    print(f"\n学科任务分布:")
    for subject in subjects:
        subject_task_count = subject.get('taskCount', 0)
        total_subject_tasks += subject_task_count
        print(f"  {subject.get('name', 'unknown')}: {subject_task_count}个任务")
    
    print(f"\n汇总对比:")
    print(f"  计划总任务数: {plan_data.get('total_tasks', 0)}")
    print(f"  学科任务总和: {total_subject_tasks}")
    print(f"  数据一致: {plan_data.get('total_tasks', 0) == total_subject_tasks}")
    
    # 2. 检查每个学科的详细任务
    print(f"\n2. 检查每个学科的详细任务...")
    for subject in subjects:
        subject_name = subject.get('name', '')
        if subject_name:
            print(f"\n检查学科: {subject_name}")
            response = requests.get(f"http://localhost:8000/api/v1/student/study-plan/{subject_name}", headers=headers)
            if response.status_code == 200:
                detail_data = response.json()
                detail_tasks = detail_data.get('tasks', [])
                
                print(f"  学科列表显示任务数: {subject.get('taskCount', 0)}")
                print(f"  学科详情实际任务数: {len(detail_tasks)}")
                print(f"  一致性: {subject.get('taskCount', 0) == len(detail_tasks)}")
                
                if len(detail_tasks) > 0:
                    completed_count = sum(1 for task in detail_tasks if task.get('completed', False))
                    print(f"  详情页完成数: {completed_count}")
                    
                    # 显示任务详情
                    for i, task in enumerate(detail_tasks[:3]):  # 只显示前3个任务
                        print(f"    任务{i+1}: {task.get('title', 'unknown')} - {'已完成' if task.get('completed', False) else '未完成'}")
            else:
                print(f"  获取{subject_name}详情失败: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_user13_study_plan()