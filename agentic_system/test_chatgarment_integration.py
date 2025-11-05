#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ChatGarment 실제 통합 테스트 스크립트

이 스크립트는 실제로 ChatGarment VLM이 이미지를 인식하여
JSON을 생성하고, GarmentCodeRC로 실제 3D 옷을 생성하는지 테스트합니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "agentic_system"))

from agentic_system.tools.chatgarment_integration import ChatGarmentPipeline
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="ChatGarment 실제 통합 테스트"
    )
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="테스트할 의류 이미지 경로"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="출력 디렉토리 (기본값: outputs/garments)"
    )
    parser.add_argument(
        "--garment-id",
        type=str,
        default=None,
        help="의류 ID (기본값: 자동 생성)"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        choices=["cuda", "cpu"],
        help="디바이스 (cuda 또는 cpu)"
    )
    
    args = parser.parse_args()
    
    # 이미지 파일 존재 확인
    if not os.path.exists(args.image):
        print(f"❌ 오류: 이미지 파일을 찾을 수 없습니다: {args.image}")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("ChatGarment 실제 통합 테스트")
    print("="*70)
    print(f"입력 이미지: {args.image}")
    print(f"출력 디렉토리: {args.output or 'outputs/garments'}")
    print(f"디바이스: {args.device}")
    print("="*70 + "\n")
    
    # 파이프라인 생성
    pipeline = ChatGarmentPipeline(device=args.device)
    
    # 모델 로딩
    print("📦 ChatGarment 모델 로딩 중...")
    pipeline.load_model()
    
    if not pipeline.model_loaded:
        print("\n❌ 모델을 로딩할 수 없습니다.")
        print("\n체크리스트:")
        print("1. ChatGarment 체크포인트가 있는지 확인:")
        print(f"   {pipeline.checkpoint_path}")
        print("2. 필요한 패키지가 설치되어 있는지 확인:")
        print("   pip install -r ChatGarment/requirements.txt")
        print("3. GPU가 사용 가능한지 확인 (CUDA)")
        sys.exit(1)
    
    # 이미지 처리 및 3D 의류 생성
    print("\n🔄 이미지 처리 시작...\n")
    
    result = pipeline.process_image_to_garment(
        image_path=args.image,
        output_dir=args.output,
        garment_id=args.garment_id
    )
    
    # 결과 출력
    print("\n" + "="*70)
    print("테스트 결과")
    print("="*70)
    
    if result["status"] == "success":
        print("✅ 성공!")
        print(f"\n생성된 파일들:")
        print(f"  - 출력 디렉토리: {result['output_dir']}")
        if result.get("json_spec_path"):
            print(f"  - JSON Specification: {result['json_spec_path']}")
        if result.get("mesh_path"):
            print(f"  - 3D 메시 파일: {result['mesh_path']}")
            print(f"\n✨ 3D 의류 생성 완료!")
            print(f"\n결과 확인:")
            print(f"  - 디렉토리: {result['output_dir']}")
            print(f"  - 3D 모델: {result.get('mesh_path', '생성 중...')}")
        else:
            print(f"\n⚠️ JSON 패턴은 생성되었지만 3D 변환은 완료되지 않았습니다.")
            print(f"GarmentCodeRC 시뮬레이션을 수동으로 실행할 수 있습니다:")
            if result.get("json_spec_path"):
                print(f"  python ChatGarment/run_garmentcode_sim.py --json_spec_file \"{result['json_spec_path']}\"")
    else:
        print("❌ 실패!")
        print(f"\n오류: {result.get('error', '알 수 없는 오류')}")
        if result.get("traceback"):
            print(f"\n상세 오류:")
            print(result["traceback"])
        sys.exit(1)
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

