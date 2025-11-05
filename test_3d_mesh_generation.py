"""
3D 메시 파일 생성 직접 테스트
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "agentic_system"))

from agentic_system.tools.extensions import Extensions2DTo3D

# Mock 3D 변환 테스트
tool = Extensions2DTo3D()

# Mock 패턴 결과
mock_pattern_result = {
    "status": "success",
    "pattern_path": "D:/AI/ChatGarment/outputs/patterns/pattern.json",
    "pattern_info": {
        "type": "hoodie",
        "components": ["front", "back", "sleeves", "hood"],
    },
    "message": "패턴 생성이 완료되었습니다. (Mock 모드)"
}

print("=" * 60)
print("Mock 3D 메시 생성 테스트")
print("=" * 60)

# 3D 변환
result = tool._mock_convert_to_3d(mock_pattern_result)

print(f"\n결과:")
print(f"  상태: {result.get('status')}")
print(f"  메시 경로: {result.get('mesh_path')}")
print(f"  메시 정보: {result.get('mesh_info')}")

# 파일 존재 확인
mesh_path = Path(result.get('mesh_path'))
if mesh_path.exists():
    print(f"  ✓ 파일 존재 확인: {mesh_path}")
    print(f"  파일 크기: {mesh_path.stat().st_size} bytes")
    
    # 파일 내용 확인 (처음 몇 줄)
    with open(mesh_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:10]
    print(f"  파일 내용 (처음 10줄):")
    for i, line in enumerate(lines, 1):
        print(f"    {i}: {line.strip()}")
else:
    print(f"  ❌ 파일이 존재하지 않습니다: {mesh_path}")

print("\n" + "=" * 60)

