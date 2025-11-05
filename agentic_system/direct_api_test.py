#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
직접 API 서버 실행 및 테스트
로그를 직접 확인하여 멈춤 지점 파악
"""

import sys
import os
from pathlib import Path
import uvicorn
import threading
import time
import requests

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_api_server():
    """API 서버 실행"""
    print("=" * 60)
    print("API 서버 시작...")
    print("=" * 60)
    uvicorn.run(
        "agentic_system.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

def test_request():
    """테스트 요청 전송"""
    time.sleep(3)  # 서버 시작 대기
    
    url = "http://localhost:8000/api/v1/request"
    form_data = {
        "text": "빨간색 원피스 추천해줘",
        "session_id": f"test_{int(time.time())}"
    }
    
    print("\n" + "=" * 60)
    print("테스트 요청 전송...")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Data: {form_data}\n")
    
    try:
        response = requests.post(url, data=form_data, timeout=20)
        print("✅ 요청 성공!")
        print(f"상태 코드: {response.status_code}")
        print(f"\n응답:")
        print(response.text[:500])
    except requests.exceptions.Timeout:
        print("❌ 타임아웃 발생 (20초)")
        print("   서버 로그를 확인하여 멈춤 지점을 파악하세요.")
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    # 서버를 별도 스레드에서 실행
    server_thread = threading.Thread(target=run_api_server, daemon=True)
    server_thread.start()
    
    # 요청 전송
    test_request()
    
    # 프로그램 종료 방지
    time.sleep(2)

