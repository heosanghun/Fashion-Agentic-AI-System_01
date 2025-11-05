"""
3D 변환 통합 테스트 스크립트
실제 이미지를 업로드하여 ChatGarment 서비스를 통해 3D 변환이 작동하는지 테스트
"""
import requests
import time
from pathlib import Path
import json

print("=" * 60)
print("3D Conversion Integration Test")
print("=" * 60)
print()

# 테스트 이미지 찾기
test_images = []
upload_dir = Path("uploads")
if upload_dir.exists():
    test_images = list(upload_dir.glob("*.jpg")) + list(upload_dir.glob("*.png")) + list(upload_dir.glob("*.jpeg"))

if not test_images:
    print("[INFO] 테스트 이미지를 찾을 수 없습니다.")
    print("      uploads 디렉토리에 이미지를 추가하거나 프론트엔드에서 테스트하세요.")
    exit(0)

test_image = test_images[0]
print(f"[*] 테스트 이미지: {test_image}")
print(f"    크기: {test_image.stat().st_size / 1024:.2f} KB")
print()

# 서비스 상태 확인
print("[*] 서비스 상태 확인 중...")

# ChatGarment 서비스 확인
try:
    response = requests.get("http://localhost:9000/health", timeout=3)
    if response.status_code == 200:
        print("[OK] ChatGarment Service is running")
    else:
        print(f"[FAIL] ChatGarment Service returned status {response.status_code}")
        exit(1)
except Exception as e:
    print(f"[FAIL] ChatGarment Service is not running: {e}")
    exit(1)

# API 서버 확인
try:
    response = requests.get("http://localhost:8000/health", timeout=3)
    if response.status_code == 200:
        print("[OK] API Server is running")
    else:
        print(f"[FAIL] API Server returned status {response.status_code}")
        exit(1)
except Exception as e:
    print(f"[FAIL] API Server is not running: {e}")
    exit(1)

print()

# 이미지 업로드 및 처리 요청
print("[*] 이미지 업로드 및 3D 변환 요청 중...")
print("    이 작업은 시간이 걸릴 수 있습니다 (모델 로딩 및 처리 시간 포함)")
print()

try:
    with open(test_image, 'rb') as f:
        files = {'image': (test_image.name, f, 'image/jpeg')}
        data = {
            'text': '이 옷을 3D로 변환해주세요',
            'session_id': f'test_{int(time.time())}'
        }
        
        print("[*] API 서버로 요청 전송 중...")
        response = requests.post(
            'http://localhost:8000/api/v1/request',
            files=files,
            data=data,
            timeout=300  # 5분 타임아웃
        )
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] 요청 처리 완료!")
            print()
            print("[*] 결과 요약:")
            print(f"    상태: {result.get('status', 'unknown')}")
            
            if result.get('status') == 'completed':
                print("[OK] 3D 변환이 성공적으로 완료되었습니다!")
                
                # 단계별 결과 확인
                steps = result.get('steps', {})
                if steps:
                    print()
                    print("[*] 처리 단계:")
                    for step_id, step_data in sorted(steps.items()):
                        step_status = step_data.get('status', 'unknown')
                        step_msg = step_data.get('result', {}).get('message', '')
                        status_icon = '✓' if step_status == 'success' else '✗'
                        print(f"    {step_id}. {status_icon} {step_msg}")
                
                # 최종 결과 확인
                final_result = result.get('final_result', {})
                if final_result:
                    final_data = final_result.get('result', {})
                    if final_data.get('visualization'):
                        print()
                        print("[OK] 렌더링 결과:")
                        vis = final_data.get('visualization', {})
                        if vis.get('image_path'):
                            print(f"    이미지 경로: {vis['image_path']}")
                        if vis.get('mesh_path'):
                            print(f"    메시 경로: {vis['mesh_path']}")
            else:
                print(f"[WARNING] 상태가 'completed'가 아닙니다: {result.get('status')}")
                if result.get('message'):
                    print(f"    메시지: {result['message']}")
            
            print()
            print("[INFO] 전체 결과를 확인하려면 프론트엔드에서 테스트하세요:")
            print("      http://localhost:5173")
            
        else:
            print(f"[FAIL] 요청 실패: {response.status_code}")
            print(f"    응답: {response.text[:500]}")
            
except Exception as e:
    print(f"[FAIL] 테스트 실패: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)

