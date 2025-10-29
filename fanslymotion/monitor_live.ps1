# Live Monitoring Script for FanslyMotion
# Continuously updates status every 5 seconds

$refreshInterval = 5

Write-Host "Starting Live Monitor (Refresh every ${refreshInterval}s, Ctrl+C to exit)" -ForegroundColor Cyan
Write-Host ""

while ($true) {
    Clear-Host
    
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "  FanslyMotion Live Monitor" -ForegroundColor Cyan
    Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check Redis
    Write-Host "Redis Server:" -ForegroundColor Yellow -NoNewline
    $redisProcess = Get-Process redis-server -ErrorAction SilentlyContinue
    if ($redisProcess) {
        $redisPid = $redisProcess.Id
        Write-Host " Running (PID: $redisPid)" -ForegroundColor Green
        $redisPing = .\redis\redis-cli.exe ping 2>$null
        Write-Host "  Response: $redisPing" -ForegroundColor Gray
    } else {
        Write-Host " Not Running" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Check Python processes
    Write-Host "Python Processes:" -ForegroundColor Yellow
    $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        foreach ($proc in $pythonProcesses) {
            $runtime = (Get-Date) - $proc.StartTime
            $runtimeStr = "{0:D2}:{1:D2}:{2:D2}" -f $runtime.Hours, $runtime.Minutes, $runtime.Seconds
            $memMB = [math]::Round($proc.WorkingSet64 / 1MB, 2)
            Write-Host "  PID $($proc.Id) - Runtime: $runtimeStr - Memory: ${memMB}MB" -ForegroundColor Gray
        }
    } else {
        Write-Host "  No Python processes found" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Check Backend API
    Write-Host "Backend API:" -ForegroundColor Yellow -NoNewline
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 3
        Write-Host " Healthy" -ForegroundColor Green
        Write-Host "  Redis: $($response.redis)" -ForegroundColor Gray
        Write-Host "  Queue: $($response.queue_length)/$($response.max_queue_size)" -ForegroundColor Gray
    } catch {
        Write-Host " Not responding" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Check Queue Status
    Write-Host "Queue Status:" -ForegroundColor Yellow
    $queueInfo = .\redis\redis-cli.exe LLEN rq:queue:svd_jobs 2>$null
    Write-Host "  Pending jobs: $queueInfo" -ForegroundColor Gray
    
    $failedInfo = .\redis\redis-cli.exe LLEN rq:queue:failed 2>$null
    if ($failedInfo -and [int]$failedInfo -gt 0) {
        Write-Host "  Failed jobs: $failedInfo" -ForegroundColor Red
    } else {
        Write-Host "  Failed jobs: 0" -ForegroundColor Green
    }
    
    # Check started jobs
    $startedInfo = .\redis\redis-cli.exe LLEN rq:queue:started 2>$null
    if ($startedInfo -and [int]$startedInfo -gt 0) {
        Write-Host "  Processing: $startedInfo" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "Next refresh in ${refreshInterval}s..." -ForegroundColor DarkGray
    Write-Host ""
    
    Start-Sleep -Seconds $refreshInterval
}



