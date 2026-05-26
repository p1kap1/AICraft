#!/bin/bash
# AICraft 一键启动

echo "🚀 启动 AICraft..."

# Docker
if ! sudo docker ps &>/dev/null 2>&1; then
    echo "  启动 Docker..."
    sudo dockerd --storage-driver=vfs --iptables=false &>/tmp/dockerd.log &
    sleep 3
fi

# 数据库容器
if ! sudo docker ps --format '{{.Names}}' | grep -q agentx-postgres; then
    sudo docker start agentx-postgres 2>/dev/null || \
    sudo docker run -d --name agentx-postgres \
        -e POSTGRES_DB=aicraft -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
        -p 5432:5432 pgvector/pgvector:pg15
fi

# 后端
cd /home/chen/AICraft/backend
pkill -f uvicorn 2>/dev/null
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 前端
cd /home/chen/AICraft/frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api npm run dev &

sleep 5
echo ""
echo "✅ AICraft 已启动"
echo "   前端: http://localhost:3001"
echo "   后端: http://localhost:8000/api/docs"
