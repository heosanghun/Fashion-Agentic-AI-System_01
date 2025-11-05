#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빠른 통합 테스트 스크립트
ChatGarment 파이프라인의 기본 기능 확인
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "agentic_system"))

def test_imports():
    """필수 모듈 임포트 테스트"""
    print("=" * 60)
    print("1. 필수 모듈 임포트 테스트")
    print("=" * 60)
    
    modules = [
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("PIL", "Pillow"),
        ("numpy", "NumPy"),
    ]
    
    success = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} (누락)")
            success = False
    
    return success

def test_cuda():
    """CUDA 사용 가능 여부 확인"""
    print("\n" + "=" * 60)
    print("2. CUDA 환경 확인")
    print("=" * 60)
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA 사용 가능")
            print(f"   CUDA 버전: {torch.version.cuda}")
            print(f"   GPU 개수: {torch.cuda.device_count()}")
            print(f"   GPU 이름: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("⚠️  CUDA 사용 불가 (CPU 모드)")
            return False
    except ImportError:
        print("❌ PyTorch가 설치되어 있지 않습니다.")
        return False

def test_chatgarment_structure():
    """ChatGarment 디렉토리 구조 확인"""
    print("\n" + "=" * 60)
    print("3. ChatGarment 디렉토리 구조 확인")
    print("=" * 60)
    
    chatgarment_path = project_root / "ChatGarment"
    required_paths = [
        ("ChatGarment/llava", "LLaVA 모듈"),
        ("ChatGarment/llava/model", "모델 디렉토리"),
        ("ChatGarment/llava/garment_utils_v2.py", "유틸리티"),
    ]
    
    success = True
    for rel_path, description in required_paths:
        full_path = project_root / rel_path
        if full_path.exists():
            print(f"✅ {description}: {rel_path}")
        else:
            print(f"❌ {description}: {rel_path} (누락)")
            success = False
    
    return success

def test_checkpoints():
    """체크포인트 파일 확인"""
    print("\n" + "=" * 60)
    print("4. 모델 체크포인트 확인")
    print("=" * 60)
    
    checkpoint_path = project_root / "checkpoints" / "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / "pytorch_model.bin"
    base_model_path = project_root / "checkpoints" / "llava-v1.5-7b"
    
    success = True
    
    if checkpoint_path.exists():
        size_mb = checkpoint_path.stat().st_size / (1024 * 1024)
        print(f"✅ ChatGarment 체크포인트: {size_mb:.1f} MB")
    else:
        print(f"⚠️  ChatGarment 체크포인트를 찾을 수 없습니다: {checkpoint_path}")
        success = False
    
    if base_model_path.exists():
        print(f"✅ 기본 모델 디렉토리 발견")
    else:
        print(f"⚠️  기본 모델 디렉토리를 찾을 수 없습니다: {base_model_path}")
    
    return success

def test_integration_module():
    """통합 모듈 임포트 테스트"""
    print("\n" + "=" * 60)
    print("5. 통합 모듈 임포트 테스트")
    print("=" * 60)
    
    try:
        from agentic_system.tools.chatgarment_integration import ChatGarmentPipeline
        print("✅ ChatGarmentPipeline 임포트 성공")
        
        # 파이프라인 초기화 테스트
        pipeline = ChatGarmentPipeline(device="cpu")  # CPU로 빠른 테스트
        print("✅ ChatGarmentPipeline 초기화 성공")
        
        return True
    except Exception as e:
        print(f"❌ 통합 모듈 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_garmentcode():
    """GarmentCodeRC 확인"""
    print("\n" + "=" * 60)
    print("6. GarmentCodeRC 확인")
    print("=" * 60)
    
    garmentcode_path = project_root / "GarmentCodeRC"
    
    if garmentcode_path.exists():
        print(f"✅ GarmentCodeRC 디렉토리 발견")
        
        sim_props = garmentcode_path / "assets" / "Sim_props" / "default_sim_props.yaml"
        if sim_props.exists():
            print(f"✅ 시뮬레이션 설정 파일 발견")
            return True
        else:
            print(f"⚠️  시뮬레이션 설정 파일 누락")
            return False
    else:
        print(f"⚠️  GarmentCodeRC 디렉토리를 찾을 수 없습니다")
        print("   3D 변환 기능은 사용할 수 없습니다.")
        return False

def main():
    """메인 테스트 함수"""
    print("\n" + "=" * 60)
    print("ChatGarment 통합 빠른 테스트")
    print("=" * 60 + "\n")
    
    results = {
        "임포트": test_imports(),
        "CUDA": test_cuda(),
        "ChatGarment 구조": test_chatgarment_structure(),
        "체크포인트": test_checkpoints(),
        "통합 모듈": test_integration_module(),
        "GarmentCodeRC": test_garmentcode(),
    }
    
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 모든 테스트 통과!")
        print("\n다음 단계:")
        print("  python3 test_chatgarment_integration.py --image <이미지_경로> --device cuda")
        return 0
    else:
        print("\n⚠️  일부 테스트 실패")
        print("필수 구성 요소를 확인하고 수정해주세요.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

