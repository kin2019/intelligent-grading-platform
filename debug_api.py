#!/usr/bin/env python3
import requests

# 登录
login_data = {"code": "test_user_18", "role": "student"}
response = requests.post("http://localhost:8000/api/v1/auth/wechat/login", json=login_data)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 获取首页第一个作业
response = requests.get("http://localhost:8000/api/v1/student/dashboard", headers=headers)
homework_list = response.json()["recent_homework"]
first_homework = homework_list[0]

print(f"首页第一个作业: ID={first_homework['id']}, 总题数={first_homework['total_questions']}, 错题={first_homework['error_count']}")

# 获取详情页数据
homework_id = first_homework['id']
response = requests.get(f"http://localhost:8000/api/v1/homework/result/{homework_id}", headers=headers)
detail_data = response.json()

print(f"详情页数据: ID={detail_data['id']}, 总题数={detail_data['total_questions']}, 错题={detail_data['wrong_count']}")

# 检查correction_results
if 'correction_results' in detail_data:
    results = detail_data['correction_results']
    print(f"题目详情: 共{len(results)}题")
    correct_count = sum(1 for q in results if q['is_correct'])
    wrong_count = len(results) - correct_count
    print(f"题目统计: 正确{correct_count}题, 错误{wrong_count}题")