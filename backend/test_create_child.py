#!/usr/bin/env python3

import requests
import json

# Test create child API
url = "http://localhost:8000/api/v1/parent/children"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTYwMzI4NjcsInN1YiI6InBhcmVudF8zMSJ9.utPQFw-KRGanFg-KTR3ps0jir_OemptMLqF9yHsmguc",
    "Content-Type": "application/json"
}
data = {
    "nickname": "测试小孩",
    "grade": "四年级", 
    "school": "测试小学",
    "avatar_url": "emoji:😊"
}

print("Testing create child API...")
response = requests.post(url, headers=headers, json=data)
print(f"Status: {response.status_code}")
try:
    print(f"Response: {response.text}")
except:
    print(f"Response (bytes): {response.content}")

if response.status_code == 200:
    print("✅ Child created successfully!")
    result = response.json()
    child_id = result.get('id')
    
    # Test dashboard to see if child appears
    print(f"\nTesting dashboard API to see if child ID {child_id} appears...")
    dashboard_response = requests.get("http://localhost:8000/api/v1/parent/dashboard", headers=headers)
    print(f"Dashboard status: {dashboard_response.status_code}")
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()
        children = dashboard_data.get('children', [])
        print(f"Children found: {len(children)}")
        for child in children:
            print(f"  - ID: {child.get('id')}, Name: {child.get('name')}, Grade: {child.get('grade')}")
else:
    print(f"❌ Failed to create child: {response.text}")