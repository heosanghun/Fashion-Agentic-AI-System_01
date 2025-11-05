"""
ChatGarment 모델 파일 검증 및 이동 스크립트
"""
import os
import shutil
import zipfile
from pathlib import Path

# 파일 경로
source_file = Path("ChatGarment/llava/model/pytorch_model.bin")
target_dir = Path("checkpoints/try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final")
target_file = target_dir / "pytorch_model.bin"

print("=" * 60)
print("ChatGarment 모델 파일 검증 및 이동")
print("=" * 60)
print()

# 원본 파일 확인
if not source_file.exists():
    print(f"[FAIL] 원본 파일을 찾을 수 없습니다: {source_file}")
    exit(1)

size = source_file.stat().st_size
size_gb = size / (1024 ** 3)

print(f"[*] 원본 파일 정보:")
print(f"    경로: {source_file.absolute()}")
print(f"    크기: {size_gb:.2f} GB ({size:,} bytes)")
print()

# 파일 타입 확인
print("[*] 파일 타입 확인 중...")
with open(source_file, 'rb') as f:
    header = f.read(4)

# ZIP 파일 확인 (50 4B 03 04)
if header.startswith(b'PK\x03\x04'):
    print("[OK] ZIP 파일로 확인됨")
    print("    PyTorch 모델이 ZIP 형식으로 저장되었을 수 있습니다.")
    print()
    
    # ZIP 파일 내용 확인
    print("[*] ZIP 파일 내용 확인 중...")
    try:
        with zipfile.ZipFile(source_file, 'r') as zf:
            file_list = zf.namelist()
            print(f"    ZIP 파일 내 항목 수: {len(file_list)}")
            if len(file_list) > 0:
                print(f"    첫 번째 항목: {file_list[0]}")
                print(f"    마지막 항목: {file_list[-1]}")
                
                # 특정 파일이 있는지 확인
                if 'pytorch_model.bin' in file_list:
                    print("[INFO] ZIP 파일 내부에 pytorch_model.bin이 있습니다.")
                    print("       ZIP 파일을 압축 해제해야 할 수 있습니다.")
                elif len(file_list) == 1 and file_list[0].endswith('.bin'):
                    print(f"[INFO] ZIP 파일 내부에 단일 .bin 파일이 있습니다: {file_list[0]}")
    except zipfile.BadZipFile:
        print("[경고] ZIP 파일이 아니거나 손상되었을 수 있습니다.")
    except Exception as e:
        print(f"[오류] ZIP 파일 확인 실패: {e}")
    
    print()
    print("[INFO] PyTorch 모델 파일은 때때로 ZIP 형식으로 저장됩니다.")
    print("       torch.save()는 기본적으로 ZIP 형식을 사용합니다.")
    print("       이 파일은 torch.load()로 직접 로드할 수 있습니다.")
    print()
elif header.startswith(b'<!DOCTYPE') or header.startswith(b'<html'):
    print("[FAIL] HTML 파일입니다!")
    print("    파일이 잘못되었습니다.")
    exit(1)
else:
    print("[OK] 바이너리 파일로 확인됨")
    print()

# 타겟 디렉토리 준비
target_dir.mkdir(parents=True, exist_ok=True)

# 파일 복사
if target_file.exists():
    existing_size = target_file.stat().st_size
    if existing_size == size:
        print(f"[INFO] 타겟 파일이 이미 존재하고 크기가 동일합니다.")
        print(f"    경로: {target_file.absolute()}")
        print(f"    크기: {existing_size / (1024**3):.2f} GB")
        print()
        print("[OK] 모델 파일이 올바른 위치에 있습니다!")
        exit(0)
    else:
        print(f"[INFO] 기존 파일 크기가 다릅니다 (기존: {existing_size / (1024**3):.2f} GB, 새: {size_gb:.2f} GB)")
        print(f"    파일을 교체합니다...")

print(f"[*] 파일을 다음 위치로 복사 중...")
print(f"    {target_file.absolute()}")
print()

try:
    # 파일 복사 (큰 파일이므로 shutil.copy 사용)
    print("[INFO] 큰 파일 복사 중... (시간이 걸릴 수 있습니다)")
    shutil.copy2(source_file, target_file)
    
    # 복사 확인
    copied_size = target_file.stat().st_size
    if copied_size == size:
        print(f"[OK] 파일 복사 완료!")
        print(f"    경로: {target_file.absolute()}")
        print(f"    크기: {copied_size / (1024**3):.2f} GB")
        print()
        print("[OK] ChatGarment 모델 파일이 올바른 위치에 설정되었습니다!")
        print("     ChatGarment 서비스를 재시작하면 실제 모델을 사용할 수 있습니다.")
    else:
        print(f"[경고] 복사된 파일 크기가 다릅니다!")
        print(f"    원본: {size:,} bytes")
        print(f"    복사본: {copied_size:,} bytes")
        
except Exception as e:
    print(f"[오류] 파일 복사 실패: {e}")
    print()
    print("수동으로 파일을 복사하세요:")
    print(f"  원본: {source_file.absolute()}")
    print(f"  대상: {target_file.absolute()}")

print()
print("=" * 60)

