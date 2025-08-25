# 中小学智能批改平台后端服务

基于FastAPI + PostgreSQL + Redis的智能作业批改系统后端服务，支持小学数学口算批改功能。

## 🚀 功能特性

### 核心功能
- ✅ **用户认证**: 微信小程序登录、JWT令牌管理
- ✅ **权限管理**: 基于角色的权限控制(RBAC)
- ✅ **数学批改**: 小学口算题目智能批改
- ✅ **错题管理**: 错题记录、分析和复习跟踪
- ✅ **额度管理**: VIP用户管理、每日使用额度控制
- ✅ **API限流**: 基于Redis的频率限制
- ✅ **日志记录**: 结构化日志和请求追踪

### 技术架构
- **Web框架**: FastAPI (异步高性能)
- **数据库**: PostgreSQL 15 (主数据库)
- **缓存**: Redis 7 (缓存 + 限流)
- **ORM**: SQLAlchemy (异步模式)
- **认证**: JWT + 微信小程序登录
- **容器化**: Docker + Docker Compose
- **API文档**: 自动生成OpenAPI/Swagger文档

## 📁 项目结构

```
backend/
├── app/
│   ├── api/v1/              # API路由
│   │   ├── auth.py          # 认证接口
│   │   └── homework.py      # 作业批改接口
│   ├── core/                # 核心配置
│   │   ├── config.py        # 应用配置
│   │   ├── database.py      # 数据库连接
│   │   ├── security.py      # 安全认证
│   │   └── deps.py          # 依赖注入
│   ├── middleware/          # 中间件
│   │   ├── cors.py          # 跨域处理
│   │   ├── logging.py       # 日志记录
│   │   └── rate_limit.py    # 频率限制
│   ├── models/              # 数据模型
│   │   ├── user.py          # 用户模型
│   │   └── homework.py      # 作业模型
│   ├── services/            # 业务逻辑
│   │   ├── auth_service.py  # 认证服务
│   │   ├── user_service.py  # 用户服务
│   │   └── math_service.py  # 数学批改服务
│   └── main.py              # 应用入口
├── scripts/                 # 脚本工具
│   └── init_db.py          # 数据库初始化
├── alembic/                # 数据库迁移
├── requirements.txt        # Python依赖
├── Dockerfile             # Docker镜像
└── start.py              # 启动脚本
```

## 🛠️ 开发环境搭建

### 环境要求
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 快速启动

1. **克隆项目**
```bash
git clone <repository-url>
cd zyjc
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis、微信等参数
```

3. **启动开发环境**
```bash
# Linux/Mac
chmod +x start-dev.sh
./start-dev.sh

# Windows
# 手动执行以下命令
docker-compose up -d db redis
cd backend
pip install -r requirements.txt
python scripts/init_db.py
python start.py
```

4. **访问服务**
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 手动安装

1. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **配置数据库**
```bash
# 启动PostgreSQL和Redis
docker-compose up -d db redis

# 初始化数据库
python scripts/init_db.py
```

3. **启动服务**
```bash
python start.py
```

## 🚀 生产部署

### Docker部署

1. **配置生产环境**
```bash
# 复制并编辑生产环境配置
cp .env.example .env
# 修改ENVIRONMENT=production
# 配置安全的SECRET_KEY
# 配置真实的微信和第三方服务参数
```

2. **启动生产环境**
```bash
chmod +x start-prod.sh
./start-prod.sh
```

3. **服务监控**
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 进入容器
docker-compose exec backend bash
```

## 📚 API文档

### 认证接口
- `POST /api/v1/auth/wechat/login` - 微信登录
- `POST /api/v1/auth/refresh` - 刷新令牌
- `GET /api/v1/auth/me` - 获取用户信息
- `PUT /api/v1/auth/profile` - 更新用户资料

### 作业批改接口
- `POST /api/v1/homework/correct` - 批改作业
- `GET /api/v1/homework/list` - 获取作业历史
- `GET /api/v1/homework/{id}` - 获取作业详情
- `GET /api/v1/homework/{id}/errors` - 获取错题详情

详细API文档请访问: http://localhost:8000/docs

## 🔧 配置说明

### 环境变量
主要配置项说明：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=zyjc_db
DB_USER=postgres
DB_PASSWORD=postgres123

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis123

# 应用安全
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 微信小程序
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret

# OCR服务
BAIDU_API_KEY=your-baidu-api-key
BAIDU_SECRET_KEY=your-baidu-secret-key
```

## 🧪 测试

### 运行测试
```bash
# 单元测试
cd backend
python -m pytest tests/

# 集成测试
python -m pytest tests/integration/

# 测试覆盖率
python -m pytest --cov=app tests/
```

### API测试
```bash
# 健康检查
curl http://localhost:8000/health

# 获取API文档
curl http://localhost:8000/openapi.json
```

## 📈 性能监控

### 指标监控
- 请求响应时间
- 数据库连接池状态
- Redis连接状态
- API调用频次
- 错误率统计

### 日志查看
```bash
# Docker环境
docker-compose logs -f backend

# 本地环境
tail -f backend/logs/app.log
```

## 🔒 安全说明

### 安全措施
- JWT令牌认证
- 密码bcrypt加密
- API频率限制
- CORS跨域保护
- 输入参数验证
- SQL注入防护

### 生产环境安全建议
1. 使用强密码和复杂的SECRET_KEY
2. 启用HTTPS
3. 配置防火墙规则
4. 定期备份数据库
5. 监控异常访问

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📝 更新日志

### v1.0.0 (2024-01-XX)
- ✅ 初始版本发布
- ✅ 微信登录认证
- ✅ 小学数学口算批改MVP
- ✅ 用户权限管理
- ✅ Docker容器化部署

## 📄 许可证

本项目采用MIT许可证，详见 [LICENSE](LICENSE) 文件。

## 📞 支持

如有问题或建议，请提交Issue或联系开发团队。

---

🎯 **项目目标**: 为中小学生提供智能、准确、便捷的作业批改服务，助力教育数字化转型。