# 智能教育平台 - 管理员操作指南

## 🎯 管理员职责概述

作为智能教育平台的管理员，您负责平台的日常运维、用户管理、数据监控和系统配置。本指南将帮助您高效地管理平台。

---

## 🚀 系统部署

### 初始部署

1. **环境准备**
   ```bash
   # 检查Python版本（需要3.11+）
   python --version
   
   # 进入项目目录
   cd /path/to/zyjc/backend
   
   # 运行自动部署脚本
   python scripts/deploy.py --env production
   ```

2. **配置环境变量**
   ```bash
   # 复制配置模板
   cp .env.example .env
   
   # 编辑配置文件（重要：修改以下配置）
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=sqlite:///./app.db
   ENVIRONMENT=production
   ```

3. **数据库初始化**
   ```bash
   # 运行数据库迁移脚本
   python scripts/db_migration.py
   
   # 验证数据库创建成功
   ls -la *.db
   ```

4. **启动服务**
   ```bash
   # 开发环境
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # 生产环境
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### 服务器配置推荐

#### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 50GB SSD
- **网络**: 10Mbps带宽

#### 推荐配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 100GB SSD
- **网络**: 100Mbps带宽

---

## 👤 用户管理

### 用户查看和筛选

#### 通过API查看用户列表

```bash
# 获取所有用户
curl -X GET "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 筛选特定角色用户
curl -X GET "http://localhost:8000/api/v1/admin/users?role=student" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 查看VIP用户
curl -X GET "http://localhost:8000/api/v1/admin/users?is_vip=true" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### 直接数据库查询

```bash
# 连接数据库
sqlite3 app.db

# 查看用户统计
SELECT role, COUNT(*) as count FROM users GROUP BY role;

# 查看VIP用户
SELECT id, nickname, role, is_vip, vip_expire_time FROM users WHERE is_vip = 1;

# 查看活跃用户（近7天有登录）
SELECT id, nickname, role, last_login_at FROM users 
WHERE last_login_at > datetime('now', '-7 days');
```

### 用户权限管理

#### 设置VIP用户

```sql
-- 通过SQL设置用户为VIP（30天）
UPDATE users SET 
  is_vip = 1, 
  vip_expire_time = datetime('now', '+30 days'),
  daily_quota = -1
WHERE id = USER_ID;

-- 取消用户VIP
UPDATE users SET 
  is_vip = 0, 
  vip_expire_time = NULL,
  daily_quota = 3
WHERE id = USER_ID;
```

#### 调整用户配额

```sql
-- 增加特定用户的每日配额
UPDATE users SET daily_quota = 10 WHERE id = USER_ID;

-- 重置用户每日使用次数
UPDATE users SET daily_used = 0 WHERE id = USER_ID;

-- 批量重置所有用户每日使用次数（每日维护）
UPDATE users SET daily_used = 0, last_quota_reset = date('now');
```

### 用户行为监控

#### 查看用户活动统计

```sql
-- 今日活跃用户
SELECT COUNT(*) as active_users FROM users 
WHERE DATE(last_login_at) = DATE('now');

-- 用户注册趋势（近30天）
SELECT DATE(created_at) as date, COUNT(*) as registrations 
FROM users 
WHERE created_at > datetime('now', '-30 days')
GROUP BY DATE(created_at)
ORDER BY date;

-- 各科目使用情况
SELECT subject, COUNT(*) as usage_count 
FROM homework 
WHERE created_at > datetime('now', '-7 days')
GROUP BY subject
ORDER BY usage_count DESC;
```

#### 异常用户识别

```sql
-- 查找异常高频使用用户
SELECT u.id, u.nickname, u.daily_used, u.total_used
FROM users u
WHERE u.daily_used > 20 OR u.total_used > 500
ORDER BY u.daily_used DESC;

-- 查找可能的虚假账户
SELECT id, nickname, created_at, last_login_at
FROM users
WHERE last_login_at IS NULL AND created_at < datetime('now', '-7 days');
```

---

## 📊 系统监控与分析

### 系统健康检查

#### 服务状态检查

```bash
# 检查服务是否运行
curl -X GET "http://localhost:8000/health"

# 检查数据库连接
curl -X GET "http://localhost:8000/api/v1/admin/health/database"

# 检查磁盘空间
df -h

# 检查内存使用
free -h

# 检查进程状态
ps aux | grep uvicorn
```

#### 性能监控

```sql
-- 数据库性能监控
.timer on
.headers on

-- 慢查询识别
EXPLAIN QUERY PLAN SELECT * FROM homework 
WHERE user_id = 1 AND created_at > datetime('now', '-30 days');

-- 数据库大小统计
SELECT 
  name,
  COUNT(*) as record_count
FROM sqlite_master 
WHERE type='table' 
GROUP BY name;
```

