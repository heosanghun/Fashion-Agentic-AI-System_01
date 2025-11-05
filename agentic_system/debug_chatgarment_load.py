"""
ChatGarment 모델 로딩 디버깅 스크립트
상세한 오류 정보 출력
"""
import sys
import traceback
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "agentic_system"))

print("=" * 60)
print("ChatGarment 모델 로딩 디버깅")
print("=" * 60)
print()

checkpoint_path = project_root / "checkpoints" / "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / "pytorch_model.bin"

if not checkpoint_path.exists():
    print(f"[FAIL] 체크포인트를 찾을 수 없습니다: {checkpoint_path}")
    exit(1)

print(f"[OK] 체크포인트: {checkpoint_path}")
print()

# 1. 임포트 테스트
print("[1] ChatGarment 모듈 임포트 테스트...")
try:
    from agentic_system.tools.chatgarment_integration import ChatGarmentPipeline, CHATGARMENT_AVAILABLE
    print(f"[OK] ChatGarmentPipeline 임포트 성공")
    print(f"    CHATGARMENT_AVAILABLE: {CHATGARMENT_AVAILABLE}")
except Exception as e:
    print(f"[FAIL] 임포트 실패: {e}")
    traceback.print_exc()
    exit(1)

print()

# 2. 기본 경로 확인
print("[2] 경로 확인...")
model_path = project_root / "checkpoints" / "llava-v1.5-7b"
print(f"    모델 경로: {model_path} (존재: {model_path.exists()})")
print(f"    체크포인트 경로: {checkpoint_path} (존재: {checkpoint_path.exists()})")

if not model_path.exists():
    print("[WARNING] 기본 모델 경로가 없습니다!")
    print("          기본 모델이 필요합니다: checkpoints/llava-v1.5-7b")

print()

# 3. Pipeline 생성 및 로딩 시도
print("[3] Pipeline 생성 및 모델 로딩 시도...")
print("    이 과정에서 발생하는 모든 오류를 확인합니다.")
print()

try:
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"    디바이스: {device}")
    
    pipeline = ChatGarmentPipeline(
        checkpoint_path=str(checkpoint_path),
        device=device
    )
    print("[OK] Pipeline 인스턴스 생성 완료")
    
    print()
    print("[*] 모델 로딩 시작...")
    print("    (상세 로그가 출력됩니다)")
    print()
    
    pipeline.load_model()
    
    print()
    if pipeline.model_loaded:
        print("[OK] 모델 로딩 성공!")
        print("     실제 ChatGarment 모델이 준비되었습니다!")
    else:
        print("[FAIL] 모델 로딩 실패!")
        print("      model_loaded = False")
        print("      위의 오류 메시지를 확인하세요.")
        
except Exception as e:
    print()
    print("=" * 60)
    print("[FAIL] 오류 발생!")
    print("=" * 60)
    print(f"오류 타입: {type(e).__name__}")
    print(f"오류 메시지: {str(e)}")
    print()
    print("상세 스택 트레이스:")
    traceback.print_exc()
    print()
    print("=" * 60)

print()
print("=" * 60)
print("디버깅 완료")
print("=" * 60)

