#!/bin/bash

# 生产环境启动脚本

echo "🚀 启动中小学智能批改平台生产环境..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "❌ 未找到 .env 文件，请先配置环境变量"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p backend/logs
mkdir -p backend/uploads  
mkdir -p nginx/conf.d
mkdir -p nginx/ssl

# 设置生产环境
export ENVIRONMENT=production

# 构建并启动所有服务
echo "🔧 构建并启动生产环境服务..."
docker-compose --profile production up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 初始化数据库（如果需要）
echo "🗄️  检查数据库状态..."
docker-compose exec backend python scripts/init_db.py

echo "✅ 生产环境启动完成！"
echo "🌐 服务地址: http://localhost"
echo "📖 API文档: http://localhost/docs"
echo "💾 数据库: PostgreSQL"
echo "🔄 缓存: Redis"
echo ""
echo "📊 查看日志: docker-compose logs -f"
echo "⏹️  停止服务: docker-compose down"