### 业务数据分析

#### 使用统计报告

```sql
-- 每日业务统计
SELECT 
  DATE(created_at) as date,
  COUNT(*) as homework_count,
  AVG(accuracy_rate) as avg_accuracy
FROM homework 
WHERE created_at > datetime('now', '-30 days')
GROUP BY DATE(created_at)
ORDER BY date;

-- 用户留存分析
SELECT 
  DATE(u.created_at) as reg_date,
  COUNT(*) as new_users,
  COUNT(CASE WHEN u.last_login_at > datetime('now', '-7 days') THEN 1 END) as active_users
FROM users u
WHERE u.created_at > datetime('now', '-30 days')
GROUP BY DATE(u.created_at);

-- VIP转化率统计
SELECT 
  COUNT(CASE WHEN is_vip = 0 THEN 1 END) as free_users,
  COUNT(CASE WHEN is_vip = 1 THEN 1 END) as vip_users,
  ROUND(COUNT(CASE WHEN is_vip = 1 THEN 1 END) * 100.0 / COUNT(*), 2) as vip_rate
FROM users;
```

#### 收入分析（如果有支付功能）

```sql
-- 假设有payments表的情况
-- 每日收入统计
SELECT 
  DATE(created_at) as date,
  COUNT(*) as order_count,
  SUM(amount) as total_revenue
FROM payments 
WHERE status = 'success' AND created_at > datetime('now', '-30 days')
GROUP BY DATE(created_at);

-- VIP订阅分析
SELECT 
  plan_type,
  COUNT(*) as subscription_count,
  SUM(amount) as revenue
FROM payments 
WHERE status = 'success' AND plan_type IS NOT NULL
GROUP BY plan_type;
```

---

## 🔧 系统配置管理

### 配置文件管理

#### 主配置文件 (.env)

```bash
# 生产环境关键配置
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ENVIRONMENT=production

# 数据库配置
DATABASE_URL=sqlite:///./app.db

# 安全配置
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ALGORITHM=HS256

# VIP系统配置
DEFAULT_DAILY_QUOTA=3
VIP_UNLIMITED_QUOTA=-1

# 文件上传限制
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.bmp,.webp

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

#### 动态配置更新

```python
# 通过Python脚本更新配置
import os
from app.core.config import settings

# 查看当前配置
print(f"当前每日配额: {settings.DEFAULT_DAILY_QUOTA}")
print(f"当前环境: {settings.ENVIRONMENT}")

# 修改配置需要重启服务
```

### 系统参数调优

#### 数据库优化

```sql
-- SQLite性能优化
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = memory;

-- 清理和优化数据库
VACUUM;
ANALYZE;
```

#### 日志管理

```bash
# 日志轮转配置
# 创建logrotate配置文件
cat > /etc/logrotate.d/zyjc-platform << EOF
/path/to/zyjc/backend/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    create 644 www-data www-data
    postrotate
        systemctl reload zyjc-platform
    endscript
}
EOF

# 手动清理旧日志
find logs/ -name "*.log" -mtime +30 -delete
```

---

## 🛡️ 安全管理

### 访问控制

#### 管理员账户管理

```sql
-- 创建管理员账户
INSERT INTO users (openid, nickname, role, is_active, is_verified) 
VALUES ('admin_001', '系统管理员', 'admin', 1, 1);

-- 查看所有管理员
SELECT id, nickname, role, is_active, created_at 
FROM users WHERE role = 'admin';

-- 禁用管理员账户
UPDATE users SET is_active = 0 WHERE id = ADMIN_ID AND role = 'admin';
```

#### 安全日志监控

```bash
# 查看登录失败日志
grep "LOGIN_FAILED" logs/app.log | tail -20

# 查看异常API调用
grep "403\|401" logs/app.log | tail -20

# 监控大文件上传
grep "FILE_UPLOAD" logs/app.log | grep -E "size:[0-9]{8,}" | tail -10
```

### 数据备份与恢复

#### 数据备份策略

```bash
#!/bin/bash
# backup.sh - 数据备份脚本

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/zyjc"
DB_FILE="app.db"
UPLOAD_DIR="uploads"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
echo "备份数据库..."
cp $DB_FILE "$BACKUP_DIR/app_$DATE.db"

# 备份上传文件
echo "备份上传文件..."
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" $UPLOAD_DIR

# 清理7天前的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $DATE"
```

#### 数据恢复

```bash
#!/bin/bash
# restore.sh - 数据恢复脚本

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <backup_file.db>"
    exit 1
fi

# 停止服务
echo "停止服务..."
pkill -f uvicorn

# 备份当前数据库
cp app.db app.db.backup.$(date +%Y%m%d_%H%M%S)

