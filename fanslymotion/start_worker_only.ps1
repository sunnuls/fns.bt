# Start only Worker for GPU processing
Write-Host "=== Starting Worker Only ===" -ForegroundColor Cyan

# Stop old worker
Write-Host "Stopping old worker processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $proc = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue
        if ($proc -and $proc.CommandLine -like "*worker*") {
            Write-Host "  Stopping PID $($_.Id)"
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    } catch {}
}
Start-Sleep -Seconds 2

# Check Redis
Write-Host "`nChecking Redis..." -ForegroundColor Yellow
try {
    $redisCheck = python -c "import redis; r = redis.Redis(); print('OK' if r.ping() else 'FAIL')" 2>&1
    if ($redisCheck -match "OK") {
        Write-Host "  Redis: OK" -ForegroundColor Green
    } else {
        Write-Host "  Redis: FAILED - Starting..." -ForegroundColor Red
        if (Test-Path "redis\redis-server.exe") {
            Start-Process -FilePath "redis\redis-server.exe" -WindowStyle Minimized
            Start-Sleep -Seconds 2
        }
    }
} catch {
    Write-Host "  Redis check failed" -ForegroundColor Red
}

# Start Worker
Write-Host "`nStarting Worker..." -ForegroundColor Yellow
$workerCmd = @"
cd '$PWD'
`$host.ui.RawUI.WindowTitle = 'FanslyMotion Worker [GPU]'
Write-Host '=== WORKER STARTUP ===' -ForegroundColor Cyan
Write-Host 'Starting GPU Worker...' -ForegroundColor Yellow
python -u worker/worker.py
Write-Host '`nWorker process ended. Press Enter to close.' -ForegroundColor Gray
Read-Host
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $workerCmd
Write-Host "  Worker started in new window!" -ForegroundColor Green
Write-Host "`nCheck the 'FanslyMotion Worker [GPU]' window for logs" -ForegroundColor Yellow

