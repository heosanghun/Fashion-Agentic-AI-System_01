"""
InternVL2-8B Model Wrapper
InternVL2-8B 모델을 Agentic AI 시스템에 통합하기 위한 래퍼
"""

import torch
import torchvision.transforms as T
from PIL import Image
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import sys

# transformers 임포트
try:
    from transformers import AutoModel, AutoTokenizer
except ImportError:
    raise ImportError("transformers 라이브러리가 필요합니다: pip install transformers")


class InternVL2Wrapper:
    """
    InternVL2-8B 모델 래퍼
    
    멀티모달 VLM (Vision-Language Model)로 텍스트와 이미지를 동시에 처리
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "cuda",
        torch_dtype: torch.dtype = torch.bfloat16,
        load_in_8bit: bool = False,
        use_flash_attn: bool = True
    ):
        """
        InternVL2 모델 초기화
        
        Args:
            model_path: 모델 경로 (기본값: 프로젝트의 model/InternVL2_8B)
            device: 디바이스 ('cuda' or 'cpu')
            torch_dtype: 데이터 타입 (torch.bfloat16 권장)
            load_in_8bit: 8-bit 양자화 사용 여부
            use_flash_attn: Flash Attention 사용 여부
        """
        self.device = device
        self.torch_dtype = torch_dtype
        self.load_in_8bit = load_in_8bit
        self.use_flash_attn = use_flash_attn
        
        # 모델 경로 설정
        if model_path is None:
            project_root = Path(__file__).parent.parent.parent
            model_path = str(project_root / "model" / "InternVL2_8B")
        
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.conversation_history = None
        
        # 이미지 전처리 설정
        self.input_size = 448
        self.max_num_tiles = 12
        
    def load_model(self):
        """모델 및 토크나이저 로딩"""
        if self.model is not None:
            return  # 이미 로드됨
        
        print(f"InternVL2-8B 모델 로딩 중: {self.model_path}")
        
        try:
            # 모델 로딩
            self.model = AutoModel.from_pretrained(
                self.model_path,
                torch_dtype=self.torch_dtype,
                low_cpu_mem_usage=True,
                use_flash_attn=self.use_flash_attn,
                load_in_8bit=self.load_in_8bit,
                trust_remote_code=True
            )
            
            # 디바이스 설정
            if self.device == "cuda" and torch.cuda.is_available() and not self.load_in_8bit:
                self.model = self.model.eval().cuda()
            else:
                self.model = self.model.eval()
            
            # 토크나이저 로딩
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                use_fast=False
            )
            
            print("InternVL2-8B 모델 로딩 완료")
            
        except Exception as e:
            raise RuntimeError(f"모델 로딩 실패: {str(e)}")
    
    def load_image(self, image_path: str) -> torch.Tensor:
        """
        이미지 로딩 및 전처리
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            torch.Tensor: 전처리된 이미지 텐서
        """
        image = Image.open(image_path).convert('RGB')
        
        # 동적 전처리 (InternVL2 방식)
        transform = self._build_transform(self.input_size)
        images = self._dynamic_preprocess(image, self.input_size, use_thumbnail=True, max_num=self.max_num_tiles)
        
        pixel_values = [transform(img) for img in images]
        pixel_values = torch.stack(pixel_values)
        
        return pixel_values
    
    def _build_transform(self, input_size: int):
        """이미지 전처리 변환 함수 생성"""
        IMAGENET_MEAN = (0.485, 0.456, 0.406)
        IMAGENET_STD = (0.229, 0.224, 0.225)
        
        return T.Compose([
            T.Resize((input_size, input_size), interpolation=T.InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])
    
    def _find_closest_aspect_ratio(self, aspect_ratio, target_ratios, width, height, image_size):
        """가장 가까운 종횡비 찾기"""
        best_ratio_diff = float('inf')
        best_ratio = (1, 1)
        area = width * height
        for ratio in target_ratios:
            target_aspect_ratio = ratio[0] / ratio[1]
            ratio_diff = abs(aspect_ratio - target_aspect_ratio)
            if ratio_diff < best_ratio_diff:
                best_ratio_diff = ratio_diff
                best_ratio = ratio
            elif ratio_diff == best_ratio_diff:
                if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                    best_ratio = ratio
        return best_ratio
    
    def _dynamic_preprocess(
        self,
        image: Image.Image,
        input_size: int = 448,
        use_thumbnail: bool = True,
        max_num: int = 12,
        min_num: int = 1
    ) -> List[Image.Image]:
        """
        동적 이미지 전처리 (InternVL2 방식)
        큰 이미지를 타일로 분할하여 처리
        """
        from torchvision.transforms.functional import InterpolationMode
        
        orig_width, orig_height = image.size
        aspect_ratio = orig_width / orig_height
        
        # 가능한 타겟 종횡비 계산
        target_ratios = set(
            (i, j) for n in range(min_num, max_num + 1) 
            for i in range(1, n + 1) for j in range(1, n + 1) 
            if i * j <= max_num and i * j >= min_num
        )
        target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])
        
        # 가장 가까운 종횡비 찾기
        target_aspect_ratio = self._find_closest_aspect_ratio(
            aspect_ratio, target_ratios, orig_width, orig_height, input_size
        )
        
        # 타겟 너비/높이 계산
        target_width = input_size * target_aspect_ratio[0]
        target_height = input_size * target_aspect_ratio[1]
        blocks = target_aspect_ratio[0] * target_aspect_ratio[1]
        
        # 이미지 리사이즈
        resized_img = image.resize((int(target_width), int(target_height)), Image.Resampling.BICUBIC)
        processed_images = []
        
        # 이미지 분할
        for i in range(blocks):
            box = (
                (i % (int(target_width) // input_size)) * input_size,
                (i // (int(target_width) // input_size)) * input_size,
                ((i % (int(target_width) // input_size)) + 1) * input_size,
                ((i // (int(target_width) // input_size)) + 1) * input_size
            )
            split_img = resized_img.crop(box)
            processed_images.append(split_img)
        
        # 썸네일 추가
        if use_thumbnail and len(processed_images) != 1:
            thumbnail_img = image.resize((input_size, input_size), Image.Resampling.BICUBIC)
            processed_images.append(thumbnail_img)
        
        return processed_images
    
    def chat(
        self,
        text: str,
        image_path: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None,
        history: Optional[List] = None,
        return_history: bool = True
    ) -> Tuple[str, Optional[List]]:
        """
        대화 형식으로 추론 수행
        
        Args:
            text: 사용자 입력 텍스트
            image_path: 이미지 경로 (선택사항)
            generation_config: 생성 설정
            history: 대화 히스토리
            return_history: 히스토리 반환 여부
            
        Returns:
            Tuple[str, Optional[List]]: (응답 텍스트, 히스토리)
        """
        if self.model is None:
            self.load_model()
        
        # 기본 생성 설정
        if generation_config is None:
            generation_config = {
                "max_new_tokens": 1024,
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.9
            }
        
        # 이미지 처리
        pixel_values = None
        if image_path:
            pixel_values = self.load_image(image_path)
            if self.device == "cuda" and torch.cuda.is_available():
                pixel_values = pixel_values.to(self.torch_dtype).cuda()
            else:
                pixel_values = pixel_values.to(self.torch_dtype)
        
        # 대화 수행
        try:
            response, history = self.model.chat(
                self.tokenizer,
                pixel_values,
                text,
                generation_config,
                history=history,
                return_history=return_history
            )
            return response, history
        except Exception as e:
            raise RuntimeError(f"추론 실패: {str(e)}")
    
    def generate_text(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        max_new_tokens: int = 512
    ) -> str:
        """
        텍스트 생성 (간단한 인터페이스)
        
        Args:
            prompt: 프롬프트
            image_path: 이미지 경로 (선택사항)
            max_new_tokens: 최대 생성 토큰 수
            
        Returns:
            str: 생성된 텍스트
        """
        generation_config = {
            "max_new_tokens": max_new_tokens,
            "do_sample": True,
            "temperature": 0.7
        }
        
        response, _ = self.chat(
            text=prompt,
            image_path=image_path,
            generation_config=generation_config,
            return_history=False
        )
        
        return response
    
    def analyze_image(self, image_path: str, task: str = "describe") -> str:
        """
        이미지 분석 (특정 작업 수행)
        
        Args:
            image_path: 이미지 경로
            task: 작업 유형 ('describe', 'analyze_garment', 'extract_features')
            
        Returns:
            str: 분석 결과
        """
        task_prompts = {
            "describe": "<image>\n이 이미지를 자세히 설명해주세요.",
            "analyze_garment": "<image>\n이 이미지의 의류(옷)에 대해 분석해주세요. 종류, 스타일, 색상, 재질 등을 포함하여 설명해주세요.",
            "extract_features": "<image>\n이 이미지에서 의류의 주요 특징을 추출해주세요. 디자인 요소, 패턴, 액세서리 등을 포함하여 설명해주세요."
        }
        
        prompt = task_prompts.get(task, task_prompts["describe"])
        
        return self.generate_text(prompt, image_path=image_path, max_new_tokens=512)
    
    def reset_history(self):
        """대화 히스토리 초기화"""
        self.conversation_history = None

