# Auto-monitor and restart script for FanslyMotion

Write-Host "========================================" -ForegroundColor Green
Write-Host "FANSLYMOTION AUTO-MONITOR" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Stop all existing processes
Write-Host "Stopping all services..." -ForegroundColor Cyan
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Write-Host "OK - All stopped" -ForegroundColor Green
Write-Host ""

# Check Redis
Write-Host "Starting Redis..." -ForegroundColor Cyan
$redis = Get-Process redis-server -ErrorAction SilentlyContinue
if (-not $redis) {
    $redisPath = "C:\Redis-x64-3.0.504\redis-server.exe"
    if (Test-Path $redisPath) {
        Start-Process -FilePath $redisPath -WindowStyle Normal
        Start-Sleep -Seconds 2
    }
}
Write-Host "OK - Redis running" -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "Starting Backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\fns_bot\fanslymotion; .\venv\Scripts\Activate.ps1; `$host.UI.RawUI.WindowTitle='BACKEND'; python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000" -WindowStyle Normal
Start-Sleep -Seconds 7

# Test Backend
$backendOK = $false
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "OK - Backend running" -ForegroundColor Green
    $backendOK = $true
} catch {
    Write-Host "FAIL - Backend not responding" -ForegroundColor Red
}
Write-Host ""

# Start Worker
Write-Host "Starting Worker..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\fns_bot\fanslymotion; .\venv\Scripts\Activate.ps1; `$host.UI.RawUI.WindowTitle='WORKER'; python worker/worker.py" -WindowStyle Normal
Start-Sleep -Seconds 3
Write-Host "OK - Worker started" -ForegroundColor Green
Write-Host ""

# Start Bot
Write-Host "Starting Bot..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\fns_bot\fanslymotion; .\venv\Scripts\Activate.ps1; `$host.UI.RawUI.WindowTitle='BOT'; python bot/bot.py" -WindowStyle Normal
Start-Sleep -Seconds 3
Write-Host "OK - Bot started" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "ALL SERVICES STARTED!" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Open windows:" -ForegroundColor White
Write-Host "  1. BACKEND - FastAPI server" -ForegroundColor Gray
Write-Host "  2. WORKER - Video generation" -ForegroundColor Gray
Write-Host "  3. BOT - Telegram bot" -ForegroundColor Gray
Write-Host ""
if ($backendOK) {
    Write-Host "System is ready!" -ForegroundColor Green
    Write-Host "Try in Telegram: /start" -ForegroundColor Cyan
} else {
    Write-Host "Backend failed to start. Check BACKEND window for errors." -ForegroundColor Red
}

