"""
ChatGarment Pipeline 직접 테스트
ChatGarmentPipeline이 실제로 로드되고 작동하는지 확인
"""
import sys
from pathlib import Path

# 프로젝트 경로 설정
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "agentic_system"))

print("=" * 60)
print("ChatGarment Pipeline 직접 테스트")
print("=" * 60)
print()

# 1. 모듈 임포트 테스트
print("[1/6] ChatGarment 모듈 임포트 테스트...")
try:
    from agentic_system.tools.chatgarment_integration import ChatGarmentPipeline
    print("[OK] ChatGarmentPipeline 임포트 성공!")
except Exception as e:
    print(f"[FAIL] ChatGarmentPipeline 임포트 실패: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# 2. 체크포인트 경로 확인
print("[2/6] 체크포인트 경로 확인...")
checkpoint_paths = [
    project_root / "checkpoints" / "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / "pytorch_model.bin",
    project_root.parent / "checkpoints" / "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / "pytorch_model.bin",
]

checkpoint_path = None
for cp_path in checkpoint_paths:
    if cp_path.exists():
        checkpoint_path = cp_path
        print(f"[OK] 체크포인트 발견: {checkpoint_path}")
        size = cp_path.stat().st_size / (1024 ** 3)
        print(f"    크기: {size:.2f} GB")
        break

if checkpoint_path is None:
    print("[FAIL] 체크포인트를 찾을 수 없습니다!")
    print("    시도한 경로들:")
    for cp_path in checkpoint_paths:
        print(f"      - {cp_path} (존재: {cp_path.exists()})")
    exit(1)

print()

# 3. CUDA 확인
print("[3/6] CUDA 디바이스 확인...")
try:
    import torch
    cuda_available = torch.cuda.is_available()
    device = "cuda" if cuda_available else "cpu"
    print(f"[OK] 디바이스: {device}")
    if cuda_available:
        print(f"    GPU: {torch.cuda.get_device_name(0)}")
        print(f"    GPU 메모리: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
except Exception as e:
    print(f"[INFO] CUDA 확인 실패: {e}")
    device = "cpu"
    print(f"[INFO] CPU 모드로 진행합니다")

print()

# 4. Pipeline 인스턴스 생성
print("[4/6] ChatGarmentPipeline 인스턴스 생성...")
try:
    pipeline = ChatGarmentPipeline(
        checkpoint_path=str(checkpoint_path),
        device=device
    )
    print("[OK] Pipeline 인스턴스 생성 성공!")
except Exception as e:
    print(f"[FAIL] Pipeline 인스턴스 생성 실패: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# 5. 모델 로딩 시도
print("[5/6] ChatGarment 모델 로딩 시도...")
print("      이 작업은 시간이 걸릴 수 있습니다 (13.96 GB 모델)...")
print()

try:
    pipeline.load_model()
    
    if pipeline.model_loaded:
        print("[OK] ChatGarment 모델 로딩 완료!")
        print("     실제 모델이 준비되었습니다!")
    else:
        print("[WARNING] 모델 로딩이 완료되지 않았습니다")
        print("          model_loaded = False")
        
except Exception as e:
    print(f"[FAIL] 모델 로딩 실패: {e}")
    import traceback
    traceback.print_exc()
    print()
    print("[INFO] 오류 상세 내용을 확인하세요.")
    exit(1)

print()

# 6. 간단한 테스트 (모델이 로드되었을 때만)
if pipeline.model_loaded:
    print("[6/6] Pipeline 작동 확인...")
    print("[INFO] 모델이 로드되었습니다. 실제 3D 변환 테스트를 위해")
    print("      이미지를 업로드하여 테스트하세요.")
    print()
    print("[OK] ChatGarment Pipeline이 정상적으로 작동합니다!")
else:
    print("[6/6] Pipeline 작동 확인 건너뜀 (모델 미로드)")

print()
print("=" * 60)
print("테스트 완료")
print("=" * 60)
print()

if pipeline.model_loaded:
    print("[SUCCESS] ChatGarment Pipeline이 실제 모델로 준비되었습니다!")
    print("          서비스에서 실제 3D 변환을 사용할 수 있습니다.")
else:
    print("[WARNING] 모델이 로드되지 않았습니다.")
    print("          서비스는 Mock 모드로 동작합니다.")

