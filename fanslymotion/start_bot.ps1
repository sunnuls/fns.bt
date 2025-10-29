# Start FanslyMotion Bot - Simple script
# Usage: .\start_bot.ps1

Write-Host "Starting FanslyMotion Bot..." -ForegroundColor Cyan

# Check current directory
if (-not (Test-Path "bot\bot.py")) {
    Write-Host "ERROR: Run script from fanslymotion directory!" -ForegroundColor Red
    exit 1
}

# Stop old processes
Write-Host "Stopping old processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*Python*" 
} | ForEach-Object {
    try {
        $proc = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)"
        if ($proc.CommandLine -like "*bot.bot*" -or $proc.CommandLine -like "*uvicorn*backend*" -or $proc.CommandLine -like "*rq worker*") {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            Write-Host "   Stopped process $($_.Id)" -ForegroundColor Green
        }
    } catch {
        # Ignore errors
    }
}

Start-Sleep -Seconds 1

# Check Redis
Write-Host ""
Write-Host "Checking Redis..." -ForegroundColor Yellow
$redisCheck = python -c 'import redis; r = redis.Redis(host="localhost", port=6379, socket_connect_timeout=2); r.ping(); print("OK")' 2>&1
if ($LASTEXITCODE -eq 0 -and $redisCheck -match "OK") {
    Write-Host "   Redis is running" -ForegroundColor Green
} else {
    Write-Host "   Redis not running, starting..." -ForegroundColor Yellow
    if (Test-Path "redis\redis-server.exe") {
        Start-Process -FilePath "redis\redis-server.exe" -WindowStyle Minimized
        Start-Sleep -Seconds 2
        Write-Host "   Redis started" -ForegroundColor Green
    } else {
        Write-Host "   Redis not found in redis\ directory" -ForegroundColor Red
        Write-Host "   Continuing without Redis (may not work)" -ForegroundColor Yellow
    }
}

# Start Backend
Write-Host ""
Write-Host "Starting Backend API..." -ForegroundColor Yellow
$backendCmd = "cd '$PWD'; `$host.ui.RawUI.WindowTitle = 'FanslyMotion Backend'; python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
Start-Sleep -Seconds 3
Write-Host "   Backend started on http://localhost:8000" -ForegroundColor Green

# Start Worker
Write-Host ""
Write-Host "Starting Worker..." -ForegroundColor Yellow
$workerCmd = "cd '$PWD'; `$host.ui.RawUI.WindowTitle = 'FanslyMotion Worker'; python worker/worker.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $workerCmd
Start-Sleep -Seconds 2
Write-Host "   Worker started" -ForegroundColor Green

# Start Bot
Write-Host ""
Write-Host "Starting Telegram Bot..." -ForegroundColor Yellow
$botCmd = @"
cd '$PWD'
`$host.ui.RawUI.WindowTitle = 'FanslyMotion Bot'
Write-Host '=== Starting Bot ===' -ForegroundColor Cyan
Write-Host 'Testing imports first...' -ForegroundColor Yellow
python test_import.py
if (`$LASTEXITCODE -ne 0) {
    Write-Host 'Import test failed!' -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit
}
Write-Host '`nStarting bot process...' -ForegroundColor Green
python -u -m bot.bot
Write-Host '`nBot process ended. Press Enter to close.' -ForegroundColor Gray
Read-Host
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $botCmd
Start-Sleep -Seconds 2
Write-Host "   Bot started (check window for logs)" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All services started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services running in separate windows:" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   Worker: Processing video jobs" -ForegroundColor Cyan
Write-Host "   Bot: Telegram bot" -ForegroundColor Cyan
Write-Host ""
Write-Host "Open Telegram and find your bot" -ForegroundColor Yellow
Write-Host "Send /start to begin" -ForegroundColor Yellow
Write-Host ""
Write-Host "WARNING: Do not close PowerShell windows!" -ForegroundColor Red
Write-Host "Closing window will stop corresponding service" -ForegroundColor Red
Write-Host ""
