"""
ChatGarment 직접 테스트 스크립트
ChatGarment 서비스를 직접 호출하여 실제 3D 변환이 작동하는지 확인
"""
import requests
import json
from pathlib import Path
import time

print("=" * 60)
print("ChatGarment 직접 테스트 - 실제 3D 변환 확인")
print("=" * 60)
print()

# 1. ChatGarment 서비스 상태 확인
print("[1/5] ChatGarment 서비스 상태 확인...")
try:
    response = requests.get("http://localhost:9000/health", timeout=3)
    if response.status_code == 200:
        print(f"[OK] ChatGarment 서비스가 실행 중입니다!")
        print(f"    응답: {response.json()}")
    else:
        print(f"[FAIL] 서비스가 정상 응답하지 않습니다: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"[FAIL] ChatGarment 서비스에 연결할 수 없습니다: {e}")
    print()
    print("[INFO] ChatGarment 서비스를 시작하세요:")
    print("    cd agentic_system\\chatgarment_service")
    print("    python main.py")
    exit(1)

print()

# 2. 테스트 이미지 찾기
print("[2/5] 테스트 이미지 찾기...")
test_images = []
upload_dir = Path("uploads")
if upload_dir.exists():
    test_images = list(upload_dir.glob("*.jpg")) + list(upload_dir.glob("*.png")) + list(upload_dir.glob("*.jpeg"))

if not test_images:
    print("[FAIL] 테스트 이미지를 찾을 수 없습니다.")
    print("    uploads 디렉토리에 이미지를 추가하세요.")
    exit(1)

test_image = test_images[0]
print(f"[OK] 테스트 이미지: {test_image}")
print(f"    크기: {test_image.stat().st_size / 1024:.2f} KB")

print()

# 3. ChatGarment 서비스에 직접 이미지 분석 요청
print("[3/5] ChatGarment 서비스에 이미지 분석 요청...")
try:
    with open(test_image, 'rb') as f:
        files = {'image': (test_image.name, f, 'image/jpeg')}
        data = {'text': '이 옷을 분석해주세요'}
        
        print("[*] /api/v1/analyze 엔드포인트 호출 중...")
        response = requests.post(
            'http://localhost:9000/api/v1/analyze',
            files=files,
            data=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] 이미지 분석 완료!")
            print(f"    상태: {result.get('status')}")
            if result.get('analysis'):
                analysis = result['analysis']
                print(f"    분석 결과:")
                for key, value in analysis.items():
                    print(f"      {key}: {value}")
            
            # Mock 모드인지 확인
            message = result.get('message', '')
            if 'Mock' in message or 'mock' in message:
                print()
                print("[WARNING] Mock 모드로 동작하고 있습니다!")
                print("    실제 ChatGarment 모델이 사용되지 않았습니다.")
            else:
                print()
                print("[OK] 실제 ChatGarment 모델이 사용되었습니다!")
        else:
            print(f"[FAIL] 분석 요청 실패: {response.status_code}")
            print(f"    응답: {response.text[:500]}")
            exit(1)
            
except Exception as e:
    print(f"[FAIL] 분석 요청 중 오류 발생: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# 4. ChatGarment 서비스에 전체 파이프라인 요청
print("[4/5] ChatGarment 서비스에 전체 파이프라인 요청 (3D 변환)...")
print("      이 작업은 시간이 걸릴 수 있습니다 (실제 모델 사용 시)")
print()

try:
    with open(test_image, 'rb') as f:
        files = {'image': (test_image.name, f, 'image/jpeg')}
        data = {'text': '이 옷을 3D로 변환해주세요'}
        
        print("[*] /api/v1/process 엔드포인트 호출 중...")
        print("    (실제 모델 사용 시 몇 분이 걸릴 수 있습니다)")
        print()
        
        start_time = time.time()
        response = requests.post(
            'http://localhost:9000/api/v1/process',
            files=files,
            data=data,
            timeout=600  # 10분 타임아웃
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] 전체 파이프라인 처리 완료! (소요 시간: {elapsed_time:.1f}초)")
            print(f"    상태: {result.get('status')}")
            
            # 결과 상세 확인
            if result.get('result'):
                result_data = result['result']
                print()
                print("[*] 처리 결과:")
                
                # 분석 결과
                if result_data.get('analysis'):
                    analysis = result_data['analysis']
                    print(f"    이미지 분석: {analysis}")
                
                # 패턴 경로
                if result_data.get('pattern_path'):
                    pattern_path = result_data['pattern_path']
                    pattern_file = Path(pattern_path)
                    if pattern_file.exists():
                        print(f"    [OK] 패턴 파일 생성됨: {pattern_path}")
                        print(f"         크기: {pattern_file.stat().st_size / 1024:.2f} KB")
                    else:
                        print(f"    [FAIL] 패턴 파일이 없습니다: {pattern_path}")
                
                # 메시 경로
                if result_data.get('mesh_path'):
                    mesh_path = result_data['mesh_path']
                    mesh_file = Path(mesh_path)
                    if mesh_file.exists():
                        size_mb = mesh_file.stat().st_size / (1024 * 1024)
                        print(f"    [OK] 3D 메시 파일 생성됨: {mesh_path}")
                        print(f"         크기: {size_mb:.2f} MB")
                    else:
                        print(f"    [FAIL] 3D 메시 파일이 없습니다: {mesh_path}")
                
                # 렌더링 경로
                if result_data.get('render_path'):
                    render_path = result_data['render_path']
                    render_file = Path(render_path)
                    if render_path and render_file.exists():
                        print(f"    [OK] 렌더링 이미지 생성됨: {render_path}")
                        print(f"         크기: {render_file.stat().st_size / 1024:.2f} KB")
                    else:
                        print(f"    [INFO] 렌더링 이미지가 없습니다: {render_path}")
            
            # Mock 모드인지 확인
            message = result.get('message', '')
            result_message = result.get('result', {}).get('message', '')
            
            if 'Mock' in message or 'mock' in message or 'Mock' in result_message or 'mock' in result_message:
                print()
                print("=" * 60)
                print("[WARNING] Mock 모드로 동작하고 있습니다!")
                print("=" * 60)
                print()
                print("실제 ChatGarment 모델이 사용되지 않았습니다.")
                print()
                print("가능한 원인:")
                print("1. ChatGarment 모델 파일이 로드되지 않음")
                print("2. ChatGarment Pipeline이 초기화되지 않음")
                print("3. 서비스 로그를 확인하여 오류 확인 필요")
                print()
                print("확인 사항:")
                print("- ChatGarment 서비스 창에서 'ChatGarment Pipeline 로딩 완료' 메시지 확인")
                print("- 모델 파일 경로 확인: checkpoints/try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final/pytorch_model.bin")
            else:
                print()
                print("=" * 60)
                print("[OK] 실제 ChatGarment 모델이 사용되었습니다!")
                print("=" * 60)
                
        else:
            print(f"[FAIL] 파이프라인 처리 실패: {response.status_code}")
            print(f"    응답: {response.text[:1000]}")
            
except Exception as e:
    print(f"[FAIL] 파이프라인 처리 중 오류 발생: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("테스트 완료")
print("=" * 60)

