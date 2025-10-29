# Debug script for bot startup
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Starting FanslyMotion Bot (Debug Mode)" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check Python
Write-Host "`n[1/5] Checking Python..." -ForegroundColor Yellow
python --version

# Check imports
Write-Host "`n[2/5] Checking imports..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, '.'); from config import settings; print('✅ Config imported'); from bot.handlers import router; print('✅ Handlers imported')" 2>&1

# Check bot token
Write-Host "`n[3/5] Checking bot token..." -ForegroundColor Yellow
python -c "from config import settings; print('BOT_TOKEN:', 'SET ✅' if settings.bot_token else 'NOT SET ❌')" 2>&1

# Check Redis
Write-Host "`n[4/5] Checking Redis..." -ForegroundColor Yellow
python -c "import redis; r = redis.Redis(); print('Redis:', 'OK ✅' if r.ping() else 'FAILED ❌')" 2>&1

# Start bot
Write-Host "`n[5/5] Starting bot..." -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
python -m bot.bot

