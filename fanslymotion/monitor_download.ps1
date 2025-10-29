# Monitor model download progress
Write-Host "Monitoring model download..." -ForegroundColor Cyan
Write-Host "This will take 10-60 minutes depending on internet speed" -ForegroundColor Yellow
Write-Host "Model size: ~15 GB" -ForegroundColor Gray
Write-Host ""

$previousSize = 0
$startTime = Get-Date

while ($true) {
    Clear-Host
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $elapsed = ((Get-Date) - $startTime).TotalMinutes
    
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "  Model Download Monitor" -ForegroundColor Cyan
    Write-Host "  Time: $timestamp (Elapsed: $([math]::Round($elapsed, 1)) min)" -ForegroundColor Gray
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check cache size
    $cacheSize = 0
    $fileCount = 0
    
    if (Test-Path ".\cache\models") {
        $items = Get-ChildItem -Path ".\cache\models" -Recurse -File -ErrorAction SilentlyContinue
        if ($items) {
            $cacheSize = ($items | Measure-Object -Property Length -Sum).Sum
            $fileCount = $items.Count
        }
    }
    
    $cacheSizeGB = [math]::Round($cacheSize / 1GB, 2)
    $downloadedPercent = [math]::Round(($cacheSizeGB / 15) * 100, 1)
    
    Write-Host "Cache Status:" -ForegroundColor Yellow
    Write-Host "  Downloaded: $cacheSizeGB GB / ~15 GB ($downloadedPercent%)" -ForegroundColor Gray
    Write-Host "  Files: $fileCount" -ForegroundColor Gray
    
    if ($previousSize -gt 0) {
        $diff = $cacheSize - $previousSize
        if ($diff -gt 0) {
            $diffMB = [math]::Round($diff / 1MB, 1)
            $speedMBps = [math]::Round($diffMB / 10, 1)
            Write-Host "  Download speed: $speedMBps MB/s (last 10s)" -ForegroundColor Green
            
            if ($speedMBps -gt 0) {
                $remaining = (15 - $cacheSizeGB) * 1024 / $speedMBps / 60
                Write-Host "  ETA: $([math]::Round($remaining, 0)) minutes" -ForegroundColor Cyan
            }
        } else {
            Write-Host "  Download speed: idle" -ForegroundColor DarkGray
        }
    }
    
    $previousSize = $cacheSize
    
    Write-Host ""
    
    # Check Python processes
    Write-Host "Process Status:" -ForegroundColor Yellow
    $pythonProcs = Get-Process python -ErrorAction SilentlyContinue
    if ($pythonProcs) {
        $mainProc = $pythonProcs | Sort-Object WorkingSet64 -Descending | Select-Object -First 1
        $memGB = [math]::Round($mainProc.WorkingSet64/1GB, 2)
        Write-Host "  Python Memory: $memGB GB" -ForegroundColor Gray
        Write-Host "  Status: Downloading..." -ForegroundColor Green
    } else {
        Write-Host "  No Python processes (download may have finished or failed)" -ForegroundColor Red
        break
    }
    
    Write-Host ""
    
    # Check if download complete
    if ($cacheSizeGB -gt 14) {
        Write-Host "Download appears complete!" -ForegroundColor Green
        Write-Host "Waiting for model loading to GPU..." -ForegroundColor Yellow
    }
    
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor DarkGray
    Write-Host ""
    
    Start-Sleep -Seconds 10
}

Write-Host ""
Write-Host "Monitoring stopped." -ForegroundColor Gray
Write-Host ""




