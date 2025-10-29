# FanslyMotion Setup Checklist

Use this checklist to ensure everything is properly configured before running the system.

## ✅ Pre-Installation Checklist

### System Requirements
- [ ] Windows 10 or 11 installed
- [ ] Python 3.10+ installed (`python --version`)
- [ ] NVIDIA GPU present (check Device Manager)
- [ ] CUDA Toolkit installed (`nvidia-smi` command works)
- [ ] At least 20GB free disk space
- [ ] At least 16GB RAM

### Required Software
- [ ] Python 3.10+ - [Download](https://www.python.org/downloads/)
- [ ] Redis Server - [Download](https://github.com/microsoftarchive/redis/releases)
- [ ] Git (optional) - [Download](https://git-scm.com/downloads)
- [ ] CUDA Toolkit - [Download](https://developer.nvidia.com/cuda-downloads)

### Telegram Bot Setup
- [ ] Opened Telegram and searched for `@BotFather`
- [ ] Sent `/newbot` command
- [ ] Chose a name for your bot
- [ ] Chose a username for your bot (must end in 'bot')
- [ ] Copied the bot token (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
- [ ] Saved token securely (you'll need it later)

## ✅ Installation Checklist

### Step 1: Project Setup
- [ ] Navigated to `fanslymotion` directory
- [ ] Verified all files are present (see PROJECT_TREE.txt)
- [ ] Opened PowerShell in the project directory

### Step 2: Environment Configuration
- [ ] Copied `env.example` to `.env`: `copy env.example .env`
- [ ] Opened `.env` file: `notepad .env`
- [ ] Replaced `your_telegram_bot_token_here` with actual token
- [ ] Verified other settings (defaults should work)
- [ ] Saved and closed `.env` file

### Step 3: Redis Setup
- [ ] Downloaded Redis (if not already installed)
- [ ] Extracted Redis to a folder
- [ ] Started Redis: `redis-server.exe`
- [ ] Verified Redis is running: `redis-cli ping` returns "PONG"
- [ ] Left Redis running in background

### Step 4: Python Environment
- [ ] Created virtual environment: `python -m venv venv`
- [ ] Activated virtual environment: `.\venv\Scripts\Activate.ps1`
- [ ] Upgraded pip: `python -m pip install --upgrade pip`
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Waited for installation to complete (may take 10-15 minutes)

### Step 5: Directory Structure
- [ ] Created storage directories (or let script do it):
  - [ ] `mkdir storage\hot`
  - [ ] `mkdir storage\archive`
  - [ ] `mkdir cache\torch`
  - [ ] `mkdir cache\models`

### Step 6: Verification
- [ ] Ran test script: `python test_setup.py`
- [ ] All import tests passed ✅
- [ ] CUDA is available ✅
- [ ] Redis connection successful ✅
- [ ] Directories exist ✅
- [ ] Environment configured ✅

## ✅ First Run Checklist

### Using PowerShell Script (Recommended)
- [ ] Ran `.\run_local.ps1`
- [ ] Script created virtual environment (if needed)
- [ ] Script installed dependencies (if needed)
- [ ] Script started Redis check
- [ ] Script opened 4 PowerShell windows:
  - [ ] Backend (green) - Running on port 8000
  - [ ] Worker (yellow) - Connected to Redis
  - [ ] Bot (cyan) - Bot started successfully
  - [ ] Launcher (white) - Shows summary

### Manual Start (Alternative)
If using manual start instead:
- [ ] Terminal 1: Started backend: `python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000`
- [ ] Terminal 2: Started worker: `python worker/worker.py`
- [ ] Terminal 3: Started bot: `python bot/bot.py`
- [ ] All services running without errors

### Service Verification
- [ ] Backend accessible: Opened http://localhost:8000 in browser
- [ ] API docs accessible: Opened http://localhost:8000/docs
- [ ] Health check passed: http://localhost:8000/health shows "healthy"
- [ ] Worker connected to Redis (check worker logs)
- [ ] Bot logged "Bot started" message

## ✅ First Generation Test

### Telegram Bot Test
- [ ] Opened Telegram and found your bot
- [ ] Sent `/start` command
- [ ] Bot responded with welcome message
- [ ] Main menu displayed with "📸 photo→video 🎦" button
- [ ] Clicked "📸 photo→video 🎦"
- [ ] Duration selection screen appeared

### Generation Flow Test
- [ ] Selected duration: **6 seconds** (recommended for first test)
- [ ] Selected resolution: **480p** (faster for testing)
- [ ] Selected motion preset: **micro** (subtle motion)
- [ ] Bot prompted for photo upload
- [ ] Uploaded a test photo (clear, well-lit image recommended)
- [ ] Bot acknowledged photo upload
- [ ] Job creation message appeared with job ID
- [ ] Progress updates started appearing
- [ ] Queue position showed (if applicable)
- [ ] Progress bar updated (0% → 100%)
- [ ] Video generation completed
- [ ] Received MP4 video file
- [ ] Video plays correctly
- [ ] Video shows motion effect

### First Run Notes
- [ ] Noted model download time (10-30 minutes first time)
- [ ] Checked GPU utilization (nvidia-smi)
- [ ] Verified video quality
- [ ] Total time recorded: _______ seconds

## ✅ Troubleshooting Checklist

If something doesn't work, check:

### Bot Issues
- [ ] Bot token is correct in `.env`
- [ ] Bot service is running (check cyan window)
- [ ] No error messages in bot log
- [ ] Backend is accessible from bot
- [ ] Network/firewall not blocking

### Backend Issues
- [ ] Port 8000 is not in use by another app
- [ ] Redis connection successful
- [ ] No import errors in backend log
- [ ] Can access http://localhost:8000

### Worker Issues
- [ ] CUDA is available (`nvidia-smi` works)
- [ ] GPU has enough VRAM (8GB minimum)
- [ ] Model cache directory is writable
- [ ] No other GPU processes running
- [ ] Worker connected to Redis

### Redis Issues
- [ ] Redis server is running
- [ ] Port 6379 is available
- [ ] `redis-cli ping` returns "PONG"
- [ ] Redis URL is correct in `.env`

### Generation Issues
- [ ] Image file is valid format (PNG, JPG)
- [ ] Image file size < 10MB
- [ ] Selected valid resolution/duration
- [ ] GPU has enough memory for resolution
- [ ] Check worker logs for errors

## ✅ Performance Optimization Checklist

### GPU Optimization
- [ ] Closed other GPU applications (games, browsers)
- [ ] Verified GPU temperature is normal
- [ ] Checked VRAM usage with `nvidia-smi`
- [ ] Started with lower resolution (480p) for testing
- [ ] Upgraded to higher resolution if GPU can handle it

### System Optimization
- [ ] Installed dependencies on SSD (faster loading)
- [ ] Sufficient RAM available (16GB+ recommended)
- [ ] Model cache on fast storage
- [ ] Close unnecessary background apps

### Queue Management
- [ ] Set appropriate `WORKER_MAX_JOBS` in `.env`
- [ ] Monitor queue length via health endpoint
- [ ] Adjust based on GPU capabilities

## ✅ Production Deployment Checklist

If deploying to production:

### Security
- [ ] Changed default passwords/tokens
- [ ] Enabled HTTPS/TLS
- [ ] Configured firewall rules
- [ ] Set up rate limiting
- [ ] Implemented authentication
- [ ] Regular security updates scheduled

### Monitoring
- [ ] Set up logging aggregation
- [ ] Configured health check monitoring
- [ ] Set up alerting (email/SMS)
- [ ] Monitor GPU temperature/usage
- [ ] Track queue length and job success rate

### Backup
- [ ] Automated Redis backups configured
- [ ] Storage backup strategy in place
- [ ] Configuration files backed up
- [ ] Recovery procedure documented
- [ ] Backup restoration tested

### Scaling
- [ ] Identified bottlenecks
- [ ] Planned scaling strategy (vertical/horizontal)
- [ ] Load testing performed
- [ ] Auto-scaling configured (if applicable)

### Documentation
- [ ] Updated README with deployment-specific info
- [ ] Documented any custom configurations
- [ ] Created runbook for operations team
- [ ] Documented troubleshooting procedures

## ✅ Maintenance Checklist

### Daily Tasks
- [ ] Check service health
- [ ] Monitor queue length
- [ ] Review error logs
- [ ] Verify GPU temperature

### Weekly Tasks
- [ ] Clear old job data
- [ ] Check disk space
- [ ] Review performance metrics
- [ ] Update dependencies (if needed)

### Monthly Tasks
- [ ] Full system backup
- [ ] Security updates
- [ ] Review and optimize configuration
- [ ] Capacity planning review

## 📝 Notes Section

Use this space to record important information:

**Bot Token**: `____________________________________`

**Redis URL**: `____________________________________`

**Backend URL**: `____________________________________`

**GPU Model**: `____________________________________`

**VRAM**: `____________________________________`

**First Generation Time**: `____________________________________`

**Average Generation Time**: `____________________________________`

**Issues Encountered**:
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

**Custom Configurations**:
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

## 🎉 Completion

When all items are checked:
- ✅ System is fully operational
- ✅ First video generated successfully
- ✅ All services running smoothly
- ✅ Ready for production use

**Congratulations! Your FanslyMotion system is ready! 🎬✨**

---

**Need Help?**
- Check README.md for detailed documentation
- Run `python test_setup.py` for diagnostics
- Review logs in service windows
- See TROUBLESHOOTING section in README.md

