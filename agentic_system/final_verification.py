#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 검증 테스트
"""

import requests
import time
import sys
from datetime import datetime

def print_status(message, status="INFO"):
    """상태 출력"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def test_api():
    """API 테스트"""
    print("=" * 70)
    print("최종 검증 테스트")
    print("=" * 70)
    print()
    
    # 1. 헬스체크
    print_status("1/3: API 서버 연결 확인...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print_status("   -> API 서버 정상 작동")
        else:
            print_status(f"   -> API 서버 오류: {response.status_code}")
            return False
    except:
        print_status("   -> API 서버가 실행되지 않았습니다!")
        print_status("   -> 서버를 시작해주세요: python start_api_server.py")
        return False
    
    # 2. 텍스트 요청
    print_status("2/3: 텍스트 요청 테스트...")
    url = "http://localhost:8000/api/v1/request"
    form_data = {
        "text": "빨간색 원피스 추천해줘",
        "session_id": f"final_test_{int(time.time())}"
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, data=form_data, timeout=8)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print_status(f"   -> 요청 성공! (응답 시간: {elapsed:.2f}초)")
            try:
                result = response.json()
                print_status(f"   -> 상태: {result.get('status', 'N/A')}")
                print_status(f"   -> 메시지: {result.get('message', 'N/A')[:50]}")
                return True
            except:
                print_status(f"   -> 응답 내용: {response.text[:100]}")
                return True
        else:
            print_status(f"   -> 요청 실패: {response.status_code}")
            print_status(f"   -> 응답: {response.text[:100]}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print_status(f"   -> 타임아웃 발생! (경과 시간: {elapsed:.2f}초)")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print_status(f"   -> 오류: {str(e)} (경과 시간: {elapsed:.2f}초)")
        return False
    
    # 3. 요약
    print()
    print_status("3/3: 테스트 완료")
    print()
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = test_api()
    if success:
        print("✅ 모든 테스트 통과!")
    else:
        print("❌ 일부 테스트 실패")
    print("=" * 70)
    sys.exit(0 if success else 1)

