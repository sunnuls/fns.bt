# Test API endpoints
Write-Host "Testing FanslyMotion API..." -ForegroundColor Cyan
Write-Host ""

# Test root endpoint
Write-Host "1. Testing root endpoint..." -ForegroundColor Yellow
try {
    $root = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get
    Write-Host "  Status: $($root.status)" -ForegroundColor Green
    Write-Host "  Service: $($root.service)" -ForegroundColor Gray
} catch {
    Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test health endpoint
Write-Host "2. Testing health endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "  Status: $($health.status)" -ForegroundColor Green
    Write-Host "  Redis: $($health.redis)" -ForegroundColor Gray
    Write-Host "  Queue: $($health.queue_length)/$($health.max_queue_size)" -ForegroundColor Gray
} catch {
    Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test with a sample image
Write-Host "3. Testing job creation (with sample image)..." -ForegroundColor Yellow
Write-Host "  Looking for test image in storage/hot..." -ForegroundColor Gray

$testImages = Get-ChildItem -Path ".\storage\hot\*_input.png" -ErrorAction SilentlyContinue | Select-Object -First 1

if ($testImages) {
    $imagePath = $testImages.FullName
    Write-Host "  Found: $($testImages.Name)" -ForegroundColor Gray
    
    try {
        # Read image and convert to base64
        $imageBytes = [System.IO.File]::ReadAllBytes($imagePath)
        $imageBase64 = [Convert]::ToBase64String($imageBytes)
        
        # Create job request
        $jobRequest = @{
            user_id = 123456789
            image_data = $imageBase64
            duration = 6
            resolution = "720p"
            motion_preset = "micro"
        } | ConvertTo-Json
        
        Write-Host "  Creating test job..." -ForegroundColor Gray
        $jobResponse = Invoke-RestMethod -Uri "http://localhost:8000/job/create" -Method Post -Body $jobRequest -ContentType "application/json"
        
        Write-Host "  Job created successfully!" -ForegroundColor Green
        Write-Host "  Job ID: $($jobResponse.job_id)" -ForegroundColor Gray
        Write-Host "  Status: $($jobResponse.status)" -ForegroundColor Gray
        Write-Host "  Queue position: $($jobResponse.queue_position)" -ForegroundColor Gray
        Write-Host "  Estimated time: $($jobResponse.estimated_time)s" -ForegroundColor Gray
        
        # Check job status
        Write-Host ""
        Write-Host "  Checking job status..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
        
        $statusResponse = Invoke-RestMethod -Uri "http://localhost:8000/job/status/$($jobResponse.job_id)" -Method Get
        Write-Host "  Current status: $($statusResponse.status)" -ForegroundColor Gray
        if ($statusResponse.progress) {
            Write-Host "  Progress: $($statusResponse.progress)%" -ForegroundColor Gray
        }
        
    } catch {
        Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "  No test images found in storage/hot" -ForegroundColor Yellow
    Write-Host "  Skipping job creation test" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "API tests complete" -ForegroundColor Cyan
Write-Host ""



