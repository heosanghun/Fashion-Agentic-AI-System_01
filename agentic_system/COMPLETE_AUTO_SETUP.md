# 완전 자동 설정 가이드 (최종)

## ✅ Windows 설정 - 완료됨!

모든 Windows 설정이 자동으로 완료되었습니다:
- ✅ 환경 변수 설정 완료
- ✅ 코드 통합 완료
- ✅ WSL Ubuntu 확인 완료
- ✅ 서비스 파일 준비 완료

## 🚀 WSL 서비스 시작 (최종 단계)

### 방법 1: Windows에서 자동 시작

PowerShell에서 다음 명령어 실행:

```powershell
wsl -d Ubuntu -- bash -c "cd ~/ChatGarment/chatgarment_service && nohup python3 main.py > service.log 2>&1 & echo 'Service started'"
```

### 방법 2: WSL Ubuntu 터미널에서 직접 시작

1. WSL Ubuntu 터미널 열기
2. 다음 명령어 실행:

```bash
cd ~/ChatGarment/chatgarment_service
python3 main.py
```

### 방법 3: 백그라운드로 시작 (추천)

WSL Ubuntu 터미널에서:

```bash
cd ~/ChatGarment/chatgarment_service
nohup python3 main.py > service.log 2>&1 &
```

## ✅ 서비스 확인

서비스가 시작되었는지 확인:

```bash
# WSL에서
curl http://localhost:9000/health

# Windows에서
Invoke-WebRequest -Uri "http://localhost:9000/health"
```

**예상 응답**: `{"status":"healthy","service":"chatgarment"}`

## 🚀 API 서버 재시작

서비스가 시작된 후, Windows PowerShell에서:

```powershell
.\restart_api_server.ps1
```

또는:

```batch
python start_api_server.py
```

## 🎉 완료!

이제 프론트엔드에서 테스트:
1. http://localhost:5173 접속
2. 의류 이미지 업로드
3. "요청 전송" 클릭
4. **실제 ChatGarment 서비스**가 처리합니다!

## 📝 참고사항

- WSL 서비스는 Windows 재시작 시 자동으로 시작되지 않습니다
- 서비스를 재시작하려면 위의 "WSL 서비스 시작" 명령어를 다시 실행하세요
- 서비스 로그 확인: `wsl -d Ubuntu -- bash -c "tail -f ~/ChatGarment/chatgarment_service/service.log"`

