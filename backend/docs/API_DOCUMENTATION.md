# 智能教育平台 API 文档

## 📖 概述

智能教育平台提供了一套完整的RESTful API，支持用户认证、作业批改、智能出题、学习计划管理等功能。

**API基础URL**: `http://localhost:8000/api/v1`  
**文档地址**: `http://localhost:8000/docs` (Swagger UI)  
**API版本**: `v1.0.0`

---

## 🔐 认证机制

### JWT Token认证

所有需要认证的API都使用Bearer Token方式：

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

### 获取Token

**POST** `/auth/login`

请求体：
```json
{
  "username": "string",
  "password": "string"
}
```

响应：
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user_info": {
    "id": 1,
    "nickname": "学生用户",
    "role": "student"
  }
}
```

---

## 👤 用户管理 API

### 1. 获取当前用户信息

**GET** `/auth/me`

**权限**: 需要认证

**响应**:
```json
{
  "id": 1,
  "nickname": "学生用户",
  "avatar_url": "/uploads/avatars/user1.jpg",
  "role": "student",
  "grade": "五年级",
  "is_vip": false,
  "daily_quota": 3,
  "daily_used": 1
}
```

### 2. 更新用户信息

**PUT** `/auth/profile`

**权限**: 需要认证

**请求体**:
```json
{
  "nickname": "新昵称",
  "avatar_url": "/uploads/avatars/new_avatar.jpg",
  "phone": "13800138000"
}
```

### 3. 获取VIP状态

**GET** `/user/vip-status`

**权限**: 需要认证

**响应**:
```json
{
  "is_vip": false,
  "vip_type": "free",
  "expire_date": null,
  "remaining_days": 0,
  "daily_quota": 3,
  "remaining_quota": 2
}
```

---

## 📚 作业批改 API

### 1. 上传作业图片

**POST** `/homework/upload`

**权限**: 需要认证

**请求**: `multipart/form-data`
- `file`: 图片文件 (支持 jpg, png, webp 等格式)
- `subject`: 科目 (数学/语文/英语/物理/化学等)
- `grade_level`: 年级 (一年级/二年级/.../高三)

**响应**:
```json
{
  "id": 123,
  "original_image_url": "/uploads/homework/123_original.jpg",
  "subject": "数学",
  "status": "processing",
  "created_at": "2025-01-15T10:30:00Z"
}
```

### 2. 获取批改结果

**GET** `/homework/{homework_id}`

**权限**: 需要认证

**响应**:
```json
{
  "id": 123,
  "status": "completed",
  "subject": "数学",
  "original_image_url": "/uploads/homework/123_original.jpg",
  "processed_image_url": "/uploads/homework/123_processed.jpg",
  "ocr_result": {
    "text": "1. 125 + 237 = 362\n2. 458 - 189 = 269",
    "confidence": 0.95
  },
  "correction_result": {
    "total_questions": 2,
    "correct_count": 1,
    "wrong_count": 1,
    "accuracy_rate": 0.5,
    "corrections": [
      {
        "question_number": 1,
        "user_answer": "362",
        "correct_answer": "362",
        "is_correct": true
      },
      {
        "question_number": 2,
        "user_answer": "269",
        "correct_answer": "269",
        "is_correct": true
      }
    ]
  },
  "processing_time": 2.35,
  "created_at": "2025-01-15T10:30:00Z",
  "completed_at": "2025-01-15T10:32:35Z"
}
```

### 3. 获取作业历史

**GET** `/homework/list`

**权限**: 需要认证

**查询参数**:
- `page`: 页码 (默认1)
- `size`: 每页数量 (默认10)
- `subject`: 科目筛选
- `status`: 状态筛选 (pending/processing/completed/failed)

**响应**:
```json
{
  "items": [
    {
      "id": 123,
      "subject": "数学",
      "status": "completed",
      "accuracy_rate": 0.8,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "size": 10,
  "pages": 2
}
```

---

## 🎯 智能出题 API

### 1. 创建出题任务

**POST** `/exercise/generate`

**权限**: 需要认证 + VIP权限控制

**请求体**:
```json
{
  "subject": "数学",
  "grade": "五年级",
  "title": "小数加减法练习",
  "description": "针对小数点运算的专项训练",
  "question_count": 10,
  "difficulty_level": "medium",
  "question_types": ["填空题", "选择题", "计算题"]
}
```

**响应**:
```json
{
  "id": 456,
  "status": "pending",
  "subject": "数学",
  "grade": "五年级",
  "question_count": 10,
  "estimated_time": 120,
  "created_at": "2025-01-15T11:00:00Z"
}
```

### 2. 获取出题进度

**GET** `/exercise/generate/{generation_id}/progress`

**权限**: 需要认证

**响应**:
```json
{
  "id": 456,
  "status": "generating",
  "progress_percent": 60.0,
  "current_step": "生成第6题",
  "estimated_remaining_time": 48
}
```

### 3. 获取生成的题目

**GET** `/exercise/generate/{generation_id}/questions`

**权限**: 需要认证

**响应**:
```json
{
  "generation_id": 456,
  "status": "completed",
  "questions": [
    {
      "number": 1,
      "question_text": "计算：3.5 + 2.8 = ？",
      "question_type": "计算题",
      "correct_answer": "6.3",
      "analysis": "小数加法需要对齐小数点进行计算...",
      "difficulty": "medium"
    },
    {
      "number": 2,
      "question_text": "下列哪个计算结果正确？\nA. 4.2 - 1.7 = 2.5\nB. 4.2 - 1.7 = 2.6\nC. 4.2 - 1.7 = 3.5",
      "question_type": "选择题",
      "correct_answer": "A",
      "analysis": "4.2 - 1.7 = 2.5，选择A正确..."
    }
  ]
}
```

### 4. 导出题目

**GET** `/exercise/generate/{generation_id}/export`

**权限**: 需要认证

**查询参数**:
- `format`: 导出格式 (pdf/docx/txt) 默认pdf

**响应**: 文件下载

---

## 📅 学习计划 API

### 1. 创建学习计划

**POST** `/study-plan/create`

**权限**: 需要认证

**请求体**:
```json
{
  "title": "期末复习计划",
  "description": "针对期末考试的全面复习",
  "duration_days": 30,
  "daily_time": 60,
  "subjects": ["数学", "语文", "英语"],
  "priority": "high"
}
```

### 2. 获取学习计划列表

**GET** `/study-plan/list`

**权限**: 需要认证

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "title": "期末复习计划",
      "status": "active",
      "progress_percent": 45.2,
      "total_tasks": 15,
      "completed_tasks": 7,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### 3. 获取计划详情

**GET** `/study-plan/{plan_id}`

**权限**: 需要认证

**响应**:
```json
{
  "id": 1,
  "title": "期末复习计划",
  "description": "针对期末考试的全面复习",
  "status": "active",
  "progress_percent": 45.2,
  "tasks": [
    {
      "id": 1,
      "title": "数学第一章复习",
      "subject": "数学",
      "estimated_time": 60,
      "status": "completed",
      "due_date": "2025-01-10"
    }
  ]
}
```

---

## 👨‍💼 家长端 API

### 1. 家长仪表盘

**GET** `/parent/dashboard`

**权限**: 家长角色认证

**响应**:
```json
{
  "children": [
    {
      "id": 1,
      "name": "小明",
      "avatar": "/uploads/avatars/child1.jpg",
      "grade": "五年级",
      "school": "实验小学",
      "class": "五年级1班",
      "status": "active",
      "todayScore": 85,
      "weeklyProgress": {
        "homework_count": 12,
        "accuracy_rate": 0.82,
        "study_time": 180
      }
    }
  ],
  "summary": {
    "total_children": 1,
    "active_plans": 2,
    "this_week_homework": 12
  }
}
```

### 2. 查看孩子详情

**GET** `/parent/child/{child_id}`

**权限**: 家长角色认证

**响应**:
```json
{
  "child_info": {
    "id": 1,
    "name": "小明",
    "grade": "五年级",
    "avatar": "/uploads/avatars/child1.jpg"
  },
  "recent_homework": [
    {
      "id": 123,
      "subject": "数学",
      "accuracy_rate": 0.85,
      "completed_at": "2025-01-15T15:30:00Z"
    }
  ],
  "study_progress": {
    "total_study_time": 1200,
    "subjects_progress": {
      "数学": 85,
      "语文": 78,
      "英语": 90
    }
  }
}
```

---

## 🔧 管理员 API

### 1. 系统统计概览

**GET** `/admin/analytics/overview`

**权限**: 管理员角色

**响应**:
```json
{
  "users": {
    "total": 1250,
    "active_today": 89,
    "new_registrations": 15
  },
  "homework": {
    "processed_today": 234,
    "total_processed": 15678,
    "average_accuracy": 0.78
  },
  "exercise_generation": {
    "generated_today": 56,
    "total_generated": 3456,
    "success_rate": 0.95
  },
  "system_health": {
    "api_response_time": 125.6,
    "error_rate": 0.02,
    "uptime": "99.8%"
  }
}
```

### 2. 用户行为分析

**GET** `/admin/analytics/user-behavior`

**权限**: 管理员角色

**查询参数**:
- `start_date`: 开始日期
- `end_date`: 结束日期
- `user_type`: 用户类型筛选

**响应**:
```json
{
  "active_users_trend": [
    {"date": "2025-01-15", "count": 89},
    {"date": "2025-01-14", "count": 76}
  ],
  "subject_distribution": {
    "数学": 45,
    "语文": 28,
    "英语": 27
  },
  "usage_patterns": {
    "peak_hours": [19, 20, 21],
    "average_session_time": 25.6
  }
}
```

---

## ❌ 错误代码

### HTTP状态码

- `200` - 成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未认证
- `403` - 权限不足
- `404` - 资源不存在
- `429` - 请求过于频繁
- `500` - 服务器内部错误

### 业务错误码

```json
{
  "error": "QUOTA_EXCEEDED",
  "message": "今日出题次数已用完",
  "code": "E1001",
  "details": {
    "daily_quota": 3,
    "used_count": 3,
    "reset_time": "明天00:00"
  }
}
```

常见错误码：
- `E1001` - 配额超限
- `E1002` - VIP权限不足
- `E2001` - 文件格式不支持
- `E2002` - 文件大小超限
- `E3001` - OCR识别失败
- `E3002` - AI生成失败

---

## 🚀 使用示例

### Python示例

```python
import requests

# 登录获取token
login_response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'username': 'demo_student',
    'password': 'password123'
})
token = login_response.json()['access_token']