# 恢复数据库
echo "恢复数据库..."
cp "$BACKUP_FILE" app.db

# 启动服务
echo "启动服务..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

echo "恢复完成"
```

---

## 📈 运营数据分析

### 关键指标监控

#### 用户增长指标

```sql
-- 用户增长趋势
WITH daily_stats AS (
  SELECT 
    DATE(created_at) as date,
    COUNT(*) as new_users
  FROM users 
  WHERE created_at > datetime('now', '-30 days')
  GROUP BY DATE(created_at)
),
cumulative AS (
  SELECT 
    date,
    new_users,
    SUM(new_users) OVER (ORDER BY date) as total_users
  FROM daily_stats
)
SELECT * FROM cumulative ORDER BY date;

-- 用户活跃度分析
SELECT 
  CASE 
    WHEN last_login_at > datetime('now', '-1 days') THEN 'Today'
    WHEN last_login_at > datetime('now', '-7 days') THEN 'This Week'
    WHEN last_login_at > datetime('now', '-30 days') THEN 'This Month'
    ELSE 'Inactive'
  END as activity_level,
  COUNT(*) as user_count
FROM users
GROUP BY activity_level;
```

#### 功能使用分析

```sql
-- 作业批改功能使用统计
SELECT 
  subject,
  COUNT(*) as usage_count,
  AVG(accuracy_rate) as avg_accuracy,
  AVG(processing_time) as avg_processing_time
FROM homework 
WHERE status = 'completed' AND created_at > datetime('now', '-30 days')
GROUP BY subject
ORDER BY usage_count DESC;

-- 智能出题功能使用统计
SELECT 
  subject,
  grade,
  COUNT(*) as generation_count,
  AVG(question_count) as avg_questions,
  AVG(generation_time) as avg_generation_time
FROM exercise_generations
WHERE status = 'completed' AND created_at > datetime('now', '-30 days')
GROUP BY subject, grade
ORDER BY generation_count DESC;
```

#### VIP转化分析

```sql
-- VIP转化漏斗分析
SELECT 
  'Total Users' as stage,
  COUNT(*) as count
FROM users
UNION ALL
SELECT 
  'Used Free Quota' as stage,
  COUNT(DISTINCT user_id) as count
FROM homework
UNION ALL
SELECT 
  'Reached Quota Limit' as stage,
  COUNT(*) as count
FROM users WHERE daily_used >= daily_quota
UNION ALL
SELECT 
  'VIP Users' as stage,
  COUNT(*) as count
FROM users WHERE is_vip = 1;
```

### 报表生成

#### 周报生成脚本

```python
#!/usr/bin/env python3
# weekly_report.py

import sqlite3
from datetime import datetime, timedelta
import json

