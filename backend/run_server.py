#!/usr/bin/env python3
"""
서버 실행 스크립트
"""
import uvicorn
import sys
import os

if __name__ == "__main__":
    # 현재 디렉토리를 sys.path에 추가
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    print("🚀 Starting FastAPI server...")
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8080,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
