"""
ChatGarment 마이크로서비스 클라이언트
Windows 백엔드에서 리눅스 서버의 ChatGarment 서비스 호출
"""

import requests
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수에서 서비스 URL 가져오기
CHATGARMENT_SERVICE_URL = os.getenv(
    "CHATGARMENT_SERVICE_URL",
    "http://localhost:9000"  # 기본값 (로컬 테스트용)
)

class ChatGarmentServiceClient:
    """ChatGarment 마이크로서비스 클라이언트"""
    
    def __init__(self, service_url: Optional[str] = None):
        self.service_url = service_url or CHATGARMENT_SERVICE_URL
        self.base_url = f"{self.service_url}/api/v1"
    
    def health_check(self) -> bool:
        """서비스 헬스 체크"""
        try:
            response = requests.get(f"{self.service_url}/health", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def analyze_image(self, image_path: str, text: Optional[str] = None) -> Dict[str, Any]:
        """
        이미지 분석
        
        Args:
            image_path: 이미지 파일 경로
            text: 선택적 텍스트 설명
            
        Returns:
            분석 결과
        """
        try:
            with open(image_path, "rb") as f:
                files = {"image": f}
                data = {}
                if text:
                    data["text"] = text
                
                response = requests.post(
                    f"{self.base_url}/analyze",
                    files=files,
                    data=data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "status": "error",
                        "error": f"서비스 오류: {response.status_code}",
                        "message": response.text
                    }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": "서비스 타임아웃",
                "message": "ChatGarment 서비스 응답 시간 초과"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "서비스 연결 오류"
            }
    
    def process_image(
        self,
        image_path: str,
        text: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        전체 파이프라인 실행 (이미지 분석 + 3D 생성)
        
        Args:
            image_path: 이미지 파일 경로
            text: 선택적 텍스트 설명
            output_dir: 출력 디렉토리 (선택사항)
            
        Returns:
            전체 처리 결과
        """
        try:
            with open(image_path, "rb") as f:
                files = {"image": f}
                data = {}
                if text:
                    data["text"] = text
                if output_dir:
                    data["output_dir"] = output_dir
                
                response = requests.post(
                    f"{self.base_url}/process",
                    files=files,
                    data=data,
                    timeout=300  # 5분 타임아웃 (3D 생성 시간 고려)
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "status": "error",
                        "error": f"서비스 오류: {response.status_code}",
                        "message": response.text
                    }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": "서비스 타임아웃",
                "message": "ChatGarment 서비스 응답 시간 초과 (5분)"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "서비스 연결 오류"
            }

def chatgarment_service_tool(action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    ChatGarment 마이크로서비스 도구
    
    Args:
        action: 실행할 액션 (analyze, process)
        parameters: 액션에 필요한 파라미터
        context: 실행 컨텍스트
        
    Returns:
        실행 결과
    """
    # 환경 변수 확인
    service_url = os.getenv("CHATGARMENT_SERVICE_URL", "http://localhost:9000")
    logger.info(f"[ChatGarmentServiceTool] 서비스 URL: {service_url}")
    
    client = ChatGarmentServiceClient(service_url=service_url)
    
    # 서비스 헬스 체크
    logger.info(f"[ChatGarmentServiceTool] 헬스 체크 시작: {service_url}/health")
    if not client.health_check():
        logger.error(f"[ChatGarmentServiceTool] 헬스 체크 실패")
        return {
            "status": "error",
            "error": "ChatGarment 서비스에 연결할 수 없습니다",
            "message": f"서비스 URL: {client.service_url}",
            "suggestion": "리눅스 서버에서 ChatGarment 서비스가 실행 중인지 확인하세요."
        }
    
    logger.info(f"[ChatGarmentServiceTool] 헬스 체크 성공")
    
    image_path = parameters.get("image_path") or context.get("image_path")
    logger.info(f"[ChatGarmentServiceTool] 이미지 경로: {image_path}")
    if not image_path:
        logger.error(f"[ChatGarmentServiceTool] 이미지 경로가 없습니다")
        return {
            "status": "error",
            "error": "이미지 경로가 필요합니다"
        }
    
    if not Path(image_path).exists():
        logger.error(f"[ChatGarmentServiceTool] 이미지 파일이 없습니다: {image_path}")
        return {
            "status": "error",
            "error": f"이미지 파일을 찾을 수 없습니다: {image_path}"
        }
    
    text = parameters.get("text_description") or context.get("text")
    logger.info(f"[ChatGarmentServiceTool] 액션: {action}, 텍스트: {text}")
    
    if action == "analyze":
        logger.info(f"[ChatGarmentServiceTool] 이미지 분석 시작...")
        result = client.analyze_image(image_path, text)
        logger.info(f"[ChatGarmentServiceTool] 이미지 분석 결과: status={result.get('status')}")
        return result
    
    elif action == "process":
        output_dir = parameters.get("output_dir") or context.get("output_dir")
        logger.info(f"[ChatGarmentServiceTool] 전체 파이프라인 처리 시작...")
        result = client.process_image(image_path, text, output_dir)
        logger.info(f"[ChatGarmentServiceTool] 전체 파이프라인 처리 결과: status={result.get('status')}")
        return result
    
    else:
        logger.error(f"[ChatGarmentServiceTool] 지원하지 않는 액션: {action}")
        return {
            "status": "error",
            "error": f"지원하지 않는 액션: {action}"
        }
