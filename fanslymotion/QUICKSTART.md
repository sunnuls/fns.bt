# Quick Start Guide

Get FanslyMotion up and running in **5 minutes**!

## Prerequisites Checklist

- [ ] Windows 10/11
- [ ] Python 3.10 or higher
- [ ] NVIDIA GPU (RTX series)
- [ ] Redis Server
- [ ] Telegram Bot Token

## Installation Steps

### 1. Get a Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. Copy the bot token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Install Redis (if not already installed)

**Option A: Download directly**
- Visit: https://github.com/microsoftarchive/redis/releases
- Download `Redis-x64-*.zip`
- Extract and run `redis-server.exe`

**Option B: Using Docker**
```powershell
docker run -d -p 6379:6379 redis
```

### 3. Setup FanslyMotion

Open PowerShell and navigate to the project folder:

```powershell
cd fanslymotion
```

**Important:** Make sure you're in the `fanslymotion` folder, not `fns_bot`.

### 4. Configure Environment

```powershell
# Copy the example environment file
copy env.example .env

# Edit the .env file
notepad .env
```

Replace `your_telegram_bot_token_here` with your actual bot token from step 1.

### 5. Run the Setup Script

```powershell
.\run_local.ps1
```

This will:
- Create virtual environment
- Install all dependencies (~10 minutes first time)
- Create storage directories
- Launch all services

### 6. First Run Notes

**Model Download**: On first run, the system will download the SVD model (~10GB). This takes 10-30 minutes depending on your internet speed. The model is cached for future use.

**Services**: The script opens 4 PowerShell windows:
1. FastAPI Backend (port 8000)
2. RQ Worker (GPU processing)
3. Telegram Bot
4. Launcher (this window)

## Using the Bot

1. Open Telegram and find your bot
2. Send `/start`
3. Click "📸 photo→video 🎦"
4. Follow the prompts:
   - Select duration (3-12 seconds)
   - Choose resolution (360p-1080p)
   - Pick motion preset
   - Upload a photo
5. Wait for processing (1-3 minutes)
6. Receive your video!

## Testing Your Setup

Run the verification script:

```powershell
python test_setup.py
```

This checks:
- ✅ All Python packages installed
- ✅ CUDA availability
- ✅ Redis connection
- ✅ Storage directories
- ✅ Environment configuration

## Common Issues

### "CUDA not available"
- Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
- Restart your computer after installation
- Verify with: `nvidia-smi`

### "Redis connection failed"
- Ensure Redis is running: `redis-cli ping` should return "PONG"
- Check if port 6379 is available
- Try restarting Redis: `redis-server`

### "Bot not responding"
- Verify bot token in `.env` is correct
- Check if bot service is running (green window)
- Look for errors in bot window

### "Out of memory"
- Use lower resolution (360p or 480p)
- Close other GPU applications
- Your GPU may have insufficient VRAM

## Performance Tips

### For RTX 4090 / High-end GPUs:
- Use 1080p for best quality
- Expect ~60-90 seconds per video

### For RTX 3060-3080 / Mid-range GPUs:
- Use 720p for balanced quality/speed
- Expect ~90-120 seconds per video

### For RTX 3050 / Entry-level GPUs:
- Use 480p or 360p
- Expect ~120-180 seconds per video

## File Locations

- **Generated Videos**: `storage/hot/`
- **Model Cache**: `cache/models/`
- **Logs**: Check service windows
- **Config**: `.env` file

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Customize motion presets in `config.py`
- Add custom features in `bot/handlers.py`
- Deploy to cloud (see README for guides)

## Getting Help

If you encounter issues:
1. Check the service windows for error messages
2. Run `python test_setup.py` to diagnose
3. Review README.md troubleshooting section
4. Check GPU memory with: `nvidia-smi`

## Stopping Services

To stop all services:
- Close all PowerShell windows
- Or press `Ctrl+C` in each service window

---

**Happy video generation! 🎬✨**

