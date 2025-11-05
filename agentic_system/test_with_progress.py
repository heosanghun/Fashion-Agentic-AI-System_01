#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
진행률 표시가 있는 테스트 스크립트
"""

import requests
import time
import sys
import threading
from datetime import datetime

def print_progress(message, step=None, total=None):
    """진행률 출력"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if step and total:
        percent = int((step / total) * 100)
        print(f"[{timestamp}] [{percent:3d}%] {message}")
    else:
        print(f"[{timestamp}] [---] {message}")
    sys.stdout.flush()

def test_api_with_progress():
    """진행률 표시가 있는 API 테스트"""
    print("=" * 70)
    print("Fashion Agentic AI System - 실시간 진행률 테스트")
    print("=" * 70)
    print()
    
    # 서버 연결 확인
    print_progress("1/5: API 서버 연결 확인 중...", 1, 5)
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print_progress("   -> API 서버 정상 작동", 1, 5)
        else:
            print_progress(f"   -> API 서버 오류: {response.status_code}", 1, 5)
            return False
    except requests.exceptions.ConnectionError:
        print_progress("   -> API 서버가 실행되지 않았습니다!", 1, 5)
        print_progress("   -> 서버를 시작해주세요: python start_api_server.py", 1, 5)
        return False
    except Exception as e:
        print_progress(f"   -> 연결 오류: {str(e)}", 1, 5)
        return False
    
    time.sleep(0.5)
    
    # 요청 준비
    print_progress("2/5: 요청 데이터 준비 중...", 2, 5)
    url = "http://localhost:8000/api/v1/request"
    form_data = {
        "text": "빨간색 원피스 추천해줘",
        "session_id": f"progress_test_{int(time.time())}"
    }
    time.sleep(0.5)
    
    # 요청 전송
    print_progress("3/5: 요청 전송 중...", 3, 5)
    print_progress(f"   -> URL: {url}", 3, 5)
    print_progress(f"   -> 데이터: {form_data}", 3, 5)
    print()
    
    # 진행률 모니터링
    progress_thread = None
    request_sent = threading.Event()
    request_completed = threading.Event()
    response_received = None
    error_occurred = None
    
    def monitor_progress():
        """진행률 모니터링"""
        dots = 0
        while not request_completed.is_set():
            if request_sent.is_set():
                dots = (dots + 1) % 4
                dots_str = "." * dots + " " * (3 - dots)
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] [처리중] 서버 응답 대기 중{dots_str}", end="", flush=True)
            time.sleep(0.5)
        print()  # 줄바꿈
    
    start_time = time.time()
    
    try:
        # 진행률 모니터링 시작
        progress_thread = threading.Thread(target=monitor_progress, daemon=True)
        progress_thread.start()
        
        request_sent.set()
        
        # 요청 전송 (타임아웃 15초)
        response = requests.post(url, data=form_data, timeout=15)
        
        request_completed.set()
        elapsed = time.time() - start_time
        
        print_progress("4/5: 응답 수신 완료!", 4, 5)
        print_progress(f"   -> 응답 시간: {elapsed:.2f}초", 4, 5)
        print_progress(f"   -> 상태 코드: {response.status_code}", 4, 5)
        
        time.sleep(0.5)
        
        # 결과 확인
        print_progress("5/5: 결과 분석 중...", 5, 5)
        try:
            result = response.json()
            print()
            print("=" * 70)
            print("SUCCESS - 요청이 성공적으로 처리되었습니다!")
            print("=" * 70)
            print(f"상태: {result.get('status', 'N/A')}")
            print(f"메시지: {result.get('message', 'N/A')}")
            print()
            print("응답 데이터:")
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
            print("=" * 70)
            return True
        except:
            print()
            print("=" * 70)
            print("SUCCESS - 요청 처리 완료!")
            print("=" * 70)
            print(f"응답 내용 (처음 500자):")
            print(response.text[:500])
            print("=" * 70)
            return True
            
    except requests.exceptions.Timeout:
        request_completed.set()
        elapsed = time.time() - start_time
        
        print()
        print_progress("4/5: 타임아웃 발생!", 4, 5)
        print_progress(f"   -> 경과 시간: {elapsed:.2f}초 (15초 타임아웃)", 4, 5)
        print()
        print("=" * 70)
        print("TIMEOUT - 요청 처리 타임아웃")
        print("=" * 70)
        print("서버 로그를 확인하여 멈춤 지점을 파악하세요:")
        print("  1. API 서버 콘솔에서 로그 확인")
        print("  2. 마지막 출력된 로그 메시지 확인")
        print("  3. [API], [AgentRuntime], [F.LLM], [Extensions2DTo3D] 로그 확인")
        print("=" * 70)
        return False
        
    except requests.exceptions.ConnectionError as e:
        request_completed.set()
        print()
        print_progress("4/5: 연결 오류 발생!", 4, 5)
        print()
        print("=" * 70)
        print("CONNECTION ERROR")
        print("=" * 70)
        print(f"오류: {str(e)}")
        print("API 서버가 실행 중인지 확인하세요.")
        print("=" * 70)
        return False
        
    except Exception as e:
        request_completed.set()
        elapsed = time.time() - start_time
        
        print()
        print_progress(f"4/5: 오류 발생: {str(e)}", 4, 5)
        print_progress(f"   -> 경과 시간: {elapsed:.2f}초", 4, 5)
        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print(f"오류: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        return False

if __name__ == "__main__":
    success = test_api_with_progress()
    sys.exit(0 if success else 1)

