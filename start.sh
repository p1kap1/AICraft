#!/bin/bash
# AICraft All-in-One Startup

echo "🚀 AICraft"

# 1. Docker
if ! docker ps &>/dev/null 2>&1; then
    echo "  启动 Docker..."
    sudo dockerd --storage-driver=vfs --iptables=false &>/dev/null &
    sleep 2
fi

# 2. PostgreSQL + pgvector
if ! docker ps --format '{{.Names}}' | grep -q agentx-postgres; then
    docker start agentx-postgres &>/dev/null 2>&1 || \
    docker run -d --name agentx-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 pgvector/pgvector:pg15
    sleep 3
fi

# 3. Backend
cd backend
pkill -f uvicorn 2>/dev/null
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/aicraft-backend.log 2>&1 &
cd ..

# 4. Frontend
cd frontend
nohup npm run dev > /tmp/aicraft-frontend.log 2>&1 &
cd ..

echo "✅ Backend: http://localhost:8000"
echo "✅ Frontend: http://localhost:3000"
