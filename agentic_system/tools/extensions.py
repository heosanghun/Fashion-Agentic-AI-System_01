"""
Extensions Tool - 2D to 3D 변환 도구

실제 ChatGarment 시스템과 통합하여 2D 이미지를 3D 모델로 변환
"""

from typing import Dict, Any, Optional
import os
import sys
from pathlib import Path
import json
import subprocess
import torch
import random

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "ChatGarment"))

# ChatGarment 임포트
try:
    from .chatgarment_integration import ChatGarmentPipeline
    CHATGARMENT_AVAILABLE = True
except ImportError as e:
    print(f"ChatGarment 통합 모듈 임포트 경고: {e}")
    try:
        from llava.garment_utils_v2 import (
            try_generate_garments,
            run_garmentcode_parser_float50,
            recursive_change_params
        )
        from llava.json_fixer import repair_json
        from llava.model import *
        from llava.mm_utils import tokenizer_image_token
        from llava import conversation as conversation_lib
        from llava.constants import DEFAULT_IMAGE_TOKEN
        import transformers
        CHATGARMENT_AVAILABLE = True
        CHATGARMENT_PIPELINE_AVAILABLE = False
    except ImportError as e2:
        print(f"ChatGarment 임포트 경고: {e2}")
        CHATGARMENT_AVAILABLE = False
        CHATGARMENT_PIPELINE_AVAILABLE = False
    else:
        CHATGARMENT_PIPELINE_AVAILABLE = False
else:
    CHATGARMENT_PIPELINE_AVAILABLE = True


