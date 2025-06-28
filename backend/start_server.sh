#!/bin/bash

# 백엔드 서버 시작 스크립트 (워크플로우용)

set -e  # 에러 발생 시 스크립트 중단

echo "🔍 Checking Python version..."
python3 --version

echo "🔍 Checking for existing server processes..."
pkill -f "python.*run_server" 2>/dev/null || true
pkill -f "uvicorn.*main:app" 2>/dev/null || true
sleep 2

echo "🔍 Checking if port 8080 is available..."
if nc -z localhost 8080 2>/dev/null; then
    echo "❌ Port 8080 is still in use. Finding and killing processes..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

echo "🚀 Installing Python dependencies..."
pip install -r requirements.txt

echo "🚀 Starting FastAPI server in background..."
nohup python3 run_server.py > server.log 2>&1 &
SERVER_PID=$!

echo "Server PID: $SERVER_PID"
echo "⏳ Waiting for server to start..."

# 서버가 시작될 때까지 최대 30초 대기
for i in {1..30}; do
    if nc -z localhost 8080 2>/dev/null; then
        echo "✅ Server is running on port 8080!"
        echo "📝 Logs are being written to server.log"
        echo "🔍 Server process ID: $SERVER_PID"
        exit 0
    fi
    echo "Waiting... ($i/30)"
    sleep 1
done

echo "❌ Server failed to start within 30 seconds"
echo "📝 Last 10 lines of server.log:"
tail -10 server.log 2>/dev/null || echo "No log file found"
exit 1버 시작 스크립트 (백그라운드 실행)

echo "� Checking for existing server processes..."
pkill -f "python.*run_server" 2>/dev/null || true
pkill -f "uvicorn.*main:app" 2>/dev/null || true

echo "�🚀 Installing Python dependencies..."
pip install -r requirements.txt

echo "🚀 Starting FastAPI server in background..."
nohup python3 run_server.py > server.log 2>&1 &

# 서버가 시작될 때까지 잠시 대기
sleep 5

echo "✅ Server started in background"
echo "📝 Logs are saved to server.log"
echo "🔍 Check server status with: ps aux | grep python"
