# Check failed job details
param(
    [string]$jobId = "331ca5a0-0ded-4e2c-a4dc-6b55c81b7482"
)

Write-Host "Checking failed job: $jobId" -ForegroundColor Cyan
Write-Host ""

# Get job status from API
Write-Host "Job Status from API:" -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "http://localhost:8000/job/status/$jobId" -Method Get
    Write-Host "  Status: $($status.status)" -ForegroundColor Gray
    Write-Host "  Created: $($status.created_at)" -ForegroundColor Gray
    if ($status.started_at) {
        Write-Host "  Started: $($status.started_at)" -ForegroundColor Gray
    }
    if ($status.error) {
        Write-Host "  Error: $($status.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "  Failed to get status: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Check Redis for job metadata
Write-Host "Job Metadata from Redis:" -ForegroundColor Yellow
$metadata = .\redis\redis-cli.exe GET "job:${jobId}:metadata"
if ($metadata) {
    Write-Host $metadata -ForegroundColor Gray
} else {
    Write-Host "  No metadata found" -ForegroundColor Red
}

Write-Host ""

# Check failed queue
Write-Host "Failed Jobs Queue:" -ForegroundColor Yellow
$failedCount = .\redis\redis-cli.exe LLEN "rq:queue:failed"
Write-Host "  Total failed jobs: $failedCount" -ForegroundColor Gray

if ([int]$failedCount -gt 0) {
    Write-Host ""
    Write-Host "  Last failed job details:" -ForegroundColor Yellow
    $failedJob = .\redis\redis-cli.exe LRANGE "rq:queue:failed" 0 0
    Write-Host $failedJob -ForegroundColor Gray
}

Write-Host ""



