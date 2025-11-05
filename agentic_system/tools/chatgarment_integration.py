"""
ChatGarment 실제 통합 모듈

실제 ChatGarment 모델을 사용하여 이미지를 분석하고
GarmentCodeRC로 3D 옷을 생성하는 완전한 파이프라인
"""

import os
# 강제 UTF-8 환경 (Windows cp949 디코딩 오류 방지)
os.environ.setdefault("PYTHONUTF8", "1")
import sys
import torch
import json
import random
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import builtins as _builtins

# Windows cp949 기본 인코딩으로 인한 디코딩 오류 방지: 텍스트 open 기본값을 UTF-8로 강제
_orig_open = _builtins.open
def _open_utf8(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
    if encoding is None and 'b' not in mode:
        encoding = 'utf-8'
    return _orig_open(file, mode, buffering, encoding, errors, newline, closefd, opener)
_builtins.open = _open_utf8

# 프로젝트 경로 설정
project_root = Path(__file__).parent.parent.parent
chatgarment_path = project_root / "ChatGarment"
garmentcode_path = project_root / "GarmentCodeRC"

sys.path.insert(0, str(chatgarment_path))
sys.path.insert(1, str(garmentcode_path))

# ChatGarment 임포트
# 작업 디렉토리를 ChatGarment로 변경 (상대 경로 문제 영구 해결)
import os
try:
    if chatgarment_path.exists():
        os.chdir(str(chatgarment_path))
        print(f"[ChatGarment Integration] 작업 디렉토리: {os.getcwd()}")
    from llava.constants import (
        IGNORE_INDEX, IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN,
        DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN
    )
    from llava import conversation as conversation_lib
    from llava.model import *
    from llava.mm_utils import tokenizer_image_token
    from llava.garment_utils_v2 import (
        run_garmentcode_parser_float50,
        try_generate_garments
    )
    from llava.json_fixer import repair_json
    # 훈련 의존성(deepspeed 등)로 인한 ImportError 회피를 위해 우선 실제 인자 클래스를 시도
    try:
        from llava.train.train_garmentcode_outfit import (
            ModelArguments, DataArguments, TrainingArguments
        )
    except ImportError as inner_e:
        # deepspeed 등 누락 시 더미 모듈을 주입하고 재시도
        import types, sys as _sys
        missing = str(inner_e)
        if 'deepspeed' in missing and 'deepspeed' not in _sys.modules:
            _sys.modules['deepspeed'] = types.SimpleNamespace(__version__='0.0.0')
        try:
            from llava.train.train_garmentcode_outfit import (
                ModelArguments, DataArguments, TrainingArguments
            )
        except Exception:
            # 최후 수단: 내부 간단 대체 인자 클래스 정의
            from dataclasses import dataclass
            @dataclass
            class ModelArguments:
                model_name_or_path: str
                version: str = "v1"
                vision_tower: str = "openai/clip-vit-large-patch14-336"
                mm_vision_select_layer: int = -2
                mm_vision_select_feature: str = "patch"
                pretrain_mm_mlp_adapter: str = ""
            @dataclass
            class DataArguments:
                image_aspect_ratio: str = "pad"
                image_folder: str = ""
            @dataclass
            class TrainingArguments:
                output_dir: str = "./tmp"
                bf16: bool = True
                fp16: bool = False
                model_max_length: int = 2048
                gradient_checkpointing: bool = True
    import transformers
    CHATGARMENT_AVAILABLE = True
except ImportError as e:
    print(f"ChatGarment 임포트 오류: {e}")
    CHATGARMENT_AVAILABLE = False
except Exception as e:
    print(f"ChatGarment 임포트 오류: {e}")
    CHATGARMENT_AVAILABLE = False


class ChatGarmentPipeline:
    """
    ChatGarment 완전한 파이프라인
    
    실제로 작동하는 ChatGarment → GarmentCodeRC 통합
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        checkpoint_path: Optional[str] = None,
        device: str = "cuda"
    ):
        """
        ChatGarment 파이프라인 초기화
        
        Args:
            model_path: ChatGarment 모델 경로
            checkpoint_path: 체크포인트 파일 경로
            device: 디바이스 ('cuda' or 'cpu')
        """
        self.device = device
        self.model = None
        self.tokenizer = None
        self.image_processor = None
        self.model_loaded = False
        
        # 경로 설정
        if model_path is None:
            model_path = str(project_root / "checkpoints" / "llava-v1.5-7b")
        if checkpoint_path is None:
            checkpoint_path = str(
                project_root / "checkpoints" / 
                "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / 
                "pytorch_model.bin"
            )
        
        self.model_path = model_path
        self.checkpoint_path = checkpoint_path
        
    def load_model(self):
        """ChatGarment 모델 로딩"""
        if self.model_loaded or not CHATGARMENT_AVAILABLE:
            if not CHATGARMENT_AVAILABLE:
                print("[ChatGarment Pipeline] CHATGARMENT_AVAILABLE = False, 모델 로딩 건너뜀")
            return
        
        # 현재 작업 디렉토리는 ChatGarment로 유지됨
        try:
            if chatgarment_path.exists():
                print(f"[ChatGarment Pipeline] 작업 디렉토리: {os.getcwd()}")
        except Exception as e:
            print(f"[ChatGarment Pipeline] 작업 디렉토리 확인 실패: {e}")
        
        try:
            print("=" * 60)
            print("ChatGarment 모델 로딩 시작...")
            print(f"모델 경로: {self.model_path}")
            print(f"체크포인트: {self.checkpoint_path}")
            print("=" * 60)
            
            # 모델 인자 설정
            model_args = ModelArguments(
                model_name_or_path=self.model_path,
                version="v1",
                vision_tower=None  # 기본값 사용
            )
            
            data_args = DataArguments(
                image_aspect_ratio="pad",
                image_folder=str(chatgarment_path / "data")
            )
            
            training_args = TrainingArguments(
                output_dir="./tmp",
                bf16=True,
                fp16=False,
                model_max_length=2048,
                gradient_checkpointing=True
            )
            
            # 토크나이저 로딩
            self.tokenizer = transformers.AutoTokenizer.from_pretrained(
                self.model_path,
                cache_dir=None,
                model_max_length=training_args.model_max_length,
                padding_side="right",
                use_fast=False,
            )
            self.tokenizer.pad_token = self.tokenizer.unk_token
            num_added_tokens = self.tokenizer.add_tokens("[SEG]")
            seg_token_idx = self.tokenizer("[SEG]", add_special_tokens=False).input_ids[-1]
            
            # 모델 생성
            self.model = GarmentGPTFloat50ForCausalLM.from_pretrained(
                self.model_path,
                cache_dir=None,
                torch_dtype=torch.bfloat16,
                seg_token_idx=seg_token_idx,
            )
            
            # Vision 모듈 초기화
            # 필요한 비전 설정 기본값 보강 (누락 필드 대비)
            try:
                defaults = {
                    'vision_tower': 'openai/clip-vit-large-patch14-336',
                    'mm_vision_select_layer': -2,
                    'mm_vision_select_feature': 'patch',
                    'pretrain_mm_mlp_adapter': None,  # 파일이 없으면 None으로 설정 (빈 문자열 대신)
                    'mm_patch_merge_type': 'flat',
                }
                for k, v in defaults.items():
                    if not hasattr(model_args, k):
                        setattr(model_args, k, v)
                
                # 빈 문자열을 None으로 변환 (pretrain_mm_mlp_adapter가 빈 문자열일 경우)
                if hasattr(model_args, 'pretrain_mm_mlp_adapter') and model_args.pretrain_mm_mlp_adapter == '':
                    model_args.pretrain_mm_mlp_adapter = None
            except Exception:
                pass

            # fsdp는 시퀀스형을 기대하므로 빈 리스트 전달
            self.model.get_model().initialize_vision_modules(
                model_args=model_args,
                fsdp=[]
            )
            
            # 체크포인트 로딩
            if os.path.exists(self.checkpoint_path):
                print(f"체크포인트 로딩 중: {self.checkpoint_path}")
                state_dict = torch.load(self.checkpoint_path, map_location="cpu")
                # LoRA 가중치 포함으로 인한 불일치 허용 (strict=False)
                missing_keys, unexpected_keys = self.model.load_state_dict(state_dict, strict=False)
                if missing_keys:
                    print(f"⚠️ 누락된 키 (일부는 정상일 수 있음): {len(missing_keys)}개")
                if unexpected_keys:
                    print(f"⚠️ 예상치 못한 키 (LoRA 가중치 등): {len(unexpected_keys)}개")
                print("체크포인트 로딩 완료")
            else:
                print(f"⚠️ 체크포인트를 찾을 수 없습니다: {self.checkpoint_path}")
                print("⚠️ 사전 훈련된 모델만 사용합니다.")
            
            # 디바이스 설정
            if self.device == "cuda" and torch.cuda.is_available():
                self.model = self.model.bfloat16().cuda().eval()
            else:
                self.model = self.model.bfloat16().eval()
            
            # 이미지 프로세서 설정
            vision_tower = self.model.get_vision_tower()
            vision_tower.to(dtype=torch.bfloat16, device=self.model.device)
            self.image_processor = vision_tower.image_processor
            data_args.image_processor = self.image_processor
            
            # 대화 템플릿 설정
            conversation_lib.default_conversation = conversation_lib.conv_templates["v1"]
            
            self.model_loaded = True
            print("=" * 60)
            print("✅ ChatGarment 모델 로딩 완료!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ ChatGarment 모델 로딩 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            self.model_loaded = False
    
    def process_image_to_garment(
        self,
        image_path: str,
        output_dir: Optional[str] = None,
        garment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        이미지를 처리하여 3D 의류 생성
        
        전체 파이프라인:
        1. 이미지 분석 (Step 1: Geometry features)
        2. 패턴 코드 생성 (Step 2: Sewing pattern code)
        3. GarmentCode 패턴 생성
        4. 3D 변환 (GarmentCodeRC)
        
        Args:
            image_path: 입력 이미지 경로
            output_dir: 출력 디렉토리
            garment_id: 의류 ID (없으면 자동 생성)
            
        Returns:
            Dict: 처리 결과 (JSON, 패턴 경로, 3D 모델 경로 등)
        """
        if not self.model_loaded:
            self.load_model()
        
        if not self.model_loaded:
            raise RuntimeError("ChatGarment 모델을 로딩할 수 없습니다.")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {image_path}")
        
        # 출력 디렉토리 설정
        if output_dir is None:
            output_dir = str(project_root / "outputs" / "garments")
        os.makedirs(output_dir, exist_ok=True)
        
        if garment_id is None:
            garment_id = f"garment_{random.randint(1000, 9999)}"
        
        saved_dir = os.path.join(output_dir, f'valid_garment_{garment_id}')
        os.makedirs(saved_dir, exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"의류 생성 시작: {garment_id}")
        print(f"이미지: {image_path}")
        print(f"출력: {saved_dir}")
        print(f"{'='*60}\n")
        
        try:
            # 이미지 로딩 및 전처리
            print("1️⃣ 이미지 로딩 및 전처리...")
            image = Image.open(image_path).convert('RGB')
            
            # 이미지 패딩 처리
            def expand2square(pil_img, background_color=(122, 116, 104)):
                width, height = pil_img.size
                if width == height:
                    return pil_img
                elif width > height:
                    result = Image.new(pil_img.mode, (width, width), background_color)
                    result.paste(pil_img, (0, (width - height) // 2))
                    return result
                else:
                    result = Image.new(pil_img.mode, (height, height), background_color)
                    result.paste(pil_img, ((height - width) // 2, 0))
                    return result
            
            image = expand2square(image, tuple(int(x*255) for x in self.image_processor.image_mean))
            image_clip = self.image_processor.preprocess(image, return_tensors='pt')['pixel_values'][0]
            image_clip = image_clip.unsqueeze(0).to(self.device)
            image_clip = image_clip.bfloat16()
            
            # Step 1: Geometry features 추출
            print("\n2️⃣ Step 1: Geometry features 분석 중...")
            question1 = 'Can you describe the geometry features of the garments worn by the model in the Json format?'
            
            conv1 = conversation_lib.conv_templates["v1"].copy()
            conv1.messages = []
            prompt1 = DEFAULT_IMAGE_TOKEN + "\n" + question1
            conv1.append_message(conv1.roles[0], prompt1)
            conv1.append_message(conv1.roles[1], None)
            prompt1_full = conv1.get_prompt()
            
            input_ids1 = tokenizer_image_token(prompt1_full, self.tokenizer, return_tensors="pt")
            input_ids1 = input_ids1.unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                output_ids1, _, _ = self.model.evaluate(
                    image_clip,
                    image_clip,
                    input_ids1,
                    max_new_tokens=2048,
                    tokenizer=self.tokenizer,
                )
            
            output_ids1 = output_ids1[0, 1:]
            text_output1 = self.tokenizer.decode(output_ids1, skip_special_tokens=False).strip().replace("</s>", "")
            text_output1 = text_output1.replace('[STARTS]', '').replace('[SEG]', '').replace('[ENDS]', '')
            
            print(f"✅ Geometry features 추출 완료")
            print(f"출력 길이: {len(text_output1)} 문자")
            
            # Step 2: Sewing pattern code 생성
            print("\n3️⃣ Step 2: Sewing pattern code 생성 중...")
            question2 = 'Can you estimate the sewing pattern code based on the image and Json format garment geometry description?'
            
            # text_output1의 upper_garment/lower_garment를 upperbody_garment/lowerbody_garment로 변환
            text_output1_modified = text_output1.replace('upper_garment', 'upperbody_garment').replace('lower_garment', 'lowerbody_garment')
            
            conv2 = conversation_lib.conv_templates["v1"].copy()
            conv2.messages = []
            prompt2 = DEFAULT_IMAGE_TOKEN + "\n" + question2 + "\n" + text_output1_modified
            conv2.append_message(conv2.roles[0], prompt2)
            conv2.append_message(conv2.roles[1], None)
            prompt2_full = conv2.get_prompt()
            
            input_ids2 = tokenizer_image_token(prompt2_full, self.tokenizer, return_tensors="pt")
            input_ids2 = input_ids2.unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                output_ids2, float_preds, seg_token_mask = self.model.evaluate(
                    image_clip,
                    image_clip,
                    input_ids2,
                    max_new_tokens=2048,
                    tokenizer=self.tokenizer,
                )
            
            output_ids2 = output_ids2[0, 1:]
            text_output2 = self.tokenizer.decode(output_ids2, skip_special_tokens=False).strip().replace("</s>", "")
            text_output2 = text_output2.replace('[STARTS]', '').replace('[SEG]', '').replace('[ENDS]', '')
            
            print(f"✅ Sewing pattern code 생성 완료")
            print(f"출력 길이: {len(text_output2)} 문자")
            if float_preds is not None:
                print(f"Float 예측값 개수: {len(float_preds[0]) if len(float_preds.shape) > 1 else len(float_preds)}")
            
            # JSON 수정 및 파싱
            print("\n4️⃣ JSON 파싱 중...")
            json_output = repair_json(text_output2, return_objects=True)
            
            # 결과 저장
            with open(os.path.join(saved_dir, 'output.txt'), 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("Step 1: Geometry Features\n")
                f.write("=" * 60 + "\n")
                f.write(prompt1_full)
                f.write("\n\n")
                f.write(text_output1)
                f.write("\n\n")
                f.write("=" * 60 + "\n")
                f.write("Step 2: Sewing Pattern Code\n")
                f.write("=" * 60 + "\n")
                f.write(prompt2_full)
                f.write("\n\n")
                f.write(text_output2)
                f.write("\n\n")
                f.write("=" * 60 + "\n")
                f.write("Parsed JSON\n")
                f.write("=" * 60 + "\n")
                f.write(json.dumps(json_output, indent=2, ensure_ascii=False))
            
            # 원본 이미지 복사
            import shutil
            shutil.copy(image_path, os.path.join(saved_dir, f'gt_image.png'))
            
            # GarmentCode 패턴 생성
            print("\n5️⃣ GarmentCode 패턴 생성 중...")
            all_json_spec_files = []
            all_json_spec_files = run_garmentcode_parser_float50(
                all_json_spec_files,
                json_output,
                float_preds,
                saved_dir
            )
            
            # 생성된 JSON specification 파일 찾기
            json_spec_files = [
                f for f in os.listdir(saved_dir) 
                if f.endswith('_specification.json')
            ]
            
            if not json_spec_files:
                # 하위 폴더에서 찾기
                for subdir in os.listdir(saved_dir):
                    subdir_path = os.path.join(saved_dir, subdir)
                    if os.path.isdir(subdir_path):
                        json_spec_files = [
                            os.path.join(subdir, f) 
                            for f in os.listdir(subdir_path)
                            if f.endswith('_specification.json')
                        ]
                        if json_spec_files:
                            break
            
            if json_spec_files:
                json_spec_path = os.path.join(saved_dir, json_spec_files[0])
                print(f"✅ 패턴 생성 완료: {json_spec_path}")
                
                # 3D 변환 (GarmentCodeRC)
                print("\n6️⃣ 3D 변환 시작 (GarmentCodeRC)...")
                mesh_path = self._convert_to_3d(json_spec_path, saved_dir)
                
                return {
                    "status": "success",
                    "garment_id": garment_id,
                    "output_dir": saved_dir,
                    "geometry_features": text_output1,
                    "pattern_code": text_output2,
                    "json_output": json_output,
                    "float_preds": float_preds.cpu().numpy().tolist() if float_preds is not None else None,
                    "json_spec_path": json_spec_path,
                    "mesh_path": mesh_path,
                    "message": "의류 생성이 성공적으로 완료되었습니다!"
                }
            else:
                raise FileNotFoundError("패턴 specification JSON 파일을 생성할 수 없었습니다.")
                
        except Exception as e:
            import traceback
            error_msg = f"의류 생성 중 오류 발생: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            
            return {
                "status": "error",
                "garment_id": garment_id,
                "output_dir": saved_dir,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "message": error_msg
            }
    
    def _convert_to_3d(
        self,
        json_spec_path: str,
        output_dir: str
    ) -> Optional[str]:
        """
        GarmentCodeRC를 사용하여 3D 변환
        
        Args:
            json_spec_path: 패턴 specification JSON 파일 경로
            output_dir: 출력 디렉토리
            
        Returns:
            3D 메시 파일 경로
        """
        try:
            import subprocess
            
            # GarmentCodeRC의 run_garmentcode_sim.py 실행
            sim_script = chatgarment_path / "run_garmentcode_sim.py"
            
            if not sim_script.exists():
                print(f"⚠️ 시뮬레이션 스크립트를 찾을 수 없습니다: {sim_script}")
                return None
            
            # 경로를 절대 경로로 변환
            json_spec_path_abs = os.path.abspath(json_spec_path)
            
            # GarmentCodeRC의 assets 경로 확인
            sim_props_path = garmentcode_path / "assets" / "Sim_props" / "default_sim_props.yaml"
            
            if not sim_props_path.exists():
                print(f"⚠️ 시뮬레이션 설정 파일을 찾을 수 없습니다: {sim_props_path}")
                print("기본 설정으로 진행합니다...")
                sim_props_path = None
            
            # 명령어 구성
            cmd = [
                sys.executable,
                str(sim_script),
                "--json_spec_file", json_spec_path_abs
            ]
            
            if sim_props_path:
                cmd.extend(["--sim_config", str(sim_props_path)])
            
            print(f"실행 명령어: {' '.join(cmd)}")
            print(f"작업 디렉토리: {str(project_root)}")
            
            # 서브프로세스 실행
            result = subprocess.run(
                cmd,
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=600  # 10분 타임아웃
            )
            
            if result.returncode == 0:
                print("✅ 3D 변환 완료!")
                print(result.stdout)
                
                # 생성된 메시 파일 찾기
                spec_dir = os.path.dirname(json_spec_path)
                mesh_files = [
                    f for f in os.listdir(spec_dir)
                    if f.endswith('.obj') and 'sim' in f
                ]
                
                if mesh_files:
                    mesh_path = os.path.join(spec_dir, mesh_files[0])
                    print(f"✅ 3D 메시 생성 완료: {mesh_path}")
                    return mesh_path
                else:
                    print("⚠️ .obj 파일을 찾을 수 없습니다.")
                    return None
            else:
                print(f"❌ 3D 변환 실패 (종료 코드: {result.returncode})")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ 3D 변환 타임아웃 (10분 초과)")
            return None
        except Exception as e:
            print(f"❌ 3D 변환 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


# 테스트 함수
def test_chatgarment_pipeline(image_path: str):
    """
    ChatGarment 파이프라인 테스트
    
    Args:
        image_path: 테스트할 이미지 경로
    """
    print("\n" + "="*60)
    print("ChatGarment 파이프라인 테스트 시작")
    print("="*60 + "\n")
    
    pipeline = ChatGarmentPipeline()
    
    result = pipeline.process_image_to_garment(
        image_path=image_path,
        garment_id="test_001"
    )
    
    print("\n" + "="*60)
    print("테스트 결과")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result


if __name__ == "__main__":
    # 테스트 실행
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, required=True, help="입력 이미지 경로")
    parser.add_argument("--output", type=str, default=None, help="출력 디렉토리")
    args = parser.parse_args()
    
    test_chatgarment_pipeline(args.image)

