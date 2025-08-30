# 智能出题API接口文档

## 概述

智能出题系统提供完整的REST API接口，支持题目生成、管理、导出和分析等功能。所有接口基于FastAPI框架开发，支持自动生成的OpenAPI文档。

**基础URL**: `http://localhost:8000/api/v1/exercise`

**认证方式**: Bearer Token (JWT)

## API接口列表

### 1. 题目生成相关

#### 1.1 生成智能练习题
```http
POST /generate
```

**请求体**:
```json
{
    "subject": "数学",
    "grade": "三年级", 
    "title": "加法练习题",
    "description": "基础加法运算练习",
    "question_count": 5,
    "difficulty_level": "same",
    "question_types": ["similar"],
    "include_answers": true,
    "include_analysis": true
}
```

**响应**:
```json
{
    "generation_id": 123,
    "status": "pending",
    "message": "题目生成任务已启动，正在处理中",
    "progress_url": "/api/v1/exercise/generation/123"
}
```

#### 1.2 获取生成记录信息
```http
GET /generation/{generation_id}
```

**响应**:
```json
{
    "id": 123,
    "subject": "数学",
    "grade": "三年级",
    "title": "加法练习题",
    "status": "completed",
    "total_questions": 5,
    "progress_percent": 100.0,
    "generation_time": 2.5,
    "created_at": "2024-08-30T10:30:00Z"
}
```

### 2. 题目查询相关

#### 2.1 获取题目列表
```http
GET /generation/{generation_id}/exercises
```

**响应**:
```json
[
    {
        "id": 1,
        "number": 1,
        "subject": "数学",
        "question_text": "计算：12 + 8 = ?",
        "question_type": "similar",
        "correct_answer": "20",
        "analysis": "这是基础加法运算",
        "difficulty": "same",
        "knowledge_points": ["加法运算"],
        "quality_score": 8.5
    }
]
```

#### 2.2 获取用户生成记录列表
```http
GET /generations
```

**查询参数**:
- `subject`: 过滤学科
- `grade`: 过滤年级
- `status`: 过滤状态
- `difficulty_level`: 过滤难度
- `is_favorite`: 过滤收藏状态
- `date_from`: 开始日期
- `date_to`: 结束日期
- `limit`: 每页数量 (1-100)
- `offset`: 偏移量

**响应**:
```json
{
    "records": [...],
    "pagination": {
        "total_count": 50,
        "limit": 20,
        "offset": 0,
        "has_more": true
    }
}
```

### 3. 文件导出相关

#### 3.1 导出题目文件
```http
POST /generation/{generation_id}/export
```

**请求体**:
```json
{
    "format": "word",
    "include_answers": true,
    "include_analysis": true,
    "custom_header": "三年级数学练习",
    "paper_size": "A4"
}
```

**响应**:
```json
{
    "success": true,
    "download_id": 456,
    "download_url": "/api/v1/exercise/download/456",
    "file_name": "exercises_20240830_123456.docx",
    "file_size": 1024,
    "processing_time": 1.2,
    "expires_at": "2024-08-31T10:30:00Z"
}
```

#### 3.2 下载文件
```http
GET /download/{download_id}
```

返回文件流，浏览器自动下载。

#### 3.3 获取下载信息
```http
GET /download/{download_id}/info
```

**响应**:
```json
{
    "id": 456,
    "status": "completed",
    "file_name": "exercises_20240830_123456.docx",
    "download_format": "word",
    "file_size": 1024,
    "is_expired": false,
    "created_at": "2024-08-30T10:30:00Z"
}
```

### 4. 微信分享相关

#### 4.1 微信分享格式化
```http
POST /generation/{generation_id}/share/wechat
```

**请求体**:
```json
{
    "include_answers": false,
    "include_analysis": false,
    "max_questions": 5
}
```

**响应**:
```json
{
    "content": "📚 数学 三年级 练习题\n📝 加法练习题\n\n【题目 1】\n计算：12 + 8 = ?\n\n🤖 由智能AI系统生成",
    "share_link": "https://your-domain.com/share/exercises/abc123"
}
```

### 5. 用户管理相关

#### 5.1 更新收藏状态
```http
PUT /generation/{generation_id}/favorite
```

**请求体**:
```json
{
    "is_favorite": true
}
```

#### 5.2 删除生成记录
```http
DELETE /generation/{generation_id}
```

#### 5.3 获取用户统计
```http
GET /statistics?days=30
```

**响应**:
```json
{
    "summary": {
        "total_generations": 50,
        "completed_generations": 45,
        "total_questions": 250,
        "success_rate": 90.0,
        "avg_generation_time": 2.5
    },
    "subject_distribution": [
        {"subject": "数学", "count": 30},
        {"subject": "语文", "count": 15}
    ],
    "difficulty_distribution": [
        {"difficulty": "same", "count": 25},
        {"difficulty": "easier", "count": 20}
    ]
}
```

#### 5.4 获取每日活动统计
```http
GET /statistics/daily?days=30
```

**响应**:
```json
{
    "activity": [
        {
            "date": "2024-08-30",
            "generation_count": 5,
            "question_count": 25
        }
    ]
}
```

#### 5.5 获取推荐配置
```http
GET /recommendation
```

**响应**:
```json
{
    "subjects": ["数学", "语文"],
    "difficulty_levels": ["same", "easier"],
    "question_counts": [5, 3, 8],
    "optimal_time": "10:00"
}
```

### 6. 配置获取相关

#### 6.1 获取支持的学科列表
```http
GET /config/subjects
```

**响应**:
```json
{
    "subjects": ["数学", "语文", "英语", "物理", "化学"],
    "total_count": 5
}
```

#### 6.2 获取支持的年级列表
```http
GET /config/grades
```

#### 6.3 获取难度等级配置
```http
GET /config/difficulty-levels
```

**响应**:
```json
{
    "difficulty_levels": {
        "easier": {
            "name": "简单",
            "description": "适合基础较弱的学生",
            "coefficient": 0.7
        },
        "same": {
            "name": "相同",
            "description": "与原题难度相同",
            "coefficient": 1.0
        }
    }
}
```

#### 6.4 获取题目类型配置
```http
GET /config/question-types
```

### 7. 下载历史

#### 7.1 获取用户下载历史
```http
GET /downloads?limit=20
```

**响应**:
```json
{
    "downloads": [
        {
            "id": 456,
            "file_name": "exercises_20240830_123456.docx",
            "download_format": "word",
            "status": "completed",
            "file_size": 1024,
            "created_at": "2024-08-30T10:30:00Z",
            "is_expired": false
        }
    ],
    "total_count": 1
}
```

### 8. 管理员接口

#### 8.1 清理过期文件
```http
DELETE /admin/cleanup
```

**响应**:
```json
{
    "success": true,
    "files_cleaned": 10,
    "records_cleaned": 5,
    "message": "清理完成: 10 个文件, 5 条记录"
}
```

## 状态码说明

- `200`: 请求成功
- `400`: 请求参数错误
- `401`: 未授权（token无效或过期）
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

## 错误响应格式

```json
{
    "detail": "错误描述信息"
}
```

## 数据验证规则

### 题目生成请求验证
- `subject`: 必须是支持的学科之一
- `grade`: 必须是支持的年级之一
- `question_count`: 1-50之间的整数
- `difficulty_level`: 必须是 easier/same/harder/mixed 之一

### 导出请求验证
- `format`: 必须是 word/pdf/text 之一
- `paper_size`: 默认为 A4

### 微信分享请求验证
- `max_questions`: 1-10之间的整数

## 使用示例

### Python示例
```python
import requests

# 配置
BASE_URL = "http://localhost:8000/api/v1/exercise"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# 生成题目
response = requests.post(
    f"{BASE_URL}/generate",
    headers=headers,
    json={
        "subject": "数学",
        "grade": "三年级",
        "question_count": 5,
        "difficulty_level": "same"
    }
)

if response.status_code == 200:
    data = response.json()
    generation_id = data["generation_id"]
    print(f"生成任务ID: {generation_id}")
```

### JavaScript示例
```javascript
const BASE_URL = 'http://localhost:8000/api/v1/exercise';
const token = 'YOUR_TOKEN';

// 获取题目列表
async function getExercises(generationId) {
    const response = await fetch(
        `${BASE_URL}/generation/${generationId}/exercises`,
        {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        }
    );
    
    if (response.ok) {
        const exercises = await response.json();
        console.log('题目列表:', exercises);
        return exercises;
    }
}
```

## 注意事项

1. **认证**：所有接口都需要有效的JWT token
2. **限频**：建议实现客户端限频，避免频繁请求
3. **超时**：文件导出和题目生成可能需要较长时间，建议设置合理的超时时间
4. **缓存**：配置信息（学科、年级等）可以在客户端缓存
5. **错误处理**：请实现完善的错误处理机制
6. **文件过期**：导出的文件有24小时有效期，过期后需重新导出

## 自动生成文档

系统支持FastAPI自动生成的交互式文档：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

建议开发时使用这些工具进行接口测试和调试。