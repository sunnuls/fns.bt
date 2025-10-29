# FanslyMotion - AI Photo to Video Generator

Transform static photos into dynamic videos using **Stable Video Diffusion (SVD-XT)** model. A complete system with Telegram bot, FastAPI backend, Redis queue, and GPU-accelerated worker.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Features

- **📸 Photo-to-Video Transformation**: Turn any photo into a short video with realistic motion
- **🎬 Multiple Motion Presets**: 6 different motion styles (micro, pan, tilt, dolly)
- **📺 Multiple Resolutions**: Support for 360p, 480p, 720p, and 1080p output
- **⏱️ Flexible Duration**: Choose from 3, 6, 8, 10, or 12-second videos
- **🤖 Telegram Bot Interface**: User-friendly interaction with aiogram 3
- **⚡ GPU Acceleration**: CUDA-optimized for RTX GPUs
- **📊 Job Queue System**: Redis RQ for reliable job processing
- **🔄 Progress Tracking**: Real-time updates with progress bars

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Telegram   │─────▶│   FastAPI    │─────▶│    Redis    │
│     Bot     │      │   Backend    │      │    Queue    │
└─────────────┘      └──────────────┘      └─────────────┘
                              │                     │
                              │                     ▼
                              │              ┌─────────────┐
                              │              │  RQ Worker  │
                              │              │  (GPU)      │
                              │              └─────────────┘
                              │                     │
                              ▼                     ▼
                     ┌─────────────────────────────────┐
                     │    Storage (hot/archive)        │
                     └─────────────────────────────────┘
```

### Components

1. **Telegram Bot** (`bot/`)
   - User interaction layer using aiogram 3
   - FSM-based conversation flow
   - Progress updates and result delivery

2. **FastAPI Backend** (`backend/`)
   - REST API endpoints for job management
   - `/job/create` - Submit new jobs
   - `/job/status/{id}` - Check progress
   - `/job/result/{id}` - Get video results

3. **RQ Worker** (`worker/`)
   - GPU-accelerated video generation
   - Processes jobs from Redis queue
   - Handles retries and timeouts

4. **SVD Renderer** (`svd/`)
   - Stable Video Diffusion pipeline
   - CUDA half-precision inference
   - Motion preset configurations

## 🚀 Quick Start

### Prerequisites

- **Windows 10/11** (tested on Windows 11)
- **Python 3.10+**
- **NVIDIA GPU** with CUDA support (RTX series recommended)
- **Redis Server** ([Download](https://github.com/microsoftarchive/redis/releases))
- **Telegram Bot Token** (get from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone or navigate to the project folder**:
   ```powershell
   cd fanslymotion
   ```

2. **Configure environment**:
   ```powershell
   # Copy the example environment file
   copy .env.example .env
   
   # Edit .env and add your Telegram bot token
   notepad .env
   ```

3. **Run the setup script**:
   ```powershell
   .\run_local.ps1
   ```

   This script will:
   - Check for Redis
   - Create virtual environment
   - Install dependencies
   - Create storage directories
   - Launch all services

### Manual Setup (Alternative)

If you prefer manual setup:

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create storage directories
mkdir storage\hot
mkdir storage\archive
mkdir cache\torch
mkdir cache\models

# Start Redis (in separate terminal)
redis-server

# Start FastAPI backend (in separate terminal)
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000

# Start RQ worker (in separate terminal)
python worker/worker.py

# Start Telegram bot (in separate terminal)
python bot/bot.py
```

## 📋 Configuration

### Environment Variables

Edit `.env` file with your settings:

```ini
# Telegram Configuration
BOT_TOKEN=your_bot_token_here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_URL=http://localhost:8000

# Storage Configuration
STORAGE_HOT_PATH=./storage/hot
STORAGE_ARCHIVE_PATH=./storage/archive

# GPU Configuration
CUDA_VISIBLE_DEVICES=0

# Model Configuration
SVD_MODEL_ID=stabilityai/stable-video-diffusion-img2vid-xt
SVD_MODEL_CACHE=./cache/models
```

### Technical Parameters

Default video generation settings (configured in `config.py`):

- **FPS**: 12 frames per second
- **Steps**: 24 inference steps
- **Guidance Scale**: 1.0
- **Noise Augmentation**: 0.1
- **Precision**: FP16 (half precision)
- **Queue Limit**: 10 concurrent jobs
- **Timeout**: 60 seconds per job
- **Retries**: 3 attempts with 40s delay

## 🎯 Usage

### Telegram Bot Flow

1. **Start the bot**: Send `/start` to your bot
2. **Select "📸 photo→video 🎦"**
3. **Choose duration**: 3, 6, 8, 10, or 12 seconds
4. **Select resolution**: 360p, 480p, 720p, or 1080p
5. **Pick motion preset**:
   - 🔍 **Micro**: Subtle micro-movements
   - ⬅️ **Pan Left**: Horizontal left motion
   - ➡️ **Pan Right**: Horizontal right motion
   - ⬆️ **Tilt Up**: Vertical upward motion
   - ⬇️ **Tilt Down**: Vertical downward motion
   - 🔎 **Dolly In**: Zoom-in effect
