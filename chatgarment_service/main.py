#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGarment 독립 서비스 (마이크로서비스)

리눅스 환경에서 독립적으로 실행되는 ChatGarment API 서버
"""

import os
import sys
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# 실제 파이프라인 사용 여부 (환경 변수로 제어)
ENABLE_REAL_PIPELINE = os.getenv("ENABLE_REAL_PIPELINE", "false").lower() == "true"
ChatGarmentPipeline = None
if ENABLE_REAL_PIPELINE:
    try:
        sys.path.insert(0, str(project_root / "agentic_system"))
        from agentic_system.tools.chatgarment_integration import ChatGarmentPipeline  # type: ignore
        print("[Service] Real ChatGarmentPipeline import success")
    except Exception as e:
        print(f"[Service] Pipeline import failed: {e}. Fallback to mock mode.")
        ChatGarmentPipeline = None

# FastAPI 앱 생성
app = FastAPI(
    title="ChatGarment Service",
    description="ChatGarment 독립 서비스 - 2D 이미지를 3D 의류로 변환",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
pipeline: Optional[ChatGarmentPipeline] = None
DEVICE = os.getenv("DEVICE", "cuda")
OUTPUT_BASE_DIR = Path(os.getenv("OUTPUT_DIR", "outputs/garments"))


class ProcessRequest(BaseModel):
    """처리 요청 모델"""
    image_path: Optional[str] = None
    garment_id: Optional[str] = None
    output_dir: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 모델 로딩"""
    global pipeline
    
    print("=" * 60)
    print("ChatGarment 서비스 시작 중...")
    print("=" * 60)
    
    if ChatGarmentPipeline is not None:
        try:
            pipeline = ChatGarmentPipeline(device=DEVICE)
            print("📦 ChatGarment 모델 로딩 시도...")
            pipeline.load_model()
            print("✅ 파이프라인 로딩 완료" if getattr(pipeline, "model_loaded", False) else "⚠️ 파이프라인 로딩 실패")
        except Exception as e:
            print(f"❌ 파이프라인 초기화 오류: {e}")
            pipeline = None
            print("모의 모드로 계속 실행합니다.")
    else:
        # 경량/모의 모드: 실제 모델은 로드하지 않음
        pipeline = None
        print("모의 모드로 시작합니다. (파이프라인 미로딩)")
    
    print("=" * 60)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "ChatGarment Service",
        "status": "running",
        "model_loaded": pipeline.model_loaded if pipeline else False,
        "device": DEVICE
    }


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트
    모델이 로드되지 않아도 서비스는 헬시로 응답(모의 처리 가능)
    """
    model_loaded = False
    if pipeline is not None:
        try:
            model_loaded = bool(pipeline.model_loaded)
        except Exception:
            model_loaded = False
    return {
        "status": "healthy",
        "model_loaded": model_loaded,
        "device": DEVICE
    }


@app.post("/api/v1/process")
async def process_image(
    image: UploadFile = File(...),
    garment_id: Optional[str] = None,
    output_dir: Optional[str] = None
):
    """
    이미지를 처리하여 3D 의류 생성
    
    Args:
        image: 업로드된 이미지 파일
        garment_id: 의류 ID (선택사항)
        output_dir: 출력 디렉토리 (선택사항)
    
    Returns:
        처리 결과 (JSON)
    """
    # 모델이 없으면 모의 처리로 응답하여 상위 시스템이 계속 진행할 수 있게 함
    if not pipeline or not getattr(pipeline, "model_loaded", False):
        # 업로드 파일 저장만 수행
        upload_dir = OUTPUT_BASE_DIR / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        image_id = str(uuid.uuid4())
        image_ext = Path(image.filename).suffix if image.filename else ".jpg"
        image_path = upload_dir / f"{image_id}{image_ext}"
        with open(image_path, "wb") as f:
            content = await image.read()
            f.write(content)
        return JSONResponse(content={
            "status": "success",
            "message": "모델 미로딩: 업로드만 완료 (Mock 처리)",
            "image_path": str(image_path)
        })
    
    # 임시 이미지 저장
    upload_dir = OUTPUT_BASE_DIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    image_id = str(uuid.uuid4())
    image_ext = Path(image.filename).suffix if image.filename else ".jpg"
    image_path = upload_dir / f"{image_id}{image_ext}"
    
    try:
        # 이미지 저장
        with open(image_path, "wb") as f:
            content = await image.read()
            f.write(content)
        
        # 출력 디렉토리 설정
        if output_dir is None:
            output_dir = str(OUTPUT_BASE_DIR / "processed")
        os.makedirs(output_dir, exist_ok=True)
        
        # ChatGarment 파이프라인 실행
        result = pipeline.process_image_to_garment(
            image_path=str(image_path),
            output_dir=output_dir,
            garment_id=garment_id or f"garment_{image_id[:8]}"
        )
        
        # 이미지 경로를 서비스 URL로 변환 (필요시)
        if result.get("status") == "success":
            result["image_url"] = f"/uploads/{image_id}{image_ext}"
        
        return JSONResponse(content=result)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "traceback": error_trace
            }
        )
    
    finally:
        # 임시 파일 정리 (선택사항)
        # if image_path.exists():
        #     image_path.unlink()
        pass


@app.post("/api/v1/process/path")
async def process_image_path(request: ProcessRequest):
    """
    이미지 경로를 받아 처리 (로컬 파일 시스템)
    
    Args:
        request: ProcessRequest 모델
    
    Returns:
        처리 결과 (JSON)
    """
    if not pipeline or not getattr(pipeline, "model_loaded", False):
        return JSONResponse(content={
            "status": "success",
            "message": "모델 미로딩: 경로 처리 스킵 (Mock 처리)",
            "result": {
                "note": "pipeline not loaded"
            }
        })
    
    if not request.image_path or not os.path.exists(request.image_path):
        raise HTTPException(
            status_code=400,
            detail=f"Image file not found: {request.image_path}"
        )
    
    # 출력 디렉토리 설정
    output_dir = request.output_dir or str(OUTPUT_BASE_DIR / "processed")
    os.makedirs(output_dir, exist_ok=True)
    
    # ChatGarment 파이프라인 실행
    try:
        result = pipeline.process_image_to_garment(
            image_path=request.image_path,
            output_dir=output_dir,
            garment_id=request.garment_id or f"garment_{uuid.uuid4().hex[:8]}"
        )
        
        return JSONResponse(content=result)
    
    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )


if __name__ == "__main__":
    # 환경 변수 설정
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    
    print(f"ChatGarment 서비스 시작: http://{host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

