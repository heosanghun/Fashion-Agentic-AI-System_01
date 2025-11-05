"""
ChatGarment 모델 가중치 다운로드 스크립트

SharePoint 링크에서 직접 다운로드가 필요합니다.
"""
import os
import webbrowser
from pathlib import Path
import sys

# 다운로드 정보
download_url = "https://sjtueducn-my.sharepoint.com/:u:/g/personal/biansiyuan_sjtu_edu_cn/EQayoB8ie7ZIsFrjLWdBASQBFexZHXcGjrS6ghgGCjIMzw?e=o60Y65"
checkpoint_dir = Path("checkpoints/try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final")
target_file = checkpoint_dir / "pytorch_model.bin"

print("=" * 60)
print("ChatGarment 모델 가중치 다운로드")
print("=" * 60)
print()

# 디렉토리 생성
checkpoint_dir.mkdir(parents=True, exist_ok=True)
print(f"[OK] 디렉토리 준비: {checkpoint_dir}")
print()

# 파일 존재 확인
if target_file.exists():
    size = target_file.stat().st_size
    size_mb = size / (1024 * 1024)
    print(f"[INFO] 파일이 이미 존재합니다: {target_file}")
    print(f"       크기: {size_mb:.2f} MB")
    
    # 파일 크기가 작으면 잘못된 파일
    if size_mb < 100:  # 100MB 미만이면 잘못된 파일로 간주
        print(f"[경고] 파일 크기가 작습니다. 일반적으로 7B 모델은 수 GB 이상입니다.")
        print(f"       파일을 확인하시거나 다시 다운로드하세요.")
        print()
    else:
        print(f"[OK] 파일 크기가 적절합니다.")
        sys.exit(0)

print("[INFO] SharePoint 링크는 브라우저에서 직접 다운로드가 필요합니다.")
print()
print("다운로드 URL:")
print(download_url)
print()
print("[*] 브라우저를 열고 다운로드를 진행합니다...")

# 브라우저에서 링크 열기
try:
    webbrowser.open(download_url)
    print("[OK] 브라우저가 열렸습니다.")
except Exception as e:
    print(f"[오류] 브라우저 열기 실패: {e}")

print()
print("=" * 60)
print("다운로드 안내")
print("=" * 60)
print()
print("1. 브라우저에서 SharePoint 페이지가 열립니다.")
print("2. '다운로드' 버튼을 클릭하여 파일을 다운로드합니다.")
print("3. 다운로드한 파일의 이름을 확인합니다.")
print("4. 다운로드한 파일을 다음 경로로 이동하세요:")
print(f"   {target_file.absolute()}")
print()
print("또는 수동으로 파일을 이동한 후 이 스크립트를 다시 실행하여")
print("파일 위치를 확인할 수 있습니다.")
print()
print("=" * 60)