6. **Upload photo**: Send a high-quality image
7. **Wait for processing**: Progress bar updates in real-time
8. **Receive video**: Download your generated MP4

### API Usage

#### Create Job

```bash
POST http://localhost:8000/job/create
Content-Type: application/json

{
  "user_id": 123456789,
  "image_data": "base64_encoded_image_data",
  "duration": 6,
  "resolution": "720p",
  "motion_preset": "pan_l"
}
```

#### Check Status

```bash
GET http://localhost:8000/job/status/{job_id}
```

#### Get Result

```bash
GET http://localhost:8000/job/result/{job_id}
```

#### Download Video

```bash
GET http://localhost:8000/job/download/{job_id}
```

## 📁 Project Structure

```
fanslymotion/
├── bot/                    # Telegram bot module
│   ├── __init__.py
│   ├── bot.py             # Main bot entry point
│   ├── handlers.py        # Message and callback handlers
│   ├── keyboards.py       # Inline keyboard builders
│   └── states.py          # FSM states
│
├── backend/               # FastAPI backend
│   ├── __init__.py
│   ├── app.py            # FastAPI application
│   └── models.py         # Pydantic models
│
├── worker/               # RQ worker for processing
│   ├── __init__.py
│   ├── worker.py         # Worker entry point
│   └── tasks.py          # Job processing tasks
│
├── svd/                  # SVD rendering module
│   ├── __init__.py
│   └── renderer.py       # Video generation logic
│
├── storage/              # Local storage
│   ├── hot/             # Active job files
│   └── archive/         # Completed job archives
│
├── cache/               # Model and torch cache
│   ├── models/          # HuggingFace model cache
│   └── torch/           # PyTorch cache
│
├── config.py            # Global configuration
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
├── run_local.ps1       # Windows startup script
└── README.md           # This file
```

## 🔧 Troubleshooting

### Common Issues

**1. "CUDA not available"**
- Install CUDA toolkit: https://developer.nvidia.com/cuda-downloads
- Verify installation: `nvidia-smi`
- Install correct PyTorch version: https://pytorch.org/get-started/locally/

**2. "Redis connection failed"**
- Ensure Redis is running: `redis-cli ping`
- Check Redis port: default is 6379
- Install Redis: https://github.com/microsoftarchive/redis/releases

**3. "Model download slow"**
- First run downloads ~10GB model from HuggingFace
- Ensure stable internet connection
- Models cached in `./cache/models`

**4. "Out of memory (OOM)"**
- Reduce resolution (use 360p or 480p)
- Close other GPU applications
- Enable attention slicing in `svd/renderer.py`

**5. "Bot not responding"**
- Check bot token in `.env`
- Verify bot is running: check logs
- Ensure backend is accessible

### Performance Optimization

**For RTX 4090 / High-end GPUs:**
- Use 1080p resolution
- Disable model CPU offload in `svd/renderer.py`
- Increase batch processing if needed

**For RTX 3060 / Mid-range GPUs:**
- Use 720p or lower
- Keep model CPU offload enabled
- Consider enabling attention slicing

**For Limited VRAM (<8GB):**
- Use 360p or 480p only
- Enable attention slicing
- Reduce concurrent jobs to 1

## 📊 System Requirements

### Minimum Requirements
- **GPU**: NVIDIA RTX 3060 (8GB VRAM)
- **RAM**: 16GB
- **Storage**: 20GB free space
- **OS**: Windows 10/11

### Recommended Requirements
- **GPU**: NVIDIA RTX 4070 or higher (12GB+ VRAM)
- **RAM**: 32GB
- **Storage**: 50GB+ SSD
- **OS**: Windows 11

## 🛠️ Development

### Adding New Motion Presets

Edit `config.py`:

```python
MOTION_PRESETS = {
    "your_preset": {
        "motion_bucket_id": 100,
        "description": "Your custom motion"
    }
}
```

### Extending API

Add new endpoints in `backend/app.py`:

```python
@app.get("/your/endpoint")
async def your_endpoint():
    # Your logic here
    return {"status": "ok"}
```

### Custom SVD Parameters

Modify generation in `svd/renderer.py`:

```python
def generate_video(self, params: VideoGenerationParams):
    # Adjust parameters
    frames = self.pipeline(
        image=image,
        num_frames=num_frames,
        # Add custom parameters
    )
```

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- **Stability AI** for Stable Video Diffusion model
- **HuggingFace** for diffusers library
- **aiogram** team for Telegram bot framework
- **FastAPI** for the excellent web framework

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact via Telegram: [Your contact]
- Email: [Your email]

## 🔮 Future Roadmap

- [ ] Web interface for video generation
- [ ] Custom motion trajectory editor
- [ ] Batch processing support
- [ ] Video style transfer
- [ ] Cloud deployment guides
- [ ] Docker containerization
- [ ] Advanced motion interpolation
- [ ] Multi-image video generation

---

**Made with ❤️ for AI video generation enthusiasts**

*Powered by Stable Video Diffusion XT*

