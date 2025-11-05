# 리눅스 서버 자동 찾기 스크립트

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "리눅스 서버 자동 검색 시작" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# 현재 Windows IP 확인
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*"} | Select-Object -First 1).IPAddress
Write-Host "[*] 현재 Windows IP: $localIP" -ForegroundColor Cyan

# 네트워크 범위 추출
$ipParts = $localIP -split '\.'
$networkBase = "$($ipParts[0]).$($ipParts[1]).$($ipParts[2])"

Write-Host "[*] 네트워크 범위: $networkBase.1-254" -ForegroundColor Cyan
Write-Host "[*] 서버 검색 중 (포트 22 및 9000 확인)..." -ForegroundColor Yellow
Write-Host ""

$foundServers = @()

# 빠른 검색: 일반적인 서버 IP 범위
$testIPs = @(
    "$networkBase.100",
    "$networkBase.101",
    "$networkBase.102",
    "$networkBase.200",
    "$networkBase.201",
    "$networkBase.202"
)

foreach ($ip in $testIPs) {
    try {
        $sshTest = Test-NetConnection -ComputerName $ip -Port 22 -WarningAction SilentlyContinue -InformationLevel Quiet
        $httpTest = Test-NetConnection -ComputerName $ip -Port 9000 -WarningAction SilentlyContinue -InformationLevel Quiet
        
        if ($sshTest -or $httpTest) {
            $foundServers += $ip
            Write-Host "[+] 서버 발견: $ip (SSH: $sshTest, HTTP: $httpTest)" -ForegroundColor Green
        }
    } catch {
        # 무시
    }
}

# 검색 결과
Write-Host ""
if ($foundServers.Count -eq 0) {
    Write-Host "[!] 자동으로 서버를 찾을 수 없습니다." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "수동 입력 방법:" -ForegroundColor Yellow
    Write-Host "1. 리눅스 서버에서 다음 명령 실행: hostname -I" -ForegroundColor Cyan
    Write-Host "2. 결과로 나온 IP 주소를 아래 스크립트에 입력" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "또는 WSL 사용 중이면 'localhost' 또는 '127.0.0.1' 사용 가능" -ForegroundColor Yellow
} else {
    Write-Host "[+] 발견된 서버: $($foundServers -join ', ')" -ForegroundColor Green
    Write-Host "[*] 첫 번째 서버를 사용합니다: $($foundServers[0])" -ForegroundColor Cyan
    
    # 환경 변수 설정
    $env:CHATGARMENT_SERVICE_URL = "http://$($foundServers[0]):9000"
    $env:USE_CHATGARMENT_SERVICE = "true"
    
    Write-Host ""
    Write-Host "[+] 환경 변수 설정 완료" -ForegroundColor Green
    Write-Host "   CHATGARMENT_SERVICE_URL=$env:CHATGARMENT_SERVICE_URL" -ForegroundColor Yellow
}