def generate_weekly_report():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    report = {
        "period": f"{start_date.date()} to {end_date.date()}",
        "generated_at": end_date.isoformat()
    }
    
    # 用户增长
    cursor.execute("""
        SELECT COUNT(*) FROM users 
        WHERE created_at BETWEEN ? AND ?
    """, (start_date, end_date))
    report["new_users"] = cursor.fetchone()[0]
    
    # 活跃用户
    cursor.execute("""
        SELECT COUNT(*) FROM users 
        WHERE last_login_at BETWEEN ? AND ?
    """, (start_date, end_date))
    report["active_users"] = cursor.fetchone()[0]
    
    # 作业处理量
    cursor.execute("""
        SELECT COUNT(*), AVG(accuracy_rate) FROM homework 
        WHERE created_at BETWEEN ? AND ? AND status = 'completed'
    """, (start_date, end_date))
    result = cursor.fetchone()
    report["homework_count"] = result[0]
    report["avg_accuracy"] = round(result[1] or 0, 2)
    
    # 智能出题量
    cursor.execute("""
        SELECT COUNT(*), SUM(question_count) FROM exercise_generations 
        WHERE created_at BETWEEN ? AND ? AND status = 'completed'
    """, (start_date, end_date))
    result = cursor.fetchone()
    report["exercise_generations"] = result[0]
    report["total_questions_generated"] = result[1] or 0
    
    # VIP用户数
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
    report["vip_users"] = cursor.fetchone()[0]
    
    conn.close()
    
    # 输出报告
    print("=" * 50)
    print("智能教育平台 - 周度运营报告")
    print("=" * 50)
    print(f"报告期间: {report['period']}")
    print(f"生成时间: {report['generated_at']}")
    print()
    print(f"新增用户: {report['new_users']}")
    print(f"活跃用户: {report['active_users']}")
    print(f"作业处理: {report['homework_count']} 份")
    print(f"平均准确率: {report['avg_accuracy']}%")
    print(f"智能出题: {report['exercise_generations']} 次")
    print(f"生成题目: {report['total_questions_generated']} 题")
    print(f"VIP用户: {report['vip_users']} 人")
    print("=" * 50)
    
    # 保存JSON格式报告
    with open(f"weekly_report_{start_date.date()}.json", 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    generate_weekly_report()
```

---

## 🚨 故障处理

### 常见问题排查

#### 服务无法启动

```bash
# 检查端口占用
lsof -i :8000

# 检查数据库文件权限
ls -la *.db

# 查看详细错误信息
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug

# 检查依赖包
pip list | grep -E "(fastapi|uvicorn|sqlalchemy)"
```

#### 数据库连接问题

```bash
# 检查数据库文件是否存在
ls -la app.db

# 测试数据库连接
sqlite3 app.db "SELECT COUNT(*) FROM users;"

# 检查数据库锁定
lsof app.db

# 数据库完整性检查
sqlite3 app.db "PRAGMA integrity_check;"
```

#### 性能问题

```sql
-- 检查慢查询
EXPLAIN QUERY PLAN SELECT * FROM homework WHERE user_id = 1;

-- 检查索引使用
.schema users
SELECT name FROM sqlite_master WHERE type='index';

-- 数据库统计信息
ANALYZE;
SELECT * FROM sqlite_stat1;
```

### 应急处理流程

#### 服务宕机处理

1. **立即响应**
   ```bash
   # 检查服务状态
   ps aux | grep uvicorn
   
   # 重启服务
   pkill -f uvicorn
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
   ```

2. **数据备份**
   ```bash
   # 立即备份当前数据
   cp app.db app.db.emergency.$(date +%Y%m%d_%H%M%S)
   ```

3. **问题定位**
   ```bash
   # 查看错误日志
   tail -f logs/app.log
   
   # 系统资源检查
   top
   df -h
   free -h
   ```

#### 数据恢复程序

1. **评估数据损坏程度**
2. **选择合适的备份文件**
3. **在测试环境验证恢复**
4. **正式环境恢复操作**
5. **服务重启和验证**

---

## 📋 日常维护检查清单

### 每日检查

- [ ] 服务运行状态正常
- [ ] 数据库连接正常
- [ ] 磁盘空间充足（>20%）
- [ ] 内存使用正常（<80%）
- [ ] 错误日志无异常
- [ ] 用户反馈处理

### 每周检查

- [ ] 生成运营周报
- [ ] 数据库完整性检查
- [ ] 清理临时文件
- [ ] 更新系统补丁
- [ ] 备份数据验证
- [ ] 性能指标分析

### 每月检查

- [ ] 全面系统备份
- [ ] 用户数据清理
- [ ] 配置参数优化
- [ ] 安全审计
- [ ] 容量规划评估
- [ ] 用户满意度调研

---

## 📞 支持与联系

### 技术支持

- **内部技术团队**: tech-team@company.com
- **系统监控告警**: alerts@company.com
- **紧急联系电话**: +86-xxx-xxxx-xxxx

### 文档更新

本文档会根据系统更新持续完善，最新版本请查看：
- **内部文档系统**: http://docs.internal.com
- **版本控制**: Git仓库 `/docs` 目录

---

## 📚 附录

### 常用SQL查询

```sql
-- 用户统计查询集合
-- 总用户数
SELECT COUNT(*) as total_users FROM users;

-- 各角色用户分布
SELECT role, COUNT(*) as count FROM users GROUP BY role;

-- 今日新增用户
SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now');

-- VIP到期用户（未来7天）
SELECT id, nickname, vip_expire_time 
FROM users 
WHERE is_vip = 1 AND vip_expire_time BETWEEN datetime('now') AND datetime('now', '+7 days');

-- 系统负载统计
SELECT 
  DATE(created_at) as date,
  COUNT(*) as homework_count,
  COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
  AVG(processing_time) as avg_processing_time
FROM homework 
WHERE created_at > datetime('now', '-30 days')
GROUP BY DATE(created_at)
ORDER BY date;
```

### 环境变量完整列表

| 变量名 | 说明 | 默认值 | 生产环境建议 |
|--------|------|--------|-------------|
| SECRET_KEY | JWT密钥 | 示例密钥 | 强随机密钥 |
| DEBUG | 调试模式 | True | False |
| ENVIRONMENT | 环境标识 | development | production |
| DATABASE_URL | 数据库地址 | sqlite:///./app.db | 保持不变 |
| DEFAULT_DAILY_QUOTA | 每日免费配额 | 3 | 3-5 |
| LOG_LEVEL | 日志级别 | INFO | INFO |
| MAX_FILE_SIZE | 文件大小限制 | 10485760 | 适当调整 |

管理员操作指南完成！记住：谨慎操作，定期备份，持续监控。🛡️