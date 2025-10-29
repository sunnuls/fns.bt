# Continuous monitoring of job progress and system resources
param(
    [string]$jobId = "685c7b7a-a38d-432e-b374-8ac21017ac59",
    [int]$refreshSeconds = 10
)

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Real-Time Progress Monitor" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Job ID: $jobId" -ForegroundColor Gray
Write-Host "Refresh: Every ${refreshSeconds}s (Ctrl+C to stop)" -ForegroundColor Gray
Write-Host ""

$previousStatus = ""
$previousProgress = -1
$iteration = 0

while ($true) {
    $iteration++
    Clear-Host
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "  Real-Time Monitor - $timestamp" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check job status
    Write-Host "JOB STATUS:" -ForegroundColor Yellow
    try {
        $status = Invoke-RestMethod -Uri "http://localhost:8000/job/status/$jobId" -Method Get -ErrorAction Stop
        
        $currentStatus = $status.status
        $currentProgress = if ($status.progress) { [math]::Round($status.progress, 1) } else { 0 }
        
        $color = switch ($currentStatus) {
            "queued" { "Yellow" }
            "processing" { "Cyan" }
            "completed" { "Green" }
            "failed" { "Red" }
            default { "Gray" }
        }
        
        Write-Host "  Status: $currentStatus" -ForegroundColor $color
        if ($status.progress) {
            $progressBar = "[" + ("#" * [math]::Floor($currentProgress / 5)) + (" " * (20 - [math]::Floor($currentProgress / 5))) + "]"
            Write-Host "  Progress: $progressBar $currentProgress%" -ForegroundColor $color
        }
        if ($status.message) {
            Write-Host "  Message: $($status.message)" -ForegroundColor Gray
        }
        if ($status.error) {
            Write-Host "  Error: $($status.error)" -ForegroundColor Red
        }
        
        # Exit if completed or failed
        if ($currentStatus -eq "completed" -or $currentStatus -eq "failed") {
            Write-Host ""
            Write-Host "Job finished with status: $currentStatus" -ForegroundColor $color
            break
        }
    }
    catch {
        Write-Host "  Unable to check job status" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # System resources
    Write-Host "SYSTEM RESOURCES:" -ForegroundColor Yellow
    $pythonProcs = Get-Process python -ErrorAction SilentlyContinue | 
        Sort-Object WorkingSet64 -Descending | 
        Select-Object -First 1
    
    if ($pythonProcs) {
        $memGB = [math]::Round($pythonProcs.WorkingSet64/1GB, 2)
        $runtime = (Get-Date) - $pythonProcs.StartTime
        $runtimeStr = "{0:D2}:{1:D2}:{2:D2}" -f $runtime.Hours, $runtime.Minutes, $runtime.Seconds
        Write-Host "  Worker Memory: ${memGB} GB" -ForegroundColor Gray
        Write-Host "  Worker Runtime: $runtimeStr" -ForegroundColor Gray
    }
    
    # GPU info
    try {
        $gpuInfo = nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>$null
        if ($gpuInfo) {
            $parts = $gpuInfo -split ','
            $gpuUtil = $parts[0].Trim()
            $gpuMemUsed = $parts[1].Trim()
            $gpuMemTotal = $parts[2].Trim()
            $gpuTemp = $parts[3].Trim()
            
            $gpuColor = if ([int]$gpuUtil -gt 80) { "Green" } elseif ([int]$gpuUtil -gt 30) { "Yellow" } else { "Gray" }
            
            Write-Host "  GPU Utilization: ${gpuUtil}%" -ForegroundColor $gpuColor
            Write-Host "  GPU Memory: ${gpuMemUsed}MB / ${gpuMemTotal}MB" -ForegroundColor Gray
            Write-Host "  GPU Temp: ${gpuTemp}C" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  GPU info not available" -ForegroundColor DarkGray
    }
    
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "Next refresh in ${refreshSeconds}s..." -ForegroundColor DarkGray
    Write-Host ""
    
    Start-Sleep -Seconds $refreshSeconds
}

Write-Host ""
Write-Host "Monitoring stopped." -ForegroundColor Gray
Write-Host ""





