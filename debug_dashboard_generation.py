#!/usr/bin/env python3
"""
调试dashboard数据生成逻辑，确定具体的生成算法
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

def generate_sample_homework_data(user_id: int) -> List[Dict[str, Any]]:
    """模拟dashboard API的数据生成逻辑"""
    sample_subjects = ["数学", "语文", "英语", "物理", "化学"]
    sample_data = []
    
    # 基于用户ID和当前日期生成固定的hash值，确保数据一致性
    today_date = datetime.now().strftime('%Y%m%d')  # 格式：20250822
    base_hash = user_id * 10000 + int(today_date) % 10000
    base_seed = user_id * 1000
    
    # 计算今日应该有多少作业（与仪表板逻辑保持一致）
    today_corrections = (base_hash % 5) + 2  # 2-6份作业
    print(f"用户ID: {user_id}")
    print(f"today_date: {today_date}")
    print(f"base_hash: {base_hash}")
    print(f"base_seed: {base_seed}")
    print(f"today_corrections: {today_corrections}")
    
    # 生成更多作业数据，确保有足够的今日作业
    total_homework_count = max(8, today_corrections + 3)  # 至少8个作业
    print(f"total_homework_count: {total_homework_count}")
    
    for i in range(total_homework_count):
        # 使用确定性算法生成固定数据
        homework_hash = base_seed + i * 100
        
        subject = sample_subjects[i % len(sample_subjects)]
        total_q = (homework_hash % 8) + 8  # 8-15题
        
        # 基于hash生成固定的正确率范围60%-95%
        accuracy_hash = (homework_hash // 10) % 36 + 60  # 60-95
        correct_q = int(total_q * (accuracy_hash / 100.0))
        error_q = total_q - correct_q
        
        print(f"作业 {i} (ID={1000+i}): homework_hash={homework_hash}, total_q={total_q}, correct_q={correct_q}, error_q={error_q}")
        
        # 确定日期：前today_corrections个作业是今日的，其余是历史作业
        if i < today_corrections:
            created_date = datetime.now().replace(hour=9 + (i % 8), minute=(i * 13) % 60, second=0, microsecond=0)
            is_today = True
        else:
            days_ago = (i - today_corrections) + 1
            created_date = datetime.now() - timedelta(days=days_ago)
            created_date = created_date.replace(hour=9 + (i % 8), minute=(i * 13) % 60, second=0, microsecond=0)
            is_today = False
        
        sample_data.append({
            "id": 1000 + i,
            "subject": subject,
            "total_questions": total_q,
            "correct_count": correct_q,
            "error_count": error_q,
            "accuracy_rate": round(correct_q / total_q, 2),
            "created_at": created_date.isoformat(),
            "is_today": is_today
        })
    
    return sample_data

# 测试用户18
user_id = 18
print("=== 调试用户18的dashboard数据生成 ===")
sample_data = generate_sample_homework_data(user_id)

print("\n生成的作业数据:")
for hw in sample_data[:3]:  # 只显示前3个
    print(f"  ID={hw['id']}: {hw['subject']}, 总题={hw['total_questions']}, 错题={hw['error_count']}, 今日={hw['is_today']}")

# 特别检查ID=1000的数据
hw_1000 = next((hw for hw in sample_data if hw['id'] == 1000), None)
if hw_1000:
    print(f"\nID=1000的详细数据:")
    print(f"  总题数: {hw_1000['total_questions']}")
    print(f"  错题数: {hw_1000['error_count']}")
    print(f"  正确率: {hw_1000['accuracy_rate']}")