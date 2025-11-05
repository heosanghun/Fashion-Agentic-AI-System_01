#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 서버 실행 및 자동 테스트
진행률 표시 포함
"""

import sys
import os
import time
import threading
import subprocess
from pathlib import Path
import requests
from datetime import datetime

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_status(message, status="INFO"):
    """상태 메시지 출력"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_symbols = {
        "INFO": "[*]",
        "SUCCESS": "[+]",
        "ERROR": "[!]",
        "WAIT": "[~]"
    }
    symbol = status_symbols.get(status, "[*]")
    print(f"[{timestamp}] {symbol} {message}")
    sys.stdout.flush()

def check_port(port=8000):
    """포트 사용 여부 확인"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def wait_for_server(max_wait=10):
    """서버 시작 대기"""
    print_status("서버 시작 대기 중...", "WAIT")
    for i in range(max_wait * 2):
        if check_port(8000):
            print_status("서버 시작 완료!", "SUCCESS")
            return True
        time.sleep(0.5)
        if i % 2 == 0:
            print_status(f"대기 중... ({i//2 + 1}/{max_wait}초)", "WAIT")
    print_status("서버 시작 시간 초과", "ERROR")
    return False

def run_api_server():
    """API 서버 실행"""
    print_status("API 서버 시작 중...", "INFO")
    try:
        import uvicorn
        uvicorn.run(
            "agentic_system.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print_status(f"서버 오류: {str(e)}", "ERROR")
        import traceback
        traceback.print_exc()

def test_request_with_progress():
    """진행률 표시가 있는 요청 테스트"""
    time.sleep(2)  # 서버 안정화 대기
    
    if not wait_for_server():
        return False
    
    print()
    print("=" * 70)
    print("API 요청 테스트 시작")
    print("=" * 70)
    print()
    
    url = "http://localhost:8000/api/v1/request"
    form_data = {
        "text": "빨간색 원피스 추천해줘",
        "session_id": f"auto_test_{int(time.time())}"
    }
    
    print_status(f"요청 URL: {url}", "INFO")
    print_status(f"요청 데이터: {form_data}", "INFO")
    print()
    
    request_completed = threading.Event()
    start_time = time.time()
    
    def show_progress():
        """진행률 표시"""
        dots = 0
        while not request_completed.is_set():
            dots = (dots + 1) % 4
            elapsed = time.time() - start_time
            dots_str = "." * dots + " " * (3 - dots)
            print(f"\r[{datetime.now().strftime('%H:%M:%S')}] [처리중] {elapsed:6.2f}초 경과{dots_str}", end="", flush=True)
            time.sleep(0.3)
        print()
    
    progress_thread = threading.Thread(target=show_progress, daemon=True)
    progress_thread.start()
    
    try:
        response = requests.post(url, data=form_data, timeout=20)
        request_completed.set()
        elapsed = time.time() - start_time
        
        print()
        print_status(f"요청 성공! (응답 시간: {elapsed:.2f}초)", "SUCCESS")
        print_status(f"상태 코드: {response.status_code}", "SUCCESS")
        print()
        
        try:
            result = response.json()
            print("응답 내용:")
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False)[:800])
        except:
            print("응답 내용:")
            print(response.text[:800])
        
        print()
        print("=" * 70)
        print("테스트 완료!")
        print("=" * 70)
        return True
        
    except requests.exceptions.Timeout:
        request_completed.set()
        elapsed = time.time() - start_time
        
        print()
        print()
        print_status(f"타임아웃 발생! (경과 시간: {elapsed:.2f}초)", "ERROR")
        print()
        print("=" * 70)
        print("타임아웃 분석")
        print("=" * 70)
        print("서버 콘솔 로그를 확인하여 멈춤 지점을 파악하세요.")
        print("마지막 출력된 로그를 확인하면 어디서 멈췄는지 알 수 있습니다.")
        print("=" * 70)
        return False
        
    except Exception as e:
        request_completed.set()
        elapsed = time.time() - start_time
        
        print()
        print()
        print_status(f"오류 발생: {str(e)} (경과 시간: {elapsed:.2f}초)", "ERROR")
        return False

if __name__ == "__main__":
    # 포트 확인
    if check_port(8000):
        print_status("포트 8000이 이미 사용 중입니다.", "INFO")
        print_status("기존 서버에 테스트 요청을 전송합니다...", "INFO")
        print()
        test_request_with_progress()
    else:
        print_status("새로운 API 서버를 시작합니다...", "INFO")
        print()
        
        # 서버를 별도 스레드에서 실행
        server_thread = threading.Thread(target=run_api_server, daemon=True)
        server_thread.start()
        
        # 테스트 실행
        test_request_with_progress()
        
        # 프로그램 종료 방지
        time.sleep(2)

