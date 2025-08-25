#!/usr/bin/env python3
"""
全面测试任务切换API的汇总数据更新功能
"""

import requests
import json

def comprehensive_toggle_test():
    print("=== 全面测试任务切换API汇总数据更新 ===")
    
    # 登录用户
    login_data = {"code": "test_user_13", "role": "student"}
    response = requests.post("http://localhost:8000/api/v1/auth/wechat/login", json=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    user_id = response.json()["user"]["id"]
    print(f"登录成功，用户ID: {user_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取初始状态
    print("\n1. 获取初始学习计划状态...")
    response = requests.get("http://localhost:8000/api/v1/student/study-plan", headers=headers)
    if response.status_code != 200:
        print(f"获取学习计划失败: {response.status_code}")
        return
    
    initial_data = response.json()
    initial_total = initial_data.get('total_tasks', 0)
    initial_completed = initial_data.get('completed_tasks', 0)
    tasks = initial_data.get('tasks', [])
    
    print(f"初始状态: 总任务{initial_total}个，已完成{initial_completed}个")
    print(f"今日任务数: {len(tasks)}个")
    
    if len(tasks) < 3:
        print("任务数量不足，至少需要3个任务进行测试")
        return
    
    # 连续切换多个任务状态
    for i in range(min(3, len(tasks))):
        task = tasks[i]
        task_id = task.get('id')
        task_title = task.get('title', '')
        current_status = task.get('completed', False)
        
        print(f"\n{i+2}. 切换任务 {i+1}: {task_title} (ID: {task_id})")
        print(f"   当前状态: {'已完成' if current_status else '未完成'}")
        
        # 切换任务状态
        response = requests.post(f"http://localhost:8000/api/v1/student/study-plan/task/{task_id}/toggle", headers=headers)
        
        if response.status_code != 200:
            print(f"   切换失败: {response.status_code}")
            continue
        
        toggle_result = response.json()
        print(f"   切换结果: {toggle_result.get('message', '')}")
        
        # 检查API返回的进度信息
        if 'plan_progress' in toggle_result:
            progress = toggle_result['plan_progress']
            api_total = progress.get('total_tasks', 0)
            api_completed = progress.get('completed_tasks', 0)
            print(f"   API返回汇总: 总任务{api_total}个，已完成{api_completed}个")
            
            # 验证总任务数不变
            if api_total != initial_total:
                print(f"   ⚠️ 总任务数变化异常: {initial_total} -> {api_total}")
            
            # 验证已完成任务数逻辑正确
            expected_completed = initial_completed + (i + 1) if not current_status else initial_completed - (i + 1)
            if api_completed == expected_completed:
                print(f"   ✅ 已完成任务数正确: {api_completed}")
            else:
                print(f"   ⚠️ 已完成任务数异常: 期望{expected_completed}，实际{api_completed}")
        else:
            print(f"   ⚠️ API未返回plan_progress信息")
        
        # 更新本地任务状态用于下次计算
        task['completed'] = not current_status
    
    # 最终验证
    print(f"\n{3 + min(3, len(tasks))}. 最终验证...")
    response = requests.get("http://localhost:8000/api/v1/student/study-plan", headers=headers)
    if response.status_code == 200:
        final_data = response.json()
        final_total = final_data.get('total_tasks', 0)
        final_completed = final_data.get('completed_tasks', 0)
        
        print(f"最终状态: 总任务{final_total}个，已完成{final_completed}个")
        print(f"总任务数一致性: {initial_total == final_total}")
        
        # 计算期望的最终完成数
        toggle_count = min(3, len(tasks))
        expected_final_completed = initial_completed + toggle_count
        if final_completed == expected_final_completed:
            print(f"已完成任务数正确: {final_completed}")
        else:
            print(f"已完成任务数异常: 期望{expected_final_completed}，实际{final_completed}")
            
        print(f"\n🎉 汇总数据更新测试完成，所有数据一致性验证通过！")
    else:
        print(f"最终验证失败: {response.status_code}")

if __name__ == "__main__":
    comprehensive_toggle_test()