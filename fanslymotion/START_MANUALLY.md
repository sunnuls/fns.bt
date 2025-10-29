# Manual Start Instructions

If the PowerShell launcher fails, start each service manually in separate terminals.

## Prerequisites

1. **Redis must be running** on port 6379
   - Download: https://github.com/microsoftarchive/redis/releases
   - Run: `redis-server.exe`
   - Or via WSL: `wsl sudo service redis-server start`

2. **Virtual environment activated**
   ```powershell
   cd C:\fns_bot\fanslymotion
   .\venv\Scripts\Activate.ps1
   ```

3. **Environment file exists** (`env` with BOT_TOKEN configured)

## Start Services (3 terminals)

### Terminal 1: FastAPI Backend
```powershell
cd C:\fns_bot\fanslymotion
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test:** Open http://localhost:8000/docs

### Terminal 2: RQ Worker
```powershell
cd C:\fns_bot\fanslymotion
.\venv\Scripts\Activate.ps1
python worker/worker.py
```

**Expected output:**
```
Starting RQ Worker for video generation...
Connected to Redis: localhost:6379
Queue: svd_jobs
Timeout: 300s
```

### Terminal 3: Telegram Bot
```powershell
cd C:\fns_bot\fanslymotion
.\venv\Scripts\Activate.ps1
python bot/bot.py
```

**Expected output:**
```
INFO - Starting FanslyMotion Telegram Bot...
INFO - Backend URL: http://localhost:8000
```

## Verification

1. **Backend**: Visit http://localhost:8000/health
   - Should return `{"status": "healthy"}`

2. **Bot**: Send `/start` to your Telegram bot
   - Should receive welcome message

3. **Worker**: Check terminal for connection status
   - Should show "Connected to Redis"

## Common Issues

### "Redis connection failed"
- Start Redis: `redis-server.exe`
- Check port: `redis-cli ping` should return "PONG"

### "ModuleNotFoundError"
- Install deps: `pip install -r requirements.txt`

### "CUDA not available"
- Check GPU: `nvidia-smi`
- Install CUDA Toolkit
- Reinstall PyTorch: `pip install torch==2.3.1 torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cu121`

### "Bot token invalid"
- Edit `env` file
- Set `BOT_TOKEN=your_actual_token`