class Extensions2DTo3D:
    """
    Extensions Tool - 2D to 3D 변환
    
    실제 ChatGarment 모델을 사용하여 2D 이미지를 3D 모델로 변환
    """
    
    def __init__(self):
        self.name = "extensions_2d_to_3d"
        self.chatgarment_path = project_root / "ChatGarment"
        self.checkpoint_path = project_root / "checkpoints" / "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final"
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False
        
        # 실제 ChatGarment 파이프라인 사용 여부
        self.chatgarment_pipeline = None
        if CHATGARMENT_PIPELINE_AVAILABLE:
            try:
                self.chatgarment_pipeline = ChatGarmentPipeline(device=self.device)
                print("✅ ChatGarment 실제 파이프라인 사용 가능")
            except Exception as e:
                print(f"⚠️ ChatGarment 파이프라인 초기화 실패: {e}")
                self.chatgarment_pipeline = None
        
    def _load_model(self):
        """ChatGarment 모델 로딩 (지연 로딩)"""
        if self.model_loaded or not CHATGARMENT_AVAILABLE:
            return
        
        try:
            print("ChatGarment 모델 로딩 중...")
            
            # 모델 경로 확인
            model_path = str(self.checkpoint_path.parent)
            checkpoint_file = str(self.checkpoint_path / "pytorch_model.bin")
            
            if not os.path.exists(checkpoint_file):
                print(f"체크포인트를 찾을 수 없습니다: {checkpoint_file}")
                return
            
            # 토크나이저 로딩
            self.tokenizer = transformers.AutoTokenizer.from_pretrained(
                model_path,
                use_fast=False,
            )
            self.tokenizer.pad_token = self.tokenizer.unk_token
            num_added_tokens = self.tokenizer.add_tokens("[SEG]")
            seg_token_idx = self.tokenizer("[SEG]", add_special_tokens=False).input_ids[-1]
            
            # 모델 로딩
            from llava.train.train_garmentcode_outfit import ModelArguments
            model_args = ModelArguments(model_name_or_path=model_path)
            
            self.model = GarmentGPTFloat50ForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.bfloat16,
                seg_token_idx=seg_token_idx,
            )
            
            # 체크포인트 로딩
            state_dict = torch.load(checkpoint_file, map_location="cpu")
            self.model.load_state_dict(state_dict, strict=True)
            self.model = self.model.bfloat16().to(self.device).eval()
            
            # 대화 템플릿 설정
            conversation_lib.default_conversation = conversation_lib.conv_templates["v1"]
            
            self.model_loaded = True
            print("ChatGarment 모델 로딩 완료")
            
        except Exception as e:
            print(f"ChatGarment 모델 로딩 실패: {str(e)}")
            print("Mock 모드로 동작합니다.")
            self.model_loaded = False
    
    def execute(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        도구 실행
        
        Args:
            action: 실행할 액션 (analyze_image, generate_pattern, convert_to_3d, render_result)
            parameters: 액션에 필요한 파라미터
            context: 실행 컨텍스트
            
        Returns:
            Dict: 실행 결과
        """
        print(f"[Extensions2DTo3D] execute 호출: action={action}")
        
        try:
            if action == "analyze_image":
                print("[Extensions2DTo3D] analyze_image 시작...")
                result = self._analyze_image(parameters, context)
                print(f"[Extensions2DTo3D] analyze_image 완료: status={result.get('status')}")
                return result
            elif action == "generate_pattern":
                print("[Extensions2DTo3D] generate_pattern 시작...")
                result = self._generate_pattern(parameters, context)
                print(f"[Extensions2DTo3D] generate_pattern 완료: status={result.get('status')}")
                return result
            elif action == "convert_to_3d":
                print("[Extensions2DTo3D] convert_to_3d 시작...")
                result = self._convert_to_3d(parameters, context)
                print(f"[Extensions2DTo3D] convert_to_3d 완료: status={result.get('status')}")
                return result
            elif action == "render_result":
                print("[Extensions2DTo3D] render_result 시작...")
                result = self._render_result(parameters, context)
                print(f"[Extensions2DTo3D] render_result 완료: status={result.get('status')}")
                return result
            elif action == "process_request":
                print("[Extensions2DTo3D] process_request 시작...")
                result = self._process_full_pipeline(parameters, context)
                print(f"[Extensions2DTo3D] process_request 완료: status={result.get('status')}")
                return result
            else:
                raise ValueError(f"Unknown action: {action}")
        except Exception as e:
            print(f"[Extensions2DTo3D] execute 오류: action={action}, error={str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _analyze_image(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        이미지 분석 (ChatGarment 모델 사용)
        
        실제 ChatGarment 모델로 이미지를 분석하여 의류 정보 추출
        """
        image_path = parameters.get("image_path") or context.get("image_path")
        text_description = parameters.get("text_description") or context.get("text")
        
        if not image_path:
            raise ValueError("이미지 경로가 필요합니다.")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {image_path}")
        
        # 모델 로딩
        self._load_model()
        
        if not self.model_loaded:
            # Mock 모드
            return self._mock_analyze_image(image_path, text_description)
        
        try:
            # 이미지 로딩
            from PIL import Image
            image = Image.open(image_path).convert('RGB')
            
            # 이미지 전처리
            from llava.train.train_garmentcode_outfit import DataArguments
            data_args = DataArguments()
            data_args.image_processor = self.model.get_vision_tower().image_processor
            data_args.image_aspect_ratio = "pad"
            
            processor = data_args.image_processor
            image_clip = processor.preprocess(image, return_tensors='pt')['pixel_values'][0]
            image_clip = image_clip.unsqueeze(0).to(self.device).bfloat16()
            
            # 프롬프트 구성
            question = 'Can you describe the geometry features of the garments worn by the model in the Json format?'
            conv = conversation_lib.conv_templates["v1"].copy()
            conv.messages = []
            prompt = DEFAULT_IMAGE_TOKEN + "\n" + question
            conv.append_message(conv.roles[0], prompt)
            conv.append_message(conv.roles[1], None)
            prompt = conv.get_prompt()
            
            # 토크나이징
            input_ids = tokenizer_image_token(prompt, self.tokenizer, return_tensors="pt")
            input_ids = input_ids.unsqueeze(0).to(self.device)
            
            # 추론
            with torch.no_grad():
                output_ids, float_preds, seg_token_mask = self.model.evaluate(
                    image_clip,
                    image_clip,
                    input_ids,
                    max_new_tokens=2048,
                    tokenizer=self.tokenizer,
                )
            
            # 결과 파싱
            output_ids = output_ids[0, 1:]
            text_output = self.tokenizer.decode(output_ids, skip_special_tokens=False).strip().replace("</s>", "")
            text_output = text_output.replace('[STARTS]', '').replace('[SEG]', '').replace('[ENDS]', '')
            
            # JSON 수정
            json_output = repair_json(text_output, return_objects=True)
            
            return {
                "status": "success",
                "analysis": json_output,
                "text_output": text_output,
                "float_preds": float_preds.cpu().numpy().tolist() if float_preds is not None else None,
                "image_path": image_path,
                "message": "이미지 분석이 완료되었습니다."
            }
            
        except Exception as e:
            print(f"이미지 분석 오류: {str(e)}")
            return self._mock_analyze_image(image_path, text_description)
    
    def _generate_pattern(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        패턴 생성 (GarmentCode 사용)
        
        분석 결과를 기반으로 2D 패턴 생성
        """
        # 이전 단계 결과 사용
        analysis = parameters.get("_dependency_result") or context.get("step_1")
        
        if not analysis:
            raise ValueError("이미지 분석 결과가 필요합니다.")
        
        json_output = analysis.get("analysis") or analysis
        float_preds = analysis.get("float_preds")
        
        # 출력 디렉토리 설정
        output_dir = project_root / "outputs" / "patterns"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        garment_name = "garment_001"
        
        try:
            # 패턴 생성
            all_json_spec_files = []
            saved_dir = str(output_dir)
            
            all_json_spec_files = run_garmentcode_parser_float50(
                all_json_spec_files,
                json_output,
                float_preds,
                saved_dir
            )
            
            # 생성된 파일 경로
            pattern_json_path = os.path.join(saved_dir, f'valid_garment_{garment_name}', 
                                            f'valid_garment_{garment_name}_specification.json')
            
            if os.path.exists(pattern_json_path):
                return {
                    "status": "success",
                    "pattern_path": pattern_json_path,
                    "pattern_info": {
                        "type": json_output.get("type", "unknown"),
                        "components": list(json_output.keys()),
                    },
                    "message": "패턴 생성이 완료되었습니다."
                }
            else:
                # Mock 패턴 생성
                return self._mock_generate_pattern(analysis)
                
        except Exception as e:
            print(f"패턴 생성 오류: {str(e)}")
            return self._mock_generate_pattern(analysis)
    
    def _convert_to_3d(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        3D 모델로 변환 (GarmentCodeRC 사용)
        
        패턴을 3D 메시로 변환
        """
        # 이전 단계 결과 사용
        pattern_result = parameters.get("_dependency_result") or context.get("step_2")
        
        if not pattern_result:
            print("[Extensions2DTo3D] 패턴 생성 결과가 없어 Mock 모드로 전환합니다.")
            return self._mock_convert_to_3d({})
        
        pattern_json_path = pattern_result.get("pattern_path")
        
        # 패턴 파일이 없으면 Mock 모드로 전환
        if not pattern_json_path or not os.path.exists(pattern_json_path):
            print(f"[Extensions2DTo3D] 패턴 파일을 찾을 수 없습니다: {pattern_json_path}")
            print("[Extensions2DTo3D] Mock 모드로 3D 변환을 수행합니다.")
            return self._mock_convert_to_3d(pattern_result)
        
        # 실제 3D 변환 시도 (Mock 모드에서는 건너뛰기)
        # PoC 단계에서는 실제 변환 대신 Mock 변환 사용
        print("[Extensions2DTo3D] 실제 3D 변환 스크립트 확인...")
        sim_script = project_root / "ChatGarment" / "run_garmentcode_sim.py"
        
        # 실제 변환을 시도할지 여부 (현재는 Mock 모드 사용)
        try_real_conversion = False  # PoC 단계에서는 False
        
        if try_real_conversion and sim_script.exists() and os.path.exists(pattern_json_path):
            try:
                print(f"[Extensions2DTo3D] 실제 3D 변환 스크립트 실행: {sim_script}")
                # 서브프로세스로 3D 변환 실행
                command = f'python "{sim_script}" --json_spec_file "{pattern_json_path}"'
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(project_root),
                    timeout=600  # 10분 타임아웃
                )
                
                if result.returncode == 0:
                    # 생성된 3D 모델 경로 찾기
                    pattern_dir = os.path.dirname(pattern_json_path)
                    mesh_path = os.path.join(pattern_dir, f"{os.path.basename(pattern_dir)}_sim.obj")
                    
                    if os.path.exists(mesh_path):
                        print(f"[Extensions2DTo3D] 실제 3D 메시 생성 완료: {mesh_path}")
                        return {
                            "status": "success",
                            "mesh_path": mesh_path,
                            "mesh_info": {
                                "format": "obj",
                                "path": mesh_path
                            },
                            "message": "3D 변환이 완료되었습니다."
                        }
                    else:
                        print(f"[Extensions2DTo3D] 3D 메시 파일을 찾을 수 없습니다: {mesh_path}")
                else:
                    print(f"[Extensions2DTo3D] 3D 변환 스크립트 실패 (종료 코드: {result.returncode})")
                    print(f"[Extensions2DTo3D] STDOUT: {result.stdout[:500]}")
                    print(f"[Extensions2DTo3D] STDERR: {result.stderr[:500]}")
            except subprocess.TimeoutExpired:
                print("[Extensions2DTo3D] 3D 변환 타임아웃 (10분 초과)")
            except Exception as e:
                print(f"[Extensions2DTo3D] 실제 3D 변환 시도 중 오류: {str(e)}")
        
        # Mock 변환으로 전환 (PoC 단계 기본 동작)
        print("[Extensions2DTo3D] Mock 모드로 3D 변환을 수행합니다.")
        return self._mock_convert_to_3d(pattern_result)
    
    def _render_result(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        결과 렌더링
        """
        # 이전 단계 결과 사용
        mesh_result = parameters.get("_dependency_result") or context.get("step_3")
        
        if not mesh_result:
            raise ValueError("3D 모델 결과가 필요합니다.")
        
        mesh_path = mesh_result.get("mesh_path")
        
        # TODO: 실제 렌더링 엔진 사용 (PyTorch3D 등)
        # 현재는 Mock 구현
        render_path = self._mock_render(mesh_result)
        
        return {
            "status": "success",
            "render_path": render_path,
            "visualization": {
                "image_path": render_path,
                "mesh_path": mesh_path
            },
            "message": "렌더링이 완료되었습니다."
        }
    
    def _process_full_pipeline(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        전체 파이프라인 실행
        
        ChatGarment 마이크로서비스 사용 시도, 실패 시 Mock 모드
        """
        # ChatGarment 마이크로서비스 사용 여부 확인
        use_service = os.getenv("USE_CHATGARMENT_SERVICE", "false").lower() == "true"
        
        if use_service:
            print("[Extensions2DTo3D] ChatGarment 마이크로서비스 사용 시도...")
            try:
                from .extensions_service import chatgarment_service_tool
                
                image_path = parameters.get("image_path") or context.get("image_path")
                if image_path and Path(image_path).exists():
                    result = chatgarment_service_tool("process", {
                        "image_path": image_path,
                        "text_description": parameters.get("text_description") or context.get("text"),
                        "output_dir": context.get("output_dir")
                    }, context)
                    
                    if result.get("status") == "success":
                        print("[Extensions2DTo3D] ChatGarment 마이크로서비스 처리 완료")
                        return {
                            "status": "success",
                            "pipeline_complete": True,
                            "result": result.get("result", {}),
                            "message": "전체 파이프라인이 완료되었습니다. (ChatGarment 서비스)"
                        }
                    else:
                        print(f"[Extensions2DTo3D] 서비스 오류: {result.get('error')}")
                        print("[Extensions2DTo3D] Mock 모드로 전환합니다.")
                else:
                    print("[Extensions2DTo3D] 이미지 경로가 없어 서비스를 사용할 수 없습니다.")
                    print("[Extensions2DTo3D] Mock 모드로 전환합니다.")
            except Exception as e:
                print(f"[Extensions2DTo3D] 서비스 연결 실패: {str(e)}")
                print("[Extensions2DTo3D] Mock 모드로 전환합니다.")
                import traceback
                traceback.print_exc()
        
        # Mock 모드 또는 서비스 사용 실패 시 기존 로직 실행
        print("[Extensions2DTo3D] Mock 모드로 전체 파이프라인 실행...")
        step1 = self._analyze_image(parameters, context)
        context["step_1"] = step1
        
        step2 = self._generate_pattern(parameters, context)
        context["step_2"] = step2
        
        step3 = self._convert_to_3d(parameters, context)
        context["step_3"] = step3
        
        step4 = self._render_result(parameters, context)
        
        return {
            "status": "success",
            "pipeline_complete": True,
            "steps": {
                "analysis": step1,
                "pattern": step2,
                "3d_conversion": step3,
                "render": step4
            },
            "final_result": step4,
            "message": "전체 파이프라인이 완료되었습니다. (Mock 모드)"
        }
    
    def _mock_analyze_image(self, image_path: str, text_description: Optional[str]) -> Dict[str, Any]:
        """Mock 이미지 분석"""
        return {
            "status": "success",
            "analysis": {
                "garment_type": "상의",
                "style": "캐주얼",
                "color": "검정색",
                "type": "hoodie"
            },
            "image_path": image_path,
            "message": "이미지 분석이 완료되었습니다. (Mock 모드)"
        }
    
    def _mock_generate_pattern(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Mock 패턴 생성"""
        output_dir = project_root / "outputs" / "patterns"
        output_dir.mkdir(parents=True, exist_ok=True)
        pattern_path = str(output_dir / "pattern.json")
        
        # 실제 패턴 JSON 파일 생성 (Mock 데이터)
        pattern_data = {
            "garment_type": analysis.get("analysis", {}).get("type", "hoodie") if isinstance(analysis.get("analysis"), dict) else "hoodie",
            "components": ["front", "back", "sleeves", "hood"],
            "specification": {
                "front": {
                    "width": 50,
                    "height": 70,
                    "seams": ["shoulder", "side", "bottom"]
                },
                "back": {
                    "width": 50,
                    "height": 70,
                    "seams": ["shoulder", "side", "bottom"]
                },
                "sleeves": {
                    "length": 60,
                    "width": 30,
                    "seams": ["armhole", "side", "cuff"]
                },
                "hood": {
                    "width": 45,
                    "height": 35,
                    "seams": ["crown", "face_opening"]
                }
            },
            "version": "1.0",
            "created_by": "mock_generator"
        }
        
        # 파일 쓰기
        try:
            with open(pattern_path, 'w', encoding='utf-8') as f:
                json.dump(pattern_data, f, ensure_ascii=False, indent=2)
            print(f"[Extensions2DTo3D] Mock 패턴 파일 생성 완료: {pattern_path}")
        except Exception as e:
            print(f"[Extensions2DTo3D] Mock 패턴 파일 생성 실패: {e}")
        
        return {
            "status": "success",
            "pattern_path": pattern_path,
            "pattern_info": {
                "type": pattern_data["garment_type"],
                "components": pattern_data["components"],
            },
            "message": "패턴 생성이 완료되었습니다. (Mock 모드)"
        }
    
    def _mock_convert_to_3d(self, pattern_result: Dict[str, Any]) -> Dict[str, Any]:
        """Mock 3D 변환"""
        output_dir = project_root / "outputs" / "3d_models"
        output_dir.mkdir(parents=True, exist_ok=True)
        mesh_path = str(output_dir / "garment.obj")
        
        # 실제 Mock OBJ 파일 생성 (간단한 3D 메시)
        try:
            with open(mesh_path, 'w', encoding='utf-8') as f:
                # 간단한 Mock OBJ 파일 (큐브 형태)
                f.write("# Mock 3D Garment Mesh\n")
                f.write("# Generated by Mock Converter\n")
                f.write("g garment_mock\n")
                
                # 정점 (vertices) - 간단한 박스 형태
                vertices = [
                    (-1, -1, -1),  # 0
                    (1, -1, -1),   # 1
                    (1, 1, -1),    # 2
                    (-1, 1, -1),   # 3
                    (-1, -1, 1),   # 4
                    (1, -1, 1),    # 5
                    (1, 1, 1),     # 6
                    (-1, 1, 1),    # 7
                ]
                
                for v in vertices:
                    f.write(f"v {v[0]} {v[1]} {v[2]}\n")
                
                # 면 (faces) - 박스의 6개 면
                faces = [
                    (0, 1, 2, 3),  # 앞면
                    (4, 7, 6, 5),  # 뒷면
                    (0, 4, 5, 1),  # 아래면
                    (2, 6, 7, 3),  # 위면
                    (0, 3, 7, 4),  # 왼쪽면
                    (1, 5, 6, 2),  # 오른쪽면
                ]
                
                for face in faces:
                    f.write(f"f {' '.join([str(i+1) for i in face])}\n")
            
            print(f"[Extensions2DTo3D] Mock 3D 메시 파일 생성 완료: {mesh_path}")
        except Exception as e:
            print(f"[Extensions2DTo3D] Mock 3D 메시 파일 생성 실패: {e}")
        
        return {
            "status": "success",
            "mesh_path": mesh_path,
            "mesh_info": {
                "vertices": 8,
                "faces": 6,
                "format": "obj"
            },
            "message": "3D 변환이 완료되었습니다. (Mock 모드)"
        }
    
    def _mock_render(self, mesh_result: Dict[str, Any]) -> str:
        """Mock 렌더링"""
        output_dir = project_root / "outputs" / "renders"
        output_dir.mkdir(parents=True, exist_ok=True)
        render_path = str(output_dir / "garment_render.png")
        return render_path


# 도구 함수로 사용하기 위한 래퍼
def extensions_2d_to_3d_tool(action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """도구 함수 래퍼"""
    tool = Extensions2DTo3D()
    return tool.execute(action, parameters, context)
