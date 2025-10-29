# Start all FanslyMotion components
Write-Host "Starting all FanslyMotion components..." -ForegroundColor Cyan
Write-Host ""

# Kill existing Python processes
Write-Host "Stopping existing Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Start Backend
Write-Host "Starting FastAPI Backend..." -ForegroundColor Green
$backendCmd = "cd c:\fns_bot\fanslymotion ; .\venv\Scripts\python.exe -m uvicorn backend.app:app --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Minimized
Start-Sleep -Seconds 3

# Start Worker
Write-Host "Starting RQ Worker..." -ForegroundColor Yellow
$workerCmd = "cd c:\fns_bot\fanslymotion ; .\venv\Scripts\python.exe worker\worker.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $workerCmd -WindowStyle Minimized
Start-Sleep -Seconds 2

# Start Bot
Write-Host "Starting Telegram Bot..." -ForegroundColor Cyan
$botCmd = "cd c:\fns_bot\fanslymotion ; .\venv\Scripts\python.exe bot\bot.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $botCmd -WindowStyle Minimized
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "All components started!" -ForegroundColor Green
Write-Host ""

# Run status check
.\monitor_status.ps1



