# Quick Start Script for FanslyMotion v2.0
# This script checks system requirements and starts the bot

$ErrorActionPreference = "Stop"

Write-Host "🚀 FanslyMotion v2.0 - Quick Start" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "🐍 Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Check virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    Write-Host "   ✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Virtual environment not found" -ForegroundColor Yellow
    Write-Host "   Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    Write-Host "   ✅ Virtual environment created and activated" -ForegroundColor Green
}

# Check if requirements are installed
Write-Host ""
Write-Host "📚 Checking dependencies..." -ForegroundColor Yellow
$torchInstalled = python -c "import torch" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ℹ️  Installing dependencies (this may take a while)..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    # Install xformers separately
    Write-Host "   ⚡ Installing xformers for maximum performance..." -ForegroundColor Yellow
    pip install xformers==0.0.23
    
    Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ✅ Dependencies already installed" -ForegroundColor Green
    
    # Check if xformers is installed
    $xformersInstalled = python -c "import xformers" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ⚠️  xformers not found - installing for 2x speedup..." -ForegroundColor Yellow
        pip install xformers==0.0.23
    } else {
        Write-Host "   ✅ xformers available (2x performance boost)" -ForegroundColor Green
    }
}

# Check CUDA
Write-Host ""
Write-Host "🎮 Checking CUDA..." -ForegroundColor Yellow
$cudaCheck = python -c "import torch; print(torch.cuda.is_available())" 2>&1
if ($cudaCheck -eq "True") {
    $gpuName = python -c "import torch; print(torch.cuda.get_device_name(0))" 2>&1
    $gpuMemory = python -c "import torch; print(f'{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}')" 2>&1
    Write-Host "   ✅ CUDA available" -ForegroundColor Green
    Write-Host "   GPU: $gpuName" -ForegroundColor Green
    Write-Host "   VRAM: $gpuMemory GB" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  CUDA not available - running on CPU (will be slow)" -ForegroundColor Yellow
}

# Check .env file
Write-Host ""
Write-Host "⚙️  Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ✅ .env file found" -ForegroundColor Green
    
    # Check if BOT_TOKEN is set
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "BOT_TOKEN=.+") {
        if ($envContent -notmatch "BOT_TOKEN=your_telegram_bot_token") {
            Write-Host "   ✅ BOT_TOKEN configured" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  BOT_TOKEN not set!" -ForegroundColor Yellow
            Write-Host "   Please edit .env and add your Telegram bot token" -ForegroundColor Yellow
            Write-Host ""
            $continue = Read-Host "Continue anyway? (y/n)"
            if ($continue -ne "y") {
                exit 1
            }
        }
    }
} else {
    Write-Host "   ⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "   Creating from template..." -ForegroundColor Yellow
    
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Host "   ✅ .env created from env.example" -ForegroundColor Green
        Write-Host "   ⚠️  Please edit .env and add your BOT_TOKEN" -ForegroundColor Yellow
        notepad .env
        Write-Host ""
        Write-Host "Press Enter after saving the .env file..." -ForegroundColor Yellow
        Read-Host
    } else {
        Write-Host "   Creating default .env..." -ForegroundColor Yellow
        @"
BOT_TOKEN=your_telegram_bot_token_here
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_URL=http://localhost:8000
CUDA_VISIBLE_DEVICES=0
"@ | Out-File -FilePath ".env" -Encoding utf8
        Write-Host "   ✅ .env created" -ForegroundColor Green
        Write-Host "   ⚠️  Please edit .env and add your BOT_TOKEN" -ForegroundColor Yellow
        notepad .env
        Write-Host ""
        Write-Host "Press Enter after saving the .env file..." -ForegroundColor Yellow
        Read-Host
    }
}

# Create directories
Write-Host ""
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
$dirs = @("storage\hot", "storage\archive", "cache\models", "cache\torch", "cache\huggingface")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   ✅ Created: $dir" -ForegroundColor Green
    }
}

# Check Redis
Write-Host ""
Write-Host "🔴 Checking Redis..." -ForegroundColor Yellow
$redisRunning = $false
try {
    $redis = python -c "import redis; r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=2); r.ping(); print('OK')" 2>&1
    if ($redis -eq "OK") {
        Write-Host "   ✅ Redis is running" -ForegroundColor Green
        $redisRunning = $true
    }
} catch {
    Write-Host "   ⚠️  Redis not running" -ForegroundColor Yellow
}

if (-not $redisRunning) {
    Write-Host "   Starting Redis..." -ForegroundColor Yellow
    if (Test-Path "redis\redis-server.exe") {
        Start-Process -FilePath "redis\redis-server.exe" -WindowStyle Minimized
        Start-Sleep -Seconds 2
        Write-Host "   ✅ Redis started" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Redis not found in redis\ directory" -ForegroundColor Yellow
        Write-Host "   Please install Redis and start it manually" -ForegroundColor Yellow
        Write-Host "   See: REDIS_QUICK_INSTALL_RU.md" -ForegroundColor Yellow
        Write-Host ""
        $continue = Read-Host "Continue without Redis? (y/n)"
        if ($continue -ne "y") {
            exit 1
        }
    }
}

# Run system check
Write-Host ""
Write-Host "🔍 Running system check..." -ForegroundColor Yellow
Write-Host ""
python check_system.py

# Ask to start services
Write-Host ""
Write-Host "🚀 Ready to start FanslyMotion!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Available options:" -ForegroundColor Yellow
Write-Host "  1. Start all services (Backend + Worker + Bot)" -ForegroundColor White
Write-Host "  2. Start Backend only" -ForegroundColor White
Write-Host "  3. Start Worker only" -ForegroundColor White
Write-Host "  4. Start Bot only" -ForegroundColor White
Write-Host "  5. Run test generation" -ForegroundColor White
Write-Host "  6. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Select option (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚀 Starting all services..." -ForegroundColor Cyan
        Write-Host ""
        
        # Start backend
        Write-Host "Starting Backend..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.ui.RawUI.WindowTitle = 'FanslyMotion Backend'; cd '$PWD'; python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 }"
        Start-Sleep -Seconds 3
        
        # Start worker
        Write-Host "Starting Worker..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.ui.RawUI.WindowTitle = 'FanslyMotion Worker'; cd '$PWD'; python -m rq worker --url redis://localhost:6379/0 svd_jobs }"
        Start-Sleep -Seconds 2
        
        # Start bot
        Write-Host "Starting Bot..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.ui.RawUI.WindowTitle = 'FanslyMotion Bot'; cd '$PWD'; python -m bot.bot }"
        
        Write-Host ""
        Write-Host "✅ All services started!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Monitor services in the new windows" -ForegroundColor Yellow
        Write-Host "API available at: http://localhost:8000" -ForegroundColor Yellow
    }
    "2" {
        Write-Host "Starting Backend..." -ForegroundColor Yellow
        python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
    }
    "3" {
        Write-Host "Starting Worker..." -ForegroundColor Yellow
        python -m rq worker --url redis://localhost:6379/0 svd_jobs
    }
    "4" {
        Write-Host "Starting Bot..." -ForegroundColor Yellow
        python -m bot.bot
    }
    "5" {
        Write-Host "Running test generation..." -ForegroundColor Yellow
        if (Test-Path "test_setup.py") {
            python test_setup.py
        } else {
            Write-Host "test_setup.py not found" -ForegroundColor Red
        }
    }
    "6" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host "Invalid option" -ForegroundColor Red
        exit 1
    }
}