# 设置请求头
headers = {'Authorization': f'Bearer {token}'}

# 上传作业
with open('homework.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/homework/upload',
        files={'file': f},
        data={'subject': '数学', 'grade_level': '五年级'},
        headers=headers
    )
    
homework_id = response.json()['id']
print(f"作业上传成功，ID: {homework_id}")
```

### JavaScript示例

```javascript
// 登录获取token
const loginResponse = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'demo_student',
        password: 'password123'
    })
});
const { access_token } = await loginResponse.json();

// 创建出题任务
const generateResponse = await fetch('/api/v1/exercise/generate', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        subject: '数学',
        grade: '五年级',
        question_count: 10,
        difficulty_level: 'medium'
    })
});

const generation = await generateResponse.json();
console.log('出题任务创建成功:', generation.id);
```

---

## 📊 速率限制

- **普通用户**: 60请求/分钟
- **VIP用户**: 120请求/分钟
- **管理员**: 无限制

超过限制时返回 `429 Too Many Requests`

---

## 🔄 版本管理

当前版本: `v1.0.0`

API版本通过URL路径管理：
- `/api/v1/` - 当前版本
- `/api/v2/` - 未来版本

旧版本将至少维护12个月，提供充足的迁移时间。

---

更多详细信息请访问：
- **交互式文档**: http://localhost:8000/docs
- **技术支持**: [GitHub Issues](https://github.com/your-repo/issues)