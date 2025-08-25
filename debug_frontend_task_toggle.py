#!/usr/bin/env python3
"""
调试前端任务切换的汇总数据更新问题
"""

import requests
import json

def debug_frontend_task_toggle():
    print("=== 调试前端任务切换汇总数据更新 ===")
    
    # 使用固定的用户token（从前端复制）
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTYxMDAwMjMsInN1YiI6IjEifQ.R_dHdA1lUTRzyBIGxCPk6UrO7kiucBwSl3R_PHieRn8'
    headers = {"Authorization": f"Bearer {token}"}
    
    print("1. 获取当前学习计划状态...")
    response = requests.get("http://localhost:8000/api/v1/student/study-plan", headers=headers)
    if response.status_code != 200:
        print(f"获取学习计划失败: {response.status_code}")
        return
    
    data = response.json()
    print(f"当前汇总数据:")
    print(f"  总任务数: {data.get('total_tasks', 0)}")
    print(f"  已完成: {data.get('completed_tasks', 0)}")
    print(f"  今日任务数: {len(data.get('tasks', []))}")
    
    tasks = data.get('tasks', [])
    if not tasks:
        print("没有今日任务可以切换")
        return
        
    # 找到第一个任务
    first_task = tasks[0]
    task_id = first_task.get('id')
    task_title = first_task.get('title', '')
    is_completed = first_task.get('completed', False)
    
    print(f"\n2. 切换任务: {task_title} (ID: {task_id})")
    print(f"   切换前状态: {'已完成' if is_completed else '未完成'}")
    
    # 执行任务切换
    response = requests.post(f"http://localhost:8000/api/v1/student/study-plan/task/{task_id}/toggle", headers=headers)
    
    if response.status_code != 200:
        print(f"任务切换失败: {response.status_code}")
        if response.text:
            print(f"错误信息: {response.text}")
        return
    
    toggle_result = response.json()
    print(f"   切换成功: {toggle_result.get('message', '')}")
    
    # 检查API返回的汇总数据
    if 'plan_progress' in toggle_result:
        progress = toggle_result['plan_progress']
        api_total = progress.get('total_tasks', 0)
        api_completed = progress.get('completed_tasks', 0)
        api_progress_percent = progress.get('progress', 0)
        
        print(f"\n3. API返回的汇总数据:")
        print(f"   总任务数: {api_total}")
        print(f"   已完成: {api_completed}")
        print(f"   进度: {api_progress_percent:.1f}%")
        
        # 预期值计算
        expected_completed = data.get('completed_tasks', 0) + (1 if not is_completed else -1)
        expected_total = data.get('total_tasks', 0)
        
        print(f"\n4. 数据正确性验证:")
        print(f"   总任务数正确: {api_total == expected_total} (期望{expected_total}, 实际{api_total})")
        print(f"   已完成数正确: {api_completed == expected_completed} (期望{expected_completed}, 实际{api_completed})")
        
        if api_total == expected_total and api_completed == expected_completed:
            print("   API返回的汇总数据正确!")
        else:
            print("   API返回的汇总数据有误!")
    else:
        print("\n❌ API未返回plan_progress数据!")
    
    # 重新获取学习计划验证
    print(f"\n5. 重新获取学习计划验证...")
    response = requests.get("http://localhost:8000/api/v1/student/study-plan", headers=headers)
    if response.status_code == 200:
        updated_data = response.json()
        updated_total = updated_data.get('total_tasks', 0)
        updated_completed = updated_data.get('completed_tasks', 0)
        
        print(f"重新查询的汇总数据:")
        print(f"  总任务数: {updated_total}")
        print(f"  已完成: {updated_completed}")
        
        # 验证前端应该获取的数据
        if 'plan_progress' in toggle_result:
            progress = toggle_result['plan_progress']
            api_total = progress.get('total_tasks', 0)
            api_completed = progress.get('completed_tasks', 0)
            
            consistency_check = (api_total == updated_total and api_completed == updated_completed)
            print(f"  API与重新查询一致性: {consistency_check}")
            
            if consistency_check:
                print("   前端可以直接使用API返回的汇总数据!")
            else:
                print("   前端需要重新请求学习计划数据!")
    else:
        print(f"重新获取学习计划失败: {response.status_code}")

if __name__ == "__main__":
    debug_frontend_task_toggle()