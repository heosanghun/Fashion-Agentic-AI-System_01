"""
브라우저에서의 동작을 시뮬레이션하여 실제 테스트
"""
import requests
from pathlib import Path
import json
import time

# 테스트 설정
image_path = Path("E:/0000000_T-Shirt/TEMP/TShirt.jpg")
api_url = "http://localhost:8000/api/v1/request"
session_id = f"browser_test_{int(time.time())}"
text_prompt = "이 옷을 3D로 변환해주세요"

print("=" * 70)
print("브라우저 테스트 시뮬레이션")
print("=" * 70)
print(f"\n[시뮬레이션] 브라우저에서 다음 작업 수행:")
print(f"  1. 텍스트 입력: '{text_prompt}'")
print(f"  2. 이미지 선택: {image_path}")
print(f"  3. '요청 전송' 버튼 클릭")
print("\n" + "-" * 70)

# 이미지 파일 확인
print(f"\n[1/5] 이미지 파일 확인...")
if image_path.exists():
    file_size = image_path.stat().st_size / 1024
    print(f"  ✓ 파일 존재: {image_path}")
    print(f"  파일 크기: {file_size:.2f} KB")
else:
    print(f"  ❌ 파일 없음: {image_path}")
    exit(1)

# API 요청 전송
print(f"\n[2/5] API 서버에 요청 전송 중...")
print(f"  URL: {api_url}")
print(f"  Session ID: {session_id}")

try:
    with open(image_path, 'rb') as f:
        files = {'image': (image_path.name, f, 'image/jpeg')}
        data = {
            'text': text_prompt,
            'session_id': session_id
        }
        
        start_time = time.time()
        response = requests.post(api_url, files=files, data=data, timeout=60)
        elapsed_time = time.time() - start_time
        
    print(f"  상태 코드: {response.status_code}")
    print(f"  응답 시간: {elapsed_time:.2f}초")
    
    if response.status_code != 200:
        print(f"  ❌ 오류: {response.text}")
        exit(1)
    
    response_data = response.json()
    
    # 결과 분석
    print(f"\n[3/5] 응답 분석...")
    print(f"  전체 상태: {response_data.get('status')}")
    print(f"  메시지: {response_data.get('message')}")
    
    # 단계별 결과
    print(f"\n[4/5] 단계별 처리 결과:")
    if 'data' in response_data and 'steps' in response_data['data']:
        steps = response_data['data']['steps']
        
        for step_id in sorted(steps.keys(), key=int):
            step_info = steps[step_id]
            status = step_info.get('status', 'unknown')
            step_result = step_info.get('result', {})
            
            status_icon = "✓" if status == "success" else "✗" if status == "error" else "?"
            print(f"\n  {status_icon} Step {step_id}: {status}")
            
            if step_id == "1":  # 이미지 분석
                analysis = step_result.get('analysis', {})
                print(f"      분석: {analysis.get('type', 'N/A')}")
                print(f"      이미지: {step_result.get('image_path', 'N/A')}")
            
            elif step_id == "2":  # 패턴 생성
                pattern_path = step_result.get('pattern_path', 'N/A')
                pattern_exists = Path(pattern_path).exists() if pattern_path != 'N/A' else False
                print(f"      패턴: {pattern_path}")
                print(f"      파일 존재: {'✓' if pattern_exists else '✗'}")
            
            elif step_id == "3":  # 3D 변환
                mesh_path = step_result.get('mesh_path', 'N/A')
                mesh_exists = Path(mesh_path).exists() if mesh_path != 'N/A' else False
                print(f"      3D 메시: {mesh_path}")
                print(f"      파일 존재: {'✓' if mesh_exists else '✗'}")
                if mesh_exists:
                    mesh_info = step_result.get('mesh_info', {})
                    print(f"      정점: {mesh_info.get('vertices', 'N/A')}")
                    print(f"      면: {mesh_info.get('faces', 'N/A')}")
                error = step_info.get('error')
                if error:
                    print(f"      오류: {error}")
            
            elif step_id == "4":  # 렌더링
                render_path = step_result.get('render_path', 'N/A')
                render_exists = Path(render_path).exists() if render_path != 'N/A' else False
                print(f"      렌더링: {render_path}")
                print(f"      파일 존재: {'✓' if render_exists else '✗'}")
    
    # 최종 결과
    print(f"\n[5/5] 최종 결과:")
    print("=" * 70)
    
    if response_data.get('status') == 'success':
        print("✓ 전체 프로세스 성공!")
        
        # 생성된 파일 확인
        pattern_file = Path("D:/AI/ChatGarment/outputs/patterns/pattern.json")
        mesh_file = Path("D:/AI/ChatGarment/outputs/3d_models/garment.obj")
        
        print("\n생성된 파일:")
        if pattern_file.exists():
            print(f"  ✓ 패턴: {pattern_file} ({pattern_file.stat().st_size} bytes)")
        if mesh_file.exists():
            print(f"  ✓ 3D 메시: {mesh_file} ({mesh_file.stat().st_size} bytes)")
        
        print("\n✅ 브라우저 테스트 시뮬레이션 완료!")
        print("   브라우저에서도 동일한 결과를 얻을 수 있습니다.")
    else:
        print(f"⚠ 상태: {response_data.get('status')}")
        print(f"   메시지: {response_data.get('message')}")
    
    # 결과 저장
    output_file = f"browser_test_result_{session_id}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(response_data, f, ensure_ascii=False, indent=2)
    print(f"\n  전체 응답이 '{output_file}'에 저장되었습니다.")
    
    print("\n" + "=" * 70)

except requests.exceptions.ConnectionError:
    print("  ❌ API 서버에 연결할 수 없습니다.")
    print("     API 서버가 실행 중인지 확인하세요: http://localhost:8000")
except requests.exceptions.Timeout:
    print("  ❌ 요청 시간 초과 (60초)")
except Exception as e:
    print(f"  ❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

