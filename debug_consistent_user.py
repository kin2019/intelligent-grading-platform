#!/usr/bin/env python3
"""
使用同一个用户测试dashboard API和homework API的数据一致性
"""

import requests

def test_same_user_consistency():
    print("=== 测试同一用户的API数据一致性 ===")
    
    # 登录用户18
    login_data = {"code": "test_user_18", "role": "student"}
    response = requests.post("http://localhost:8000/api/v1/auth/wechat/login", json=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    user_id = response.json()["user"]["id"]
    print(f"登录成功，用户ID: {user_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 获取首页dashboard数据
    print("\n1. 获取首页dashboard数据...")
    response = requests.get("http://localhost:8000/api/v1/student/dashboard", headers=headers)
    if response.status_code != 200:
        print(f"获取dashboard数据失败: {response.status_code}")
        return
    
    dashboard_data = response.json()
    homework_list = dashboard_data["recent_homework"]
    
    if homework_list:
        first_homework = homework_list[0]
        homework_id = first_homework["id"]
        print(f"首页第一个作业: ID={homework_id}, 总题数={first_homework['total_questions']}, 错题={first_homework['error_count']}")
        
        # 2. 获取相同ID的作业详情
        print(f"\n2. 获取作业详情: ID={homework_id}")
        response = requests.get(f"http://localhost:8000/api/v1/homework/result/{homework_id}", headers=headers)
        if response.status_code != 200:
            print(f"获取作业详情失败: {response.status_code}")
            return
        
        detail_data = response.json()
        print(f"详情页数据: ID={detail_data['id']}, 总题数={detail_data['total_questions']}, 错题={detail_data['wrong_count']}")
        
        # 3. 比较数据
        print(f"\n3. 数据比较:")
        print(f"  总题数: 首页={first_homework['total_questions']}, 详情={detail_data['total_questions']}, 一致={first_homework['total_questions'] == detail_data['total_questions']}")
        print(f"  错题数: 首页={first_homework['error_count']}, 详情={detail_data['wrong_count']}, 一致={first_homework['error_count'] == detail_data['wrong_count']}")
        
        if first_homework['total_questions'] == detail_data['total_questions'] and first_homework['error_count'] == detail_data['wrong_count']:
            print("  🎉 数据完全一致！")
        else:
            print("  ❌ 数据不一致，需要修复")

if __name__ == "__main__":
    test_same_user_consistency()