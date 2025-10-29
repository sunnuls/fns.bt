# Start all services (Redis, Backend, Worker, Bot)
Write-Host "=== Starting All FanslyMotion Services ===" -ForegroundColor Cyan

# Stop old processes
Write-Host "`n[1] Stopping old processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $proc = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue
        if ($proc -and ($proc.CommandLine -like "*bot.bot*" -or $proc.CommandLine -like "*uvicorn*backend*" -or $proc.CommandLine -like "*worker*")) {
            Write-Host "  Stopped PID $($_.Id)" -ForegroundColor Gray
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    } catch {}
}
Start-Sleep -Seconds 2

# Check Redis
Write-Host "`n[2] Checking Redis..." -ForegroundColor Yellow
$redisCheck = python -c 'import redis; r = redis.Redis(host="localhost", port=6379, socket_connect_timeout=2); r.ping(); print("OK")' 2>&1
if ($LASTEXITCODE -eq 0 -and $redisCheck -match "OK") {
    Write-Host "  Redis: Running" -ForegroundColor Green
} else {
    Write-Host "  Redis: Starting..." -ForegroundColor Yellow
    if (Test-Path "redis\redis-server.exe") {
        Start-Process -FilePath "redis\redis-server.exe" -WindowStyle Minimized
        Start-Sleep -Seconds 2
    }
    Write-Host "  Redis: Started" -ForegroundColor Green
}

# Start Backend
Write-Host "`n[3] Starting Backend API..." -ForegroundColor Yellow
$backendCmd = @"
cd '$PWD'
`$host.ui.RawUI.WindowTitle = 'FanslyMotion Backend'
Write-Host '=== BACKEND API ===' -ForegroundColor Cyan
python -u -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
Write-Host '`nBackend stopped. Press Enter to close.' -ForegroundColor Gray
Read-Host
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
Start-Sleep -Seconds 3
Write-Host "  Backend: Started on http://localhost:8000" -ForegroundColor Green

# Start Worker
Write-Host "`n[4] Starting Worker (GPU)..." -ForegroundColor Yellow
$workerCmd = @"
cd '$PWD'
`$host.ui.RawUI.WindowTitle = 'FanslyMotion Worker [GPU]'
Write-Host '=== GPU WORKER ===' -ForegroundColor Cyan
python -u worker/worker.py
Write-Host '`nWorker stopped. Press Enter to close.' -ForegroundColor Gray
Read-Host
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $workerCmd
Start-Sleep -Seconds 2
Write-Host "  Worker: Started (check GPU window)" -ForegroundColor Green

# Start Bot
Write-Host "`n[5] Starting Telegram Bot..." -ForegroundColor Yellow
$botCmd = @"
cd '$PWD'
`$host.ui.RawUI.WindowTitle = 'FanslyMotion Bot'
Write-Host '=== TELEGRAM BOT ===' -ForegroundColor Cyan
Write-Host 'Starting bot (imports tested on startup)...' -ForegroundColor Yellow
python -u -m bot.bot
Write-Host '`nBot stopped. Press Enter to close.' -ForegroundColor Gray
Read-Host
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $botCmd
Start-Sleep -Seconds 2
Write-Host "  Bot: Started" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ALL SERVICES STARTED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nOpen these windows to monitor:" -ForegroundColor Yellow
Write-Host "  1. FanslyMotion Backend - API logs" -ForegroundColor Gray
Write-Host "  2. FanslyMotion Worker [GPU] - GPU processing logs" -ForegroundColor Gray
Write-Host "  3. FanslyMotion Bot - Bot interaction logs" -ForegroundColor Gray
Write-Host "`nIn Telegram, send /start and upload a photo!" -ForegroundColor Cyan

