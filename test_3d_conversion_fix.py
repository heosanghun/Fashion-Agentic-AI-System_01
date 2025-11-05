"""
3D 변환 문제 해결 후 테스트
"""
import requests
from pathlib import Path
import json

# 이미지 파일 경로
image_path = Path("E:/0000000_T-Shirt/TEMP/TShirt.jpg")
api_url = "http://localhost:8000/api/v1/request"
session_id = "test_3d_fix_001"
text_prompt = "이 옷을 3D로 변환해주세요"

print("=" * 60)
print("3D 변환 문제 해결 후 테스트")
print("=" * 60)

# 이미지 파일 확인
print(f"\n[1/4] 이미지 파일 확인:")
if image_path.exists():
    print(f"  ✓ 파일 존재: {image_path}")
    print(f"  파일 크기: {image_path.stat().st_size / 1024:.2f} KB")
else:
    print(f"  ❌ 파일 없음: {image_path}")
    exit(1)

# API 요청 전송
print(f"\n[2/4] API 서버에 요청 전송 중...")
try:
    with open(image_path, 'rb') as f:
        files = {'image': (image_path.name, f, 'image/jpeg')}
        data = {'text': text_prompt, 'session_id': session_id}
        
        response = requests.post(api_url, files=files, data=data, timeout=60)
    
    print(f"  상태 코드: {response.status_code}")
    
    if response.status_code != 200:
        print(f"  ❌ 오류: {response.text}")
        exit(1)
    
    response_data = response.json()
    
    # 결과 분석
    print(f"\n[3/4] 결과 분석:")
    print(f"  전체 상태: {response_data.get('status')}")
    print(f"  메시지: {response_data.get('message')}")
    
    # 단계별 결과 확인
    if 'data' in response_data and 'steps' in response_data['data']:
        steps = response_data['data']['steps']
        print(f"\n  처리 단계 ({len(steps)}개):")
        
        for step_id, step_info in steps.items():
            status = step_info.get('status', 'unknown')
            step_result = step_info.get('result', {})
            
            print(f"\n    Step {step_id}: {status}")
            
            if step_id == "1":  # 이미지 분석
                analysis = step_result.get('analysis', {})
                print(f"      분석 결과: {analysis.get('type', 'N/A')}")
                print(f"      이미지 경로: {step_result.get('image_path', 'N/A')}")
            
            elif step_id == "2":  # 패턴 생성
                pattern_path = step_result.get('pattern_path', 'N/A')
                print(f"      패턴 경로: {pattern_path}")
                # 실제 파일 존재 확인
                if pattern_path != 'N/A' and Path(pattern_path).exists():
                    print(f"      ✓ 패턴 파일 존재함")
                else:
                    print(f"      ❌ 패턴 파일 없음")
            
            elif step_id == "3":  # 3D 변환
                mesh_path = step_result.get('mesh_path', 'N/A')
                print(f"      3D 메시 경로: {mesh_path}")
                # 실제 파일 존재 확인
                if mesh_path != 'N/A' and Path(mesh_path).exists():
                    print(f"      ✓ 3D 메시 파일 존재함")
                    mesh_info = step_result.get('mesh_info', {})
                    print(f"      정점 수: {mesh_info.get('vertices', 'N/A')}")
                    print(f"      면 수: {mesh_info.get('faces', 'N/A')}")
                else:
                    print(f"      ❌ 3D 메시 파일 없음")
                error = step_info.get('error')
                if error:
                    print(f"      오류: {error}")
            
            elif step_id == "4":  # 렌더링
                render_path = step_result.get('render_path', 'N/A')
                print(f"      렌더링 경로: {render_path}")
                if render_path != 'N/A' and Path(render_path).exists():
                    print(f"      ✓ 렌더링 이미지 존재함")
                else:
                    print(f"      ❌ 렌더링 이미지 없음")
    
    # 결과 저장
    print(f"\n[4/4] 결과 저장 중...")
    with open("test_3d_fix_response.json", "w", encoding="utf-8") as f:
        json.dump(response_data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 결과가 'test_3d_fix_response.json'에 저장되었습니다.")
    
    # 최종 평가
    print(f"\n" + "=" * 60)
    print("최종 평가:")
    print("=" * 60)
    
    if response_data.get('status') == 'success':
        print("✓ 전체 프로세스 성공!")
    else:
        print(f"⚠ 전체 프로세스 상태: {response_data.get('status')}")
        print(f"  메시지: {response_data.get('message')}")
    
    # 파일 생성 확인
    pattern_file = Path("D:/AI/ChatGarment/outputs/patterns/pattern.json")
    mesh_file = Path("D:/AI/ChatGarment/outputs/3d_models/garment.obj")
    
    print(f"\n생성된 파일 확인:")
    if pattern_file.exists():
        print(f"  ✓ 패턴 파일: {pattern_file}")
    else:
        print(f"  ❌ 패턴 파일 없음: {pattern_file}")
    
    if mesh_file.exists():
        print(f"  ✓ 3D 메시 파일: {mesh_file}")
        print(f"    파일 크기: {mesh_file.stat().st_size} bytes")
    else:
        print(f"  ❌ 3D 메시 파일 없음: {mesh_file}")

except requests.exceptions.ConnectionError:
    print("  ❌ API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
except Exception as e:
    print(f"  ❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

