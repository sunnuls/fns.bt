# Fix bot startup issues
Write-Host "Diagnosing bot startup..." -ForegroundColor Cyan

# Stop any existing bot processes
Write-Host "`n[1] Stopping existing bot processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $proc = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue
        if ($proc -and $proc.CommandLine -like "*bot.bot*") {
            Write-Host "   Stopping PID $($_.Id)..."
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    } catch {}
}
Start-Sleep -Seconds 2

# Test imports
Write-Host "`n[2] Testing imports..." -ForegroundColor Yellow
python -c "from aiogram import Bot; print('✅ aiogram OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ aiogram import failed!" -ForegroundColor Red
    exit 1
}

# Test bot token
Write-Host "`n[3] Testing bot token..." -ForegroundColor Yellow
python -c "from config import settings; print('✅ BOT_TOKEN:', 'SET' if settings.bot_token else 'NOT SET')" 2>&1

# Start bot in new window with explicit output
Write-Host "`n[4] Starting bot in new window..." -ForegroundColor Yellow
$botCmd = @"
`$ErrorActionPreference = 'Continue'
cd '$PWD'
Write-Host '=== BOT STARTUP ===' -ForegroundColor Cyan
python -u -m bot.bot
Write-Host '`nBot process ended. Press Enter to close.' -ForegroundColor Gray
Read-Host
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $botCmd
Write-Host "✅ Bot window should open now." -ForegroundColor Green
Write-Host "`nWatch that window for startup messages!" -ForegroundColor Yellow

