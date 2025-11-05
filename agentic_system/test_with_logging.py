#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로그 확인을 위한 테스트 스크립트
"""

import requests
import time
import sys

def test_request():
    """요청 테스트 및 로그 확인"""
    print("=" * 60)
    print("API 요청 테스트 (로그 확인용)")
    print("=" * 60)
    
    url = "http://localhost:8000/api/v1/request"
    form_data = {
        "text": "빨간색 원피스 추천해줘",
        "session_id": f"test_{int(time.time())}"
    }
    
    print(f"\n요청 전송...")
    print(f"   URL: {url}")
    print(f"   데이터: {form_data}")
    print("\n응답 대기 중 (서버 로그를 확인하세요)...\n")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            url,
            data=form_data,
            timeout=20
        )
        
        elapsed = time.time() - start_time
        
        print("=" * 60)
        print("✅ 요청 성공!")
        print(f"응답 시간: {elapsed:.2f}초")
        print(f"상태 코드: {response.status_code}")
        print("\n응답 내용:")
        try:
            import json
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
        except:
            print(response.text[:500])
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print("=" * 60)
        print(f"❌ 타임아웃 발생 (20초)")
        print(f"경과 시간: {elapsed:.2f}초")
        print("\n⚠️ 서버 로그(api_server_log.txt)를 확인하여 멈춤 지점을 파악하세요.")
        print("\n마지막 로그 메시지를 확인:")
        print("  - [API] 요청 수신 후 어느 단계까지 진행되었는지")
        print("  - [AgentRuntime] 어느 단계에서 멈췄는지")
        print("  - [F.LLM] 실행 계획 생성 단계에서 멈췄는지")
        print("  - [Extensions2DTo3D] 도구 실행 단계에서 멈췄는지")
        sys.exit(1)
        
    except requests.exceptions.ConnectionError:
        print("=" * 60)
        print("❌ 연결 오류")
        print("   API 서버가 실행 중인지 확인하세요.")
        sys.exit(1)
        
    except Exception as e:
        elapsed = time.time() - start_time
        print("=" * 60)
        print(f"❌ 오류 발생: {str(e)}")
        print(f"경과 시간: {elapsed:.2f}초")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_request()

