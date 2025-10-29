# Quick restart worker script
Write-Host "Restarting Worker..." -ForegroundColor Cyan

# Stop worker processes
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $proc = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue
        if ($proc -and $proc.CommandLine -like "*rq worker*") {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped worker process $($_.Id)" -ForegroundColor Yellow
        }
    } catch {}
}

Start-Sleep -Seconds 1

# Start worker
Write-Host "Starting Worker..." -ForegroundColor Green
$workerCmd = "cd '$PWD'; `$host.ui.RawUI.WindowTitle = 'FanslyMotion Worker'; python worker/worker.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $workerCmd

Write-Host "Worker started in new window" -ForegroundColor Green
Write-Host "Check the window for logs and errors" -ForegroundColor Yellow

