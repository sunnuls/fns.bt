# FanslyMotion Local Startup Script (ASCII-safe version)
# This script launches all required services for local development

Write-Host ">>> FanslyMotion Local Startup Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path "env")) {
    Write-Host "WARNING: env file not found!" -ForegroundColor Yellow
    Write-Host "Please create env file with BOT_TOKEN and other settings" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if Redis is running
Write-Host "Checking Redis..." -ForegroundColor Cyan
$redisRunning = Get-Process redis-server -ErrorAction SilentlyContinue

if (-not $redisRunning) {
    Write-Host "WARNING: Redis not running" -ForegroundColor Yellow
    Write-Host "Attempting to start Redis..." -ForegroundColor Gray
    
    # Try to start Redis
    try {
        Start-Process "redis-server" -WindowStyle Minimized -ErrorAction Stop
        Write-Host "OK: Redis started" -ForegroundColor Green
        Start-Sleep -Seconds 2
    }
    catch {
        Write-Host "ERROR: Failed to start Redis automatically" -ForegroundColor Red
        Write-Host "Please install Redis or start it manually" -ForegroundColor Yellow
        Write-Host "  - Download: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Gray
        Write-Host "  - Or use WSL: wsl sudo service redis-server start" -ForegroundColor Gray
        Write-Host ""
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 1
        }
    }
}
else {
    Write-Host "OK: Redis is running" -ForegroundColor Green
}

Write-Host ""

# Create necessary directories
Write-Host "Creating storage directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "storage/hot" | Out-Null
New-Item -ItemType Directory -Force -Path "storage/archive" | Out-Null
New-Item -ItemType Directory -Force -Path "cache/torch" | Out-Null
New-Item -ItemType Directory -Force -Path "cache/models" | Out-Null
New-Item -ItemType Directory -Force -Path "C:/AI-cache/huggingface" | Out-Null
New-Item -ItemType Directory -Force -Path "C:/AI-cache/torch" | Out-Null
Write-Host "OK: Storage directories created" -ForegroundColor Green
Write-Host ""

# Check if Python virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "OK: Virtual environment created" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"
Write-Host "OK: Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Cyan
$needsInstall = $false
try {
    & python -c "import fastapi, aiogram, redis, torch, diffusers" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { $needsInstall = $true }
} catch {
    $needsInstall = $true
}

if ($needsInstall) {
    Write-Host "Installing dependencies (this may take 10-15 minutes)..." -ForegroundColor Cyan
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt
    Write-Host "OK: Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "OK: Dependencies already installed" -ForegroundColor Green
}
Write-Host ""

# Function to start a service in a new window
function Start-Service {
    param(
        [string]$Name,
        [string]$Command,
        [string]$Color = "White"
    )
    
    Write-Host ">>> Starting $Name..." -ForegroundColor $Color
    $activateCmd = "Set-Location '$PWD'; & '.\venv\Scripts\Activate.ps1'"
    $fullCmd = "$activateCmd; Write-Host '>>> $Name Running' -ForegroundColor $Color; $Command; Write-Host ''; Write-Host 'Process ended. Press Enter to close.' -ForegroundColor Gray; Read-Host"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $fullCmd
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host ">>> Launching Services..." -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

# Start FastAPI Backend
Start-Service -Name "FastAPI Backend" -Command "python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload" -Color "Green"

# Start RQ Worker
Start-Service -Name "RQ Worker (GPU)" -Command "python worker/worker.py" -Color "Yellow"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start Telegram Bot
Start-Service -Name "Telegram Bot" -Command "python bot/bot.py" -Color "Cyan"

Write-Host ""
Write-Host "OK: All services started!" -ForegroundColor Green
Write-Host ""
Write-Host ">>> Service Status:" -ForegroundColor Cyan
Write-Host "  * FastAPI Backend: http://localhost:8000" -ForegroundColor White
Write-Host "  * API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  * Telegram Bot: Running" -ForegroundColor White
Write-Host "  * RQ Worker: Running" -ForegroundColor White
Write-Host ""
Write-Host ">>> Tips:" -ForegroundColor Cyan
Write-Host "  * Check backend logs for API requests" -ForegroundColor Gray
Write-Host "  * Monitor worker logs for GPU processing" -ForegroundColor Gray
Write-Host "  * Bot logs show user interactions" -ForegroundColor Gray
Write-Host ""
Write-Host ">>> To stop all services:" -ForegroundColor Yellow
Write-Host "  * Close all PowerShell windows" -ForegroundColor Gray
Write-Host "  * Or press Ctrl+C in each window" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit this launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

