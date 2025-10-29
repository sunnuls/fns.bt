# Quick bot status check
Write-Host "Checking Bot Status..." -ForegroundColor Cyan

# Check if bot process is running
$botRunning = $false
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $proc = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue
        if ($proc -and $proc.CommandLine -like "*bot.bot*") {
            Write-Host "Bot process found: PID $($_.Id)" -ForegroundColor Green
            $script:botRunning = $true
        }
    } catch {}
}

if (-not $botRunning) {
    Write-Host "Bot is NOT running!" -ForegroundColor Red
    Write-Host "Starting bot..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; `$host.ui.RawUI.WindowTitle = 'FanslyMotion Bot'; python -m bot.bot"
    Start-Sleep -Seconds 3
    Write-Host "Bot started!" -ForegroundColor Green
} else {
    Write-Host "Bot is running" -ForegroundColor Green
}

# Test bot connection
Write-Host "`nTesting bot connection..." -ForegroundColor Cyan
python -c "from config import settings; print('BOT_TOKEN:', 'SET' if settings.bot_token else 'NOT SET')" 2>&1

Write-Host "`nCheck the 'FanslyMotion Bot' window for logs" -ForegroundColor Yellow
Write-Host "In Telegram, send /start to @LunaMotionBot" -ForegroundColor Yellow

