# Start bot with full monitoring
Write-Host "Starting bot with monitoring..." -ForegroundColor Cyan

# Stop old bots
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $proc = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue
        if ($proc -and $proc.CommandLine -like "*bot.bot*") {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    } catch {}
}
Start-Sleep -Seconds 2

# Start bot with output redirection
$logFile = "bot_runtime.log"
Write-Host "Starting bot, output will be saved to: $logFile" -ForegroundColor Yellow

$botCmd = @"
cd '$PWD'
`$host.ui.RawUI.WindowTitle = 'FanslyMotion Bot [MONITORED]'
Write-Host '=== BOT STARTING ===' -ForegroundColor Cyan
python -u -m bot.bot *>&1 | Tee-Object -FilePath '$logFile'
Write-Host '`nBot stopped. Log saved to: $logFile' -ForegroundColor Gray
Write-Host 'Press Enter to close...' -ForegroundColor Gray
Read-Host
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $botCmd
Start-Sleep -Seconds 3

Write-Host "`n✅ Bot started!" -ForegroundColor Green
Write-Host "Check window 'FanslyMotion Bot [MONITORED]' or log file: $logFile" -ForegroundColor Yellow

