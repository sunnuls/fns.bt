# Test API and monitor job progress in real-time
Write-Host "Creating test job..." -ForegroundColor Cyan

# Find test image
$testImages = Get-ChildItem -Path ".\storage\hot\*_input.png" -ErrorAction SilentlyContinue | Select-Object -First 1

if (-not $testImages) {
    Write-Host "No test images found!" -ForegroundColor Red
    exit 1
}

$imagePath = $testImages.FullName
Write-Host "Using image: $($testImages.Name)" -ForegroundColor Gray

# Read and encode image
$imageBytes = [System.IO.File]::ReadAllBytes($imagePath)
$imageBase64 = [Convert]::ToBase64String($imageBytes)

# Create job
$jobRequest = @{
    user_id = 123456789
    image_data = $imageBase64
    duration = 6
    resolution = "720p"
    motion_preset = "micro"
} | ConvertTo-Json

Write-Host "Sending job request..." -ForegroundColor Gray
$jobResponse = Invoke-RestMethod -Uri "http://localhost:8000/job/create" -Method Post -Body $jobRequest -ContentType "application/json"

Write-Host ""
Write-Host "Job created!" -ForegroundColor Green
Write-Host "  Job ID: $($jobResponse.job_id)" -ForegroundColor Yellow
Write-Host ""

# Monitor progress
Write-Host "Starting real-time monitoring..." -ForegroundColor Cyan
Write-Host ""

$jobId = $jobResponse.job_id
$previousProgress = -1
$startTime = Get-Date

while ($true) {
    try {
        $status = Invoke-RestMethod -Uri "http://localhost:8000/job/status/$jobId" -Method Get -ErrorAction Stop
        
        $currentProgress = if ($status.progress) { [math]::Round($status.progress, 1) } else { 0 }
        
        # Only print if progress changed
        if ($currentProgress -ne $previousProgress) {
            $elapsed = ((Get-Date) - $startTime).TotalSeconds
            $timestamp = Get-Date -Format "HH:mm:ss"
            
            $color = switch ($status.status) {
                "queued" { "Yellow" }
                "processing" { "Cyan" }
                "completed" { "Green" }
                "failed" { "Red" }
                default { "Gray" }
            }
            
            $progressBar = "[" + ("#" * [math]::Floor($currentProgress / 5)) + (" " * (20 - [math]::Floor($currentProgress / 5))) + "]"
            
            Write-Host "[$timestamp] $progressBar $currentProgress% - $($status.message)" -ForegroundColor $color
            
            $previousProgress = $currentProgress
            
            # Exit if completed or failed
            if ($status.status -eq "completed") {
                Write-Host ""
                Write-Host "SUCCESS! Video generated in $([math]::Round($elapsed, 1)) seconds" -ForegroundColor Green
                Write-Host "Video path: $($status.video_path)" -ForegroundColor Gray
                break
            } elseif ($status.status -eq "failed") {
                Write-Host ""
                Write-Host "FAILED after $([math]::Round($elapsed, 1)) seconds" -ForegroundColor Red
                Write-Host "Error: $($status.error)" -ForegroundColor Red
                break
            }
        }
        
        Start-Sleep -Seconds 2
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        break
    }
}

Write-Host ""




