#!/usr/bin/env python3
import requests

# 登录用户18
login_data = {"code": "test_user_18", "role": "student"}
response = requests.post("http://localhost:8000/api/v1/auth/wechat/login", json=login_data)
token = response.json()["access_token"]
user_id = response.json()["user"]["id"]
print(f"登录成功，用户ID: {user_id}")

headers = {"Authorization": f"Bearer {token}"}

# 直接调用homework详情API
homework_id = 1000
print(f"\n调用homework API: /api/v1/homework/result/{homework_id}")
response = requests.get(f"http://localhost:8000/api/v1/homework/result/{homework_id}", headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"homework API返回: total_questions={data['total_questions']}, wrong_count={data['wrong_count']}")
    if 'correction_results' in data:
        results = data['correction_results']
        actual_wrong = sum(1 for q in results if not q['is_correct'])
        print(f"题目详情验证: 共{len(results)}题, 实际错误{actual_wrong}题")
else:
    print(f"API调用失败: {response.status_code} - {response.text}")