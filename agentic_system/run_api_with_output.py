#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 서버 실행 및 로그 출력
"""

import uvicorn
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("=" * 60)
    print("Fashion Agentic AI System API 서버 시작")
    print("=" * 60)
    print("서버 주소: http://localhost:8000")
    print("API 문서: http://localhost:8000/docs")
    print("=" * 60)
    print("\n로그를 확인하세요. 요청을 보내면 아래에 로그가 출력됩니다.\n")
    
    uvicorn.run(
        "agentic_system.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # reload=False로 변경하여 로그가 명확하게 보이도록
        log_level="info"
    )

