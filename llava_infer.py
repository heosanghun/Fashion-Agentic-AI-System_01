from transformers import LlavaForCausalLM, AutoTokenizer, AutoProcessor
import torch
from PIL import Image

# 1. 모델 경로 (로컬 폴더)
model_path = "/mnt/d/AI/ChatGarment/checkpoints/llava-v1.5-7b"

# 2. 모델, 토크나이저, 프로세서 로드
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = LlavaForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, device_map="auto")
processor = AutoProcessor.from_pretrained(model_path)

# 3. 이미지 불러오기 (테스트할 이미지 경로로 변경)
image = Image.open("/mnt/d/AI/ChatGarment/ChatGarment/data/eval_images/1.jpg")

# 4. 프롬프트 입력
prompt = "Describe this image."

# 5. 입력 준비
inputs = processor(prompt, image, return_tensors="pt").to(model.device)

# 6. 추론
with torch.no_grad():
    output = model.generate(**inputs, max_new_tokens=64)

# 7. 결과 출력
print(tokenizer.decode(output[0], skip_special_tokens=True)) 