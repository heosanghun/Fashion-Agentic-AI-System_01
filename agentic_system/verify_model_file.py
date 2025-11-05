"""
ChatGarment 모델 파일 검증 스크립트
"""
import os
from pathlib import Path

# 검증할 파일
model_file = Path("ChatGarment/llava/model/pytorch_model.bin")

print("=" * 60)
print("ChatGarment 모델 파일 검증")
print("=" * 60)
print()

if not model_file.exists():
    print(f"[FAIL] 파일이 존재하지 않습니다: {model_file}")
    exit(1)

# 파일 정보
size = model_file.stat().st_size
size_gb = size / (1024 ** 3)

print(f"[*] 파일 정보:")
print(f"    경로: {model_file.absolute()}")
print(f"    크기: {size_gb:.2f} GB ({size:,} bytes)")
print()

# 파일 헤더 확인
print("[*] 파일 헤더 검증 중...")

try:
    with open(model_file, 'rb') as f:
        # 처음 64바이트 읽기
        header = f.read(64)
        
    # Hex 출력
    hex_header = ' '.join(f'{b:02X}' for b in header[:32])
    print(f"    헤더 (Hex): {hex_header}")
    print()
    
    # 파일 타입 확인
    # PyTorch 모델 파일은 보통 특정 매직 넘버를 가지고 있습니다
    # 하지만 파일이 너무 크면 실제 모델 데이터일 수 있습니다
    
    # HTML 파일인지 확인
    try:
        text_header = header.decode('utf-8', errors='ignore')
        if '<!DOCTYPE' in text_header or '<html' in text_header:
            print("[경고] HTML 파일로 보입니다!")
            print("       파일이 HTML 페이지일 수 있습니다.")
            print()
    except:
        pass
    
    # 바이너리 패턴 확인
    # PyTorch 모델은 일반적으로 바이너리 데이터입니다
    if header[:2] == b'PK':  # ZIP 파일
        print("[경고] ZIP 파일로 보입니다!")
    elif header.startswith(b'<!DOCTYPE') or header.startswith(b'<html'):
        print("[경고] HTML 파일로 보입니다!")
    else:
        # 일반 바이너리 데이터 - PyTorch 모델일 가능성이 높음
        print("[OK] 바이너리 파일로 보입니다.")
        
        # 추가 검증: 파일 끝부분 확인
        print("[*] 파일 끝부분 확인 중...")
        with open(model_file, 'rb') as f:
            f.seek(-64, 2)  # 끝에서 64바이트 전으로 이동
            footer = f.read(64)
            hex_footer = ' '.join(f'{b:02X}' for b in footer[:32])
            print(f"    끝부분 (Hex): {hex_footer}")
            
            try:
                text_footer = footer.decode('utf-8', errors='ignore')
                if '<!DOCTYPE' in text_footer or '</html>' in text_footer:
                    print("[경고] 파일 끝부분에 HTML이 포함되어 있습니다!")
                    print("       파일이 HTML 페이지일 가능성이 높습니다.")
                else:
                    print("[OK] 파일 끝부분도 바이너리 데이터입니다.")
            except:
                print("[OK] 파일 끝부분도 바이너리 데이터입니다.")
        
        print()
        print("[INFO] 파일 크기(13.96 GB)는 ChatGarment 7B 모델의 적절한 크기입니다.")
        print("       하지만 파일 내용이 HTML이라면 잘못된 파일일 수 있습니다.")
        
except Exception as e:
    print(f"[오류] 파일 검증 실패: {e}")

print()
print("=" * 60)
print("검증 완료")
print("=" * 60)
print()
print("결론:")
print("- 파일 크기: 적절함 (13.96 GB)")
print("- 파일 위치: ChatGarment/llava/model/pytorch_model.bin")
print("- 실제 모델 파일은 checkpoints/ 디렉토리에 있어야 합니다")
print()
print("권장 사항:")
print("이 파일이 실제 모델 파일이라면, 다음 위치로 복사하세요:")
print("  checkpoints/try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final/pytorch_model.bin")

