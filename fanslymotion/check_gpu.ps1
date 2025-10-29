# Check GPU usage and process status
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  System Resource Monitor" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Python processes
Write-Host "Python Processes (sorted by memory):" -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | 
    Select-Object Id, 
        @{Name="CPU%";Expression={$_.CPU}},
        @{Name="Memory(GB)";Expression={[math]::Round($_.WorkingSet64/1GB,2)}},
        @{Name="Runtime";Expression={(Get-Date) - $_.StartTime | ForEach-Object {"{0:D2}:{1:D2}:{2:D2}" -f $_.Hours,$_.Minutes,$_.Seconds}}} |
    Sort-Object "Memory(GB)" -Descending |
    Format-Table -AutoSize

Write-Host ""

# Try to check NVIDIA GPU if available
Write-Host "Checking GPU..." -ForegroundColor Yellow
try {
    $gpuInfo = nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>$null
    if ($gpuInfo) {
        Write-Host "  GPU Info:" -ForegroundColor Green
        $gpuInfo | ForEach-Object {
            $parts = $_ -split ','
            Write-Host "    GPU $($parts[0].Trim()): $($parts[1].Trim())" -ForegroundColor Gray
            Write-Host "    Utilization: $($parts[2].Trim())%" -ForegroundColor Gray
            Write-Host "    Memory: $($parts[3].Trim())MB / $($parts[4].Trim())MB" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "  NVIDIA GPU not detected or nvidia-smi not available" -ForegroundColor Gray
    Write-Host "  (This is normal if using CPU or non-NVIDIA GPU)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

