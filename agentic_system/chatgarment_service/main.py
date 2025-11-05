#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGarment 마이크로서비스
리눅스 환경에서 독립적으로 실행
"""

import sys
import os
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn

# ChatGarment 경로 추가 (자동 감지)
# Windows 또는 Linux 경로 자동 감지
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent  # agentic_system/chatgarment_service -> agentic_system -> ChatGarment

# 가능한 경로들 시도
possible_paths = [
    project_root / "ChatGarment",
    project_root.parent / "ChatGarment",
    Path.home() / "ChatGarment",  # 홈 디렉토리 기준
]

chatgarment_root = None
for path in possible_paths:
    if path.exists():
        chatgarment_root = path
        print(f"[ChatGarment Service] ChatGarment 경로 발견: {chatgarment_root}")
        sys.path.insert(0, str(chatgarment_root))
        # 작업 디렉토리를 ChatGarment로 변경 (상대 경로 문제 해결)
        os.chdir(str(chatgarment_root))
        print(f"[ChatGarment Service] 작업 디렉토리 변경: {os.getcwd()}")
        break

if chatgarment_root is None:
    print("[ChatGarment Service] 경고: ChatGarment 경로를 찾을 수 없습니다. Mock 모드로 동작합니다.")

app = FastAPI(
    title="ChatGarment Service API",
    description="ChatGarment 마이크로서비스 - 2D to 3D 변환",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ChatGarment Pipeline 인스턴스
chatgarment_pipeline = None

def load_chatgarment_pipeline():
    """ChatGarment Pipeline 로딩 (실패 시 Mock 모드)"""
    global chatgarment_pipeline
    
    if chatgarment_pipeline is not None:
        return chatgarment_pipeline
    
    # ChatGarment 경로가 없으면 Mock 모드
    if chatgarment_root is None:
        print("[ChatGarment Service] Mock 모드로 동작합니다 (경로 없음)")
        chatgarment_pipeline = "mock"
        return chatgarment_pipeline
    
    try:
        # 실제 Pipeline 로딩 시도
        # 체크포인트 경로: 프로젝트 루트 기준으로 찾기
        # 가능한 경로들 시도
        possible_checkpoint_paths = [
            project_root / "checkpoints" / "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / "pytorch_model.bin",
            project_root.parent / "checkpoints" / "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / "pytorch_model.bin",
        ]
        if chatgarment_root:
            possible_checkpoint_paths.append(
                chatgarment_root / "checkpoints" / "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / "pytorch_model.bin"
            )
        
        checkpoint_path = None
        for cp_path in possible_checkpoint_paths:
            if cp_path.exists():
                checkpoint_path = cp_path
                print(f"[ChatGarment Service] 체크포인트 발견: {checkpoint_path}")
                break
        
        if checkpoint_path is None:
            print(f"[ChatGarment Service] 체크포인트를 찾을 수 없습니다.")
            print(f"    시도한 경로들:")
            for cp_path in possible_checkpoint_paths:
                print(f"      - {cp_path} (존재: {cp_path.exists()})")
            print("[ChatGarment Service] Mock 모드로 동작합니다")
            chatgarment_pipeline = "mock"
            return chatgarment_pipeline
        
        # 임포트 경로 수정
        sys.path.insert(0, str(project_root / "agentic_system"))
        from agentic_system.tools.chatgarment_integration import ChatGarmentPipeline
        
        # CUDA 사용 가능 여부 확인
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"
        except Exception as e:
            print(f"경고: torch 임포트 실패: {e}")
            device = "cpu"
        
        pipeline = ChatGarmentPipeline(
            checkpoint_path=str(checkpoint_path),
            device=device
        )
        
        chatgarment_pipeline = pipeline
        print("✅ ChatGarment Pipeline 로딩 완료")
        return pipeline
        
    except Exception as e:
        print(f"❌ ChatGarment Pipeline 로딩 실패: {str(e)}")
        print("[ChatGarment Service] Mock 모드로 전환합니다")
        import traceback
        traceback.print_exc()
        chatgarment_pipeline = "mock"
        return chatgarment_pipeline

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "chatgarment"}

@app.post("/api/v1/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    text: Optional[str] = Form(None)
):
    """
    이미지 분석
    
    Args:
        image: 업로드된 이미지 파일
        text: 선택적 텍스트 설명
        
    Returns:
        분석 결과 (JSON)
    """
    try:
        # ChatGarment 경로 확인
        if chatgarment_root is None:
            raise HTTPException(
                status_code=500, 
                detail="ChatGarment 경로를 찾을 수 없습니다. Mock 모드를 사용하세요."
            )
        
        # 이미지 저장
        upload_dir = chatgarment_root / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 파일명 처리
        if image.filename is None:
            image.filename = f"{uuid.uuid4()}.jpg"
        image_path = upload_dir / image.filename
        with open(image_path, "wb") as f:
            content = await image.read()
            f.write(content)
        
        # Pipeline 로딩
        pipeline = load_chatgarment_pipeline()
        
        # Mock 모드 처리
        if pipeline == "mock":
            return JSONResponse(content={
                "status": "success",
                "analysis": {
                    "garment_type": "상의",
                    "style": "캐주얼",
                    "color": "검정색",
                    "type": "hoodie"
                },
                "message": "이미지 분석이 완료되었습니다. (Mock 모드)"
            })
        
        # 실제 Pipeline 사용
        result = pipeline.analyze_image(str(image_path), text)
        
        return JSONResponse(content={
            "status": "success",
            "analysis": result,
            "message": "이미지 분석이 완료되었습니다."
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/process")
async def process_image(
    image: UploadFile = File(...),
    text: Optional[str] = Form(None),
    output_dir: Optional[str] = Form(None)
):
    """
    전체 파이프라인 실행 (이미지 분석 + 3D 생성)
    
    Args:
        image: 업로드된 이미지 파일
        text: 선택적 텍스트 설명
        output_dir: 출력 디렉토리 (선택사항)
        
    Returns:
        전체 처리 결과
    """
    try:
        # ChatGarment 경로 확인
        if chatgarment_root is None:
            raise HTTPException(
                status_code=500, 
                detail="ChatGarment 경로를 찾을 수 없습니다. Mock 모드를 사용하세요."
            )
        
        # 이미지 저장
        upload_dir = chatgarment_root / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 파일명 처리
        if image.filename is None:
            import uuid
            image.filename = f"{uuid.uuid4()}.jpg"
        image_path = upload_dir / image.filename
        with open(image_path, "wb") as f:
            content = await image.read()
            f.write(content)
        
        # 출력 디렉토리 설정
        if output_dir is None:
            output_dir = chatgarment_root / "outputs" / "chatgarment"
        else:
            output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Pipeline 로딩
        pipeline = load_chatgarment_pipeline()
        
        # Mock 모드 처리
        if pipeline == "mock":
            # Mock 결과 생성 (기존 extensions.py의 Mock 로직과 유사)
            return JSONResponse(content={
                "status": "success",
                "result": {
                    "status": "success",
                    "analysis": {
                        "garment_type": "상의",
                        "style": "캐주얼",
                        "color": "검정색",
                        "type": "hoodie"
                    },
                    "pattern_path": str(output_dir / "pattern.json"),
                    "mesh_path": str(output_dir / "garment.obj"),
                    "render_path": str(output_dir / "garment_render.png"),
                    "message": "전체 파이프라인이 완료되었습니다. (Mock 모드)"
                },
                "message": "처리가 완료되었습니다. (Mock 모드)"
            })
        
        # 실제 Pipeline 사용
        result = pipeline.process_image(
            str(image_path),
            output_dir=str(output_dir),
            text_description=text
        )
        
        return JSONResponse(content={
            "status": "success",
            "result": result,
            "message": "처리가 완료되었습니다."
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 Pipeline 로드 시도"""
    print("=" * 60)
    print("[ChatGarment Service] 서비스 시작 이벤트")
    print("=" * 60)
    
    # Pipeline 로딩 시도
    print("[ChatGarment Service] Pipeline 로딩 시도...")
    pipeline = load_chatgarment_pipeline()
    
    if pipeline == "mock":
        print("[ChatGarment Service] ⚠️ Mock 모드로 동작합니다")
        print("[ChatGarment Service] 실제 모델을 사용하려면:")
        print("[ChatGarment Service] 1. 체크포인트 경로 확인")
        print("[ChatGarment Service] 2. 모든 의존성 설치 확인")
        print("[ChatGarment Service] 3. 서비스 로그 확인")
    else:
        print("[ChatGarment Service] ✅ 실제 ChatGarment Pipeline이 로드되었습니다!")
    
    print("=" * 60)
    print()

if __name__ == "__main__":
    # ChatGarment 경로 확인
    if chatgarment_root:
        print(f"[ChatGarment Service] ChatGarment 경로: {chatgarment_root}")
        print(f"[ChatGarment Service] 경로 존재 여부: {chatgarment_root.exists()}")
        print(f"[ChatGarment Service] 작업 디렉토리: {os.getcwd()}")
    else:
        print("[ChatGarment Service] ChatGarment 경로를 찾을 수 없습니다. Mock 모드로 동작합니다.")
    
    print("[ChatGarment Service] 서비스 시작: http://0.0.0.0:9000")
    print("[ChatGarment Service] 헬스 체크: http://localhost:9000/health")
    print()
    print("[ChatGarment Service] 서비스가 시작되면 Pipeline 로딩을 시도합니다...")
    print("=" * 60)
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        log_level="info"
    )

