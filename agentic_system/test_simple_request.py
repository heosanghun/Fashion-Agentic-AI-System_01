#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 요청 테스트 스크립트
로그를 확인하여 멈춤 지점 파악
"""

import requests
import time

def test_simple_request():
    """간단한 텍스트 요청 테스트"""
    print("=" * 60)
    print("간단한 요청 테스트")
    print("=" * 60)
    
    url = "http://localhost:8000/api/v1/request"
    form_data = {
        "text": "테스트 요청",
        "session_id": f"test_{int(time.time())}"
    }
    
    print(f"\n요청 URL: {url}")
    print(f"요청 데이터: {form_data}")
    print("\n요청 전송 중...")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        response = requests.post(
            url,
            data=form_data,
            timeout=15
        )
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ 요청 성공!")
        print(f"응답 시간: {elapsed_time:.2f}초")
        print(f"상태 코드: {response.status_code}")
        print(f"\n응답 내용:")
        print(response.text[:500])
        
    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        print(f"\n❌ 요청 타임아웃 (15초)")
        print(f"경과 시간: {elapsed_time:.2f}초")
        print("\n⚠️ API 서버가 요청을 처리하는 동안 멈춤")
        print("   서버 콘솔 로그를 확인하여 멈춤 지점을 파악하세요.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 연결 오류")
        print("   API 서버가 실행 중인지 확인하세요.")
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ 오류 발생: {str(e)}")
        print(f"경과 시간: {elapsed_time:.2f}초")

if __name__ == "__main__":
    test_simple_request()

