"""
API 서버와 ChatGarment 서비스 통합 테스트
"""
import requests
import time
from pathlib import Path

print("=" * 60)
print("API Server and ChatGarment Service Integration Test")
print("=" * 60)
print()

# 서비스 상태 확인
print("[*] Checking services...")

# ChatGarment 서비스 확인
try:
    response = requests.get("http://localhost:9000/health", timeout=3)
    if response.status_code == 200:
        print("[OK] ChatGarment Service is running")
        print(f"    Response: {response.json()}")
    else:
        print(f"[FAIL] ChatGarment Service returned status {response.status_code}")
except Exception as e:
    print(f"[FAIL] ChatGarment Service is not running: {e}")
    print("    Please start ChatGarment service first:")
    print("    cd agentic_system\\chatgarment_service")
    print("    python main.py")
    exit(1)

# API 서버 확인
try:
    response = requests.get("http://localhost:8000/health", timeout=3)
    if response.status_code == 200:
        print("[OK] API Server is running")
        print(f"    Response: {response.json()}")
    else:
        print(f"[FAIL] API Server returned status {response.status_code}")
except Exception as e:
    print(f"[FAIL] API Server is not running: {e}")
    print("    Please start API server first:")
    print("    cd agentic_system")
    print("    python start_api_server.py")
    exit(1)

print()

# 환경 변수 확인
import os
print("[*] Checking environment variables...")
chatgarment_url = os.getenv("CHATGARMENT_SERVICE_URL", "http://localhost:9000")
use_service = os.getenv("USE_CHATGARMENT_SERVICE", "false")
print(f"    CHATGARMENT_SERVICE_URL: {chatgarment_url}")
print(f"    USE_CHATGARMENT_SERVICE: {use_service}")

if use_service.lower() != "true":
    print("[WARNING] USE_CHATGARMENT_SERVICE is not set to 'true'")
    print("    API server will use mock mode instead of ChatGarment service")

print()

# 간단한 테스트 이미지 업로드
print("[*] Testing image upload (if test image exists)...")
test_image_path = Path("uploads")
if test_image_path.exists():
    test_images = list(test_image_path.glob("*.jpg")) + list(test_image_path.glob("*.png"))
    if test_images:
        test_image = test_images[0]
        print(f"    Found test image: {test_image}")
        print("    (You can test with this image via the frontend)")
    else:
        print("    No test images found in uploads directory")
else:
    print("    Uploads directory not found")

print()
print("=" * 60)
print("Integration Test Complete")
print("=" * 60)
print()
print("Next Steps:")
print("1. Open frontend: http://localhost:5173")
print("2. Upload an image and submit")
print("3. Check the result for 3D conversion")

