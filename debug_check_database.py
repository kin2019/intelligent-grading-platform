#!/usr/bin/env python3
"""
检查数据库中是否有真实的homework数据
"""

import requests

def check_real_homework_data():
    print("=== 检查数据库中的真实homework数据 ===")
    
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
    
    # 检查homework list API
    print("\n1. 检查homework list API...")
    response = requests.get("http://localhost:8000/api/v1/homework/list", headers=headers)
    if response.status_code == 200:
        homework_list = response.json()
        print(f"homework list API返回: {len(homework_list)}个作业")
        if homework_list:
            for hw in homework_list[:3]:
                print(f"  ID={hw['id']}, 总题数={hw['total_questions']}, 正确率={hw['accuracy_rate']}")
    else:
        print(f"homework list API失败: {response.status_code}")

if __name__ == "__main__":
    check_real_homework_data()