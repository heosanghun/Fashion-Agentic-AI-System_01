#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 서버 시작 스크립트
프론트엔드 테스트를 위한 API 서버 실행
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("Fashion Agentic AI System API 서버 시작")
    print("=" * 60)
    print("서버 주소: http://localhost:8000")
    print("API 문서: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "agentic_system.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

