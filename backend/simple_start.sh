#!/bin/bash

# 워크플로우용 간단한 백엔드 실행 명령어
# 한 줄로 실행 가능

pip install -r requirements.txt && \
pkill -f "python.*run_server" 2>/dev/null || true && \
pkill -f "uvicorn.*main:app" 2>/dev/null || true && \
sleep 2 && \
nohup python3 run_server.py > server.log 2>&1 & \
sleep 5 && \
echo "Server started. Check with: curl http://localhost:8080/swagger-ui"
