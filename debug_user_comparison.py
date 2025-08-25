#!/usr/bin/env python3
"""
比较不同用户ID的计算结果，找出差异根源
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

def debug_user_calculation(user_id: int, label: str):
    """调试特定用户ID的计算过程"""
    print(f"\n=== {label} (user_id={user_id}) ===")
    
    sample_subjects = ["数学", "语文", "英语", "物理", "化学"]
    
    # 基于用户ID和当前日期生成固定的hash值，确保数据一致性
    today_date = datetime.now().strftime('%Y%m%d')  # 格式：20250823
    base_hash = user_id * 10000 + int(today_date) % 10000
    base_seed = user_id * 1000
    
    print(f"today_date: {today_date}")
    print(f"base_hash: {base_hash}")
    print(f"base_seed: {base_seed}")
    
    # 计算今日应该有多少作业（与仪表板逻辑保持一致）
    today_corrections = (base_hash % 5) + 2  # 2-6份作业
    print(f"today_corrections: {today_corrections}")
    
    # 针对作业ID=1000，计算详细参数
    index = 0  # homework_id=1000 对应 index=0
    homework_hash = base_seed + index * 100
    
    subject = sample_subjects[index % len(sample_subjects)]
    total_q = (homework_hash % 8) + 8  # 8-15题
    
    # 基于hash生成固定的正确率范围60%-95%
    accuracy_hash = (homework_hash // 10) % 36 + 60  # 60-95
    correct_q = int(total_q * (accuracy_hash / 100.0))
    error_q = total_q - correct_q
    
    print(f"作业ID=1000的计算:")
    print(f"  index: {index}")
    print(f"  homework_hash: {homework_hash}")
    print(f"  subject: {subject}")
    print(f"  total_q: {total_q}")
    print(f"  accuracy_hash: {accuracy_hash}")
    print(f"  correct_q: {correct_q}")
    print(f"  error_q: {error_q}")
    
    return {
        "total_questions": total_q,
        "correct_count": correct_q,
        "wrong_count": error_q,
        "accuracy_rate": round((correct_q / total_q) * 100, 1)
    }

# 比较两个用户ID的计算结果
print("=== 用户ID计算结果比较 ===")

result_18 = debug_user_calculation(18, "模拟用户18")
result_19 = debug_user_calculation(19, "实际用户19")

print(f"\n=== 结果对比 ===")
print(f"用户18结果: 总题数={result_18['total_questions']}, 错题={result_18['wrong_count']}, 正确率={result_18['accuracy_rate']}")
print(f"用户19结果: 总题数={result_19['total_questions']}, 错题={result_19['wrong_count']}, 正确率={result_19['accuracy_rate']}")

if result_18 == result_19:
    print("✓ 两个用户的计算结果完全一致")
else:
    print("✗ 两个用户的计算结果不一致")
    for key in result_18:
        if result_18[key] != result_19[key]:
            print(f"  差异: {key} -> 用户18: {result_18[key]}, 用户19: {result_19[key]}")