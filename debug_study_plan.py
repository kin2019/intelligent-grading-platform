#!/usr/bin/env python3
"""
Debug script to check study plan data
"""
import requests
import json

API_BASE = 'http://localhost:8000/api/v1'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTYxMDAwMjMsInN1YiI6IjEifQ.R_dHdA1lUTRzyBIGxCPk6UrO7kiucBwSl3R_PHieRn8'

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

def test_study_plan_api():
    """Test the study plan API"""
    print("=== 测试学习计划API ===")
    
    response = requests.get(f'{API_BASE}/student/study-plan', headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Plan ID: {data.get('plan_id')}")
        print(f"Title: {data.get('title')}")
        print(f"Subjects: {[s.get('subject') for s in data.get('subjects', [])]}")
        print(f"Tasks count: {len(data.get('tasks', []))}")
        print(f"All tasks count: {len(data.get('all_tasks', []))}")
        print(f"Recommendations count: {len(data.get('recommendations', []))}")
        print("API working correctly!")
    else:
        print(f"Error: {response.text}")

def create_test_plan():
    """Create a test plan"""
    print("\n=== 创建测试学习计划 ===")
    
    plan_data = {
        "title": "Debug测试计划",
        "description": "用于调试的测试学习计划",
        "subjects": ["chinese"],
        "priority": "medium",
        "duration_days": 3,
        "daily_time": 20,
        "tasks": [
            {"title": "测试任务1", "subject": "chinese", "estimatedTime": 10},
            {"title": "测试任务2", "subject": "chinese", "estimatedTime": 10}
        ],
        "estimated_time": 20
    }
    
    response = requests.post(f'{API_BASE}/student/study-plan-create', 
                           headers=headers, 
                           json=plan_data)
    
    print(f"Create Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Created Plan ID: {result.get('plan_id')}")
        print(f"Created Title: {result.get('title')}")
    else:
        print(f"Create Error: {response.text}")
    
    return response.status_code == 200

if __name__ == "__main__":
    # First test current plan
    test_study_plan_api()
    
    # Create a new plan
    if create_test_plan():
        print("\n=== 创建后重新测试API ===")
        # Wait a moment and test again
        import time
        time.sleep(1)
        test_study_plan_api()