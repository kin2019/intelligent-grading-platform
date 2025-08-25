# 中小学全学科智能批改平台 - 后端服务

这是一个基于微服务架构的智能教育平台后端系统，支持数学、语文、英语等多学科的智能批改功能。

## 🏗️ 项目架构

### 技术栈
- **框架**: FastAPI + Python 3.9+
- **数据库**: PostgreSQL (主库) + Redis (缓存) + MongoDB (题库)
- **AI服务**: OpenAI GPT-4, Claude, 百度文心一言
- **OCR服务**: PaddleOCR, MathPix, 百度OCR, 阿里云OCR
- **文件存储**: 阿里云OSS + CDN
- **消息队列**: RabbitMQ
- **监控**: Prometheus + Grafana
- **部署**: Docker + Kubernetes

### 微服务架构
```
backend/
├── gateway/                    # API网关
├── services/                   # 微服务集群
│   ├── user-service/          # 用户服务
│   ├── subject-services/      # 学科服务集群
│   │   ├── math-service/      # 数学批改服务
│   │   ├── chinese-service/   # 语文批改服务
│   │   ├── english-service/   # 英语批改服务
│   │   └── science-service/   # 理科批改服务
│   ├── ocr-service/           # OCR识别服务
│   ├── analysis-service/      # 学情分析服务
│   ├── generator-service/     # 错题生成服务
│   ├── payment-service/       # 支付服务
│   └── notification-service/  # 通知服务
├── shared/                    # 共享模块
│   ├── models/               # 数据模型
│   ├── utils/                # 工具函数
│   └── config/               # 配置管理
└── data/                     # 数据脚本
```

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7
- MongoDB 7

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd zyjc-backend
```

2. **环境配置**
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件，填入相应的API密钥和数据库连接信息
vim .env
```

3. **Docker 部署**
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f gateway
```

4. **开发环境安装**
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements/common.txt
pip install -r requirements/math.txt
pip install -r requirements/chinese.txt
pip install -r requirements/english.txt

# 数据库初始化
python -m alembic upgrade head
```

### 服务端口分配
- API网关: 8000
- 用户服务: 8001
- 数学服务: 8002
- 语文服务: 8003
- 英语服务: 8004
- OCR服务: 8005
- 分析服务: 8006
- 生成服务: 8007
- 支付服务: 8008
- 通知服务: 8009

## 📝 API 文档

### 认证接口
```
POST /auth/login          # 微信登录
POST /auth/refresh        # 刷新Token
POST /auth/logout         # 登出
GET  /auth/me            # 获取用户信息
```

### 用户管理
```
GET    /api/users/me                    # 获取当前用户信息
PUT    /api/users/me                    # 更新用户信息
GET    /api/users/{user_id}             # 获取用户信息
GET    /api/users/{user_id}/statistics  # 获取用户统计
```

### 学生管理
```
POST   /api/students/           # 创建学生
GET    /api/students/           # 获取学生列表
GET    /api/students/{id}       # 获取学生详情
PUT    /api/students/{id}       # 更新学生信息
DELETE /api/students/{id}       # 删除学生
```

### 作业批改
```
POST   /api/homework/submit     # 提交作业
GET    /api/homework/{id}       # 获取批改结果
GET    /api/homework/           # 获取作业历史
POST   /api/homework/{id}/retry # 重新批改
```

### 错题管理
```
GET    /api/errors/             # 获取错题列表
GET    /api/errors/{id}         # 获取错题详情
POST   /api/errors/{id}/practice # 练习错题
PUT    /api/errors/{id}/master  # 标记已掌握
```

## 🔧 核心功能

### 1. 多学科批改引擎

#### 数学批改
- **四则运算**: 支持整数、小数、分数运算
- **代数运算**: 方程求解、不等式
- **几何运算**: 面积、周长、体积计算
- **函数运算**: 函数值计算、图像分析

#### 语文批改
- **拼音检查**: 声母韵母识别和纠错
- **汉字识别**: 笔画顺序、字形结构
- **阅读理解**: 关键词提取、答案匹配
- **作文批改**: 语法检查、结构分析

#### 英语批改
- **拼写检查**: 单词拼写错误检测
- **语法检查**: 时态、语态、句式
- **发音评测**: 语音识别和发音评分
- **作文批改**: 语法、词汇、逻辑

### 2. 智能错题生成
- 根据错题类型生成相似题目
- 难度自适应调整
- 知识点关联推荐
- 个性化练习计划

### 3. 学情分析
- 学习进度跟踪
- 知识点掌握分析
- 薄弱环节识别
- 学习建议生成

### 4. OCR识别优化
- 数学公式识别
- 手写文字识别
- 图表信息提取
- 多种格式支持

## 🛠️ 开发指南

### 代码结构
```python
# 示例：数学批改引擎
from engines.arithmetic import ArithmeticEngine

engine = ArithmeticEngine()
result = engine.parse_expression("23 + 45 = 68")

# 返回结果
{
    "is_correct": True,
    "operation_type": "addition",
    "operand1": 23,
    "operand2": 45,
    "user_answer": 68,
    "correct_answer": 68
}
```

### 添加新学科
1. 在 `services/subject-services/` 下创建新的学科服务
2. 实现对应的批改引擎
3. 在API网关中注册路由
4. 添加相应的数据模型

### 扩展批改引擎
1. 继承 `BaseEngine` 类
2. 实现 `parse_expression` 方法
3. 添加错误分析逻辑
4. 集成到对应的学科服务中

## 🧪 测试

### 运行测试
```bash
# 单元测试
python -m pytest tests/unit/

# 集成测试
python -m pytest tests/integration/

# 性能测试
python -m pytest tests/performance/

# 测试覆盖率
python -m pytest --cov=. tests/
```

### 测试用例
- 批改引擎准确性测试
- API接口功能测试
- 数据库操作测试
- 缓存功能测试
- 认证授权测试

## 📊 监控运维

### 健康检查
```bash
# 服务健康检查
curl http://localhost:8000/health

# 详细健康检查
curl http://localhost:8000/health/detailed

# 服务状态
curl http://localhost:8000/api/services/status
```

### 监控指标
- API响应时间
- 批改准确率
- 错误率统计
- 用户活跃度
- 资源使用情况

### 日志管理
- 结构化日志输出
- 错误日志收集
- 性能日志分析
- 安全审计日志

## 🔒 安全特性

### 认证授权
- JWT Token认证
- 角色权限控制(RBAC)
- API访问限流
- 请求签名验证

### 数据安全
- 敏感数据加密
- SQL注入防护
- XSS攻击防护
- 数据传输加密

### 隐私保护
- 用户数据匿名化
- 数据访问审计
- 数据保留策略
- GDPR合规性

## 🚀 部署指南

### Docker 部署
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 扩容服务
docker-compose scale math-service=3
```

### Kubernetes 部署
```bash
# 应用配置
kubectl apply -f kubernetes/

# 查看服务状态
kubectl get pods -n zyjc

# 服务扩容
kubectl scale deployment math-service --replicas=3
```

### 生产环境配置
- 负载均衡配置
- 数据库集群
- Redis集群
- 文件存储CDN
- SSL证书配置

## 📈 性能优化

### 缓存策略
- Redis缓存热点数据
- 数据库查询优化
- 静态资源CDN
- 接口响应缓存

### 数据库优化
- 索引优化
- 查询语句优化
- 连接池配置
- 读写分离

### 微服务优化
- 服务间通信优化
- 异步任务处理
- 熔断降级机制
- 负载均衡策略

## 🤝 贡献指南

### 开发流程
1. Fork 项目
2. 创建特性分支
3. 提交代码变更
4. 编写测试用例
5. 提交Pull Request

### 代码规范
- PEP 8 Python代码规范
- 类型注解要求
- 文档字符串规范
- 测试覆盖率要求

### 提交规范
```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 其他修改
```

## 📄 许可证

本项目采用 MIT 许可证，详情请查看 [LICENSE](LICENSE) 文件。

## 📞 联系我们

- 项目网站: https://zyjc-platform.com
- 文档网站: https://docs.zyjc-platform.com
- 技术支持: tech-support@zyjc-platform.com
- 商务合作: business@zyjc-platform.com

---

© 2024 ZYJC智能批改平台. All rights reserved.