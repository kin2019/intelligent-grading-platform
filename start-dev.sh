#!/bin/bash

# 开发环境启动脚本

echo "🚀 启动中小学智能批改平台开发环境..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 复制环境变量文件（如果不存在）
if [ ! -f .env ]; then
    echo "📋 复制环境变量配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置必要的环境变量"
fi

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p backend/logs
mkdir -p backend/uploads
mkdir -p nginx/conf.d
mkdir -p nginx/ssl

# 启动开发环境服务
echo "🔧 启动开发环境服务..."
docker-compose up -d db redis

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 10

# 初始化数据库
echo "🗄️  初始化数据库..."
cd backend
python scripts/init_db.py

# 启动后端服务
echo "🖥️  启动后端服务..."
python start.py

echo "✅ 开发环境启动完成！"
echo "📖 API文档: http://localhost:8000/docs"
echo "💾 数据库: PostgreSQL localhost:5432"
echo "🔄 缓存: Redis localhost:6379"