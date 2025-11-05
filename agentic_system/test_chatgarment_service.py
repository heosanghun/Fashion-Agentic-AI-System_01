"""
ChatGarment 서비스 테스트 스크립트
"""
import sys
import subprocess
from pathlib import Path

service_dir = Path(__file__).parent / "chatgarment_service"
main_py = service_dir / "main.py"

print(f"[테스트] 서비스 디렉토리: {service_dir}")
print(f"[테스트] main.py 존재: {main_py.exists()}")

if main_py.exists():
    print("[테스트] 서비스 시작 테스트...")
    try:
        # 서비스 시작 (5초 타임아웃)
        process = subprocess.Popen(
            [sys.executable, str(main_py)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(service_dir)
        )
        
        # 처음 몇 줄 출력 확인
        import time
        time.sleep(2)
        
        # 프로세스 상태 확인
        if process.poll() is None:
            print("[성공] 서비스가 시작되었습니다!")
            print("[안내] 서비스를 계속 실행하려면 별도 터미널에서 실행하세요:")
            print(f"  cd {service_dir}")
            print(f"  python main.py")
        else:
            stdout, stderr = process.communicate(timeout=3)
            print(f"[오류] 서비스가 종료되었습니다.")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            
    except Exception as e:
        print(f"[오류] 서비스 시작 실패: {e}")
else:
    print("[오류] main.py를 찾을 수 없습니다.")

