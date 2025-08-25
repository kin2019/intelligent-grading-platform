#!/usr/bin/env python3
"""
专门检查最近作业和详情页面正确率的一致性
"""

import requests

def test_accuracy_rate_consistency():
    print("=== 测试正确率一致性 ===")
    
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
        
        # 首页正确率信息
        homepage_accuracy = first_homework["accuracy_rate"]
        homepage_total = first_homework["total_questions"]
        homepage_correct = first_homework["correct_count"]
        homepage_errors = first_homework["error_count"]
        
        print(f"首页显示:")
        print(f"  作业ID: {homework_id}")
        print(f"  总题数: {homepage_total}")
        print(f"  正确数: {homepage_correct}")  
        print(f"  错题数: {homepage_errors}")
        print(f"  正确率: {homepage_accuracy}")
        
        # 2. 获取相同ID的作业详情
        print(f"\n2. 获取作业详情: ID={homework_id}")
        response = requests.get(f"http://localhost:8000/api/v1/homework/result/{homework_id}", headers=headers)
        if response.status_code != 200:
            print(f"获取作业详情失败: {response.status_code}")
            return
        
        detail_data = response.json()
        
        # 详情页正确率信息
        detail_accuracy = detail_data["accuracy_rate"]
        detail_total = detail_data["total_questions"]
        detail_correct = detail_data["correct_count"]
        detail_errors = detail_data["wrong_count"]
        
        print(f"详情页显示:")
        print(f"  作业ID: {detail_data['id']}")
        print(f"  总题数: {detail_total}")
        print(f"  正确数: {detail_correct}")
        print(f"  错题数: {detail_errors}")
        print(f"  正确率: {detail_accuracy}")
        
        # 3. 比较正确率数据
        print(f"\n3. 正确率数据比较:")
        print(f"  总题数: 首页={homepage_total}, 详情={detail_total}, 一致={homepage_total == detail_total}")
        print(f"  正确数: 首页={homepage_correct}, 详情={detail_correct}, 一致={homepage_correct == detail_correct}")
        print(f"  错题数: 首页={homepage_errors}, 详情={detail_errors}, 一致={homepage_errors == detail_errors}")
        print(f"  正确率: 首页={homepage_accuracy}, 详情={detail_accuracy}, 一致={abs(homepage_accuracy - detail_accuracy) < 0.01}")
        
        # 4. 验证正确率计算
        print(f"\n4. 验证正确率计算:")
        expected_accuracy_homepage = round((homepage_correct / homepage_total) * 100, 1) if homepage_total > 0 else 0
        expected_accuracy_detail = round((detail_correct / detail_total) * 100, 1) if detail_total > 0 else 0
        
        print(f"  首页期望正确率: {expected_accuracy_homepage}% (基于 {homepage_correct}/{homepage_total})")
        print(f"  首页实际正确率: {homepage_accuracy}%")
        print(f"  详情期望正确率: {expected_accuracy_detail}% (基于 {detail_correct}/{detail_total})")
        print(f"  详情实际正确率: {detail_accuracy}%")
        
        # 检查correction_results
        if 'correction_results' in detail_data:
            correction_results = detail_data['correction_results']
            actual_correct = sum(1 for q in correction_results if q['is_correct'])
            actual_total = len(correction_results)
            actual_accuracy = round((actual_correct / actual_total) * 100, 1) if actual_total > 0 else 0
            
            print(f"\n5. 题目详情验证:")
            print(f"  题目列表总数: {actual_total}")
            print(f"  题目列表正确: {actual_correct}")
            print(f"  题目列表正确率: {actual_accuracy}%")
            
            if actual_accuracy == detail_accuracy:
                print("  ✓ 详情页统计与题目列表一致")
            else:
                print("  ✗ 详情页统计与题目列表不一致")
        
        # 总结
        print(f"\n6. 总结:")
        accuracy_consistent = abs(homepage_accuracy - detail_accuracy) < 0.01
        data_consistent = (homepage_total == detail_total and 
                          homepage_correct == detail_correct and 
                          homepage_errors == detail_errors)
        
        if accuracy_consistent and data_consistent:
            print("  ✓ 所有正确率数据完全一致！")
            return True
        else:
            print("  ✗ 发现正确率数据不一致")
            if not accuracy_consistent:
                print(f"    - 正确率不一致: 首页={homepage_accuracy}%, 详情={detail_accuracy}%")
            if not data_consistent:
                print("    - 基础数据不一致")
            return False
    else:
        print("  没有作业数据可测试")
        return False

if __name__ == "__main__":
    success = test_accuracy_rate_consistency()
    exit(0 if success else 1)