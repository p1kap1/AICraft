#!/bin/bash
# AICraft 启动脚本
# 本地开发用 ./start.sh dev
# Docker 部署用 ./start.sh docker

MODE=${1:-dev}

if [ "$MODE" = "docker" ]; then
    echo "🐳 Docker Compose 启动..."
    docker compose up -d
    echo "✅ 后端 http://localhost:8000"
    echo "✅ 前端 http://localhost:3000"
else
    echo "🚀 本地开发模式"
    echo "确保 PostgreSQL 已启动 (端口 5432)"

    cd "$(dirname "$0")/backend"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    echo "✅ 后端 http://localhost:8000"

    cd "$(dirname "$0")/frontend"
    npm run dev &
    echo "✅ 前端 http://localhost:3000"

    wait
fi
