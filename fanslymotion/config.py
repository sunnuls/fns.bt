"""
Global configuration management for the FanslyMotion project.
Loads environment variables and provides typed configuration objects.
"""
import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Telegram Bot
    bot_token: str = os.getenv("BOT_TOKEN", "")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    
    # Backend
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Storage
    storage_hot_path: Path = Path(os.getenv("STORAGE_HOT_PATH", "./storage/hot"))
    storage_archive_path: Path = Path(os.getenv("STORAGE_ARCHIVE_PATH", "./storage/archive"))
    
    # Worker
    worker_queue_name: str = os.getenv("WORKER_QUEUE_NAME", "svd_jobs")
    worker_max_jobs: int = int(os.getenv("WORKER_MAX_JOBS", "10"))
    worker_timeout: int = int(os.getenv("WORKER_TIMEOUT", "900"))  # 15 minutes for 12GB VRAM
    
    # GPU
    cuda_visible_devices: str = os.getenv("CUDA_VISIBLE_DEVICES", "0")
    torch_home: Path = Path(os.getenv("TORCH_HOME", "./cache/torch"))
    hf_home: Path = Path(os.getenv("HF_HOME", "./cache/huggingface"))
    
    # SVD Model
    svd_model_id: str = os.getenv("SVD_MODEL_ID", "stabilityai/stable-video-diffusion-img2vid-xt")
    svd_model_cache: Path = Path(os.getenv("SVD_MODEL_CACHE", "./cache/models"))
    
    # Job Configuration
    job_retry_count: int = int(os.getenv("JOB_RETRY_COUNT", "3"))
    job_retry_delay: int = int(os.getenv("JOB_RETRY_DELAY", "40"))
    job_timeout: int = int(os.getenv("JOB_TIMEOUT", "60"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Video generation constants
class VideoConfig:
    """Video generation configuration constants."""
    
    # Supported resolutions (width, height)
    RESOLUTIONS = {
        "360p": (480, 360),
        "480p": (640, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
    }
    
    # Supported durations in seconds
    DURATIONS = [3, 6, 8, 10, 12]
    
    # Motion presets with their parameters
    MOTION_PRESETS = {
        "micro": {"motion_bucket_id": 50, "description": "Subtle micro-movements"},
        "pan_l": {"motion_bucket_id": 100, "description": "Pan left"},
        "pan_r": {"motion_bucket_id": 100, "description": "Pan right"},
        "tilt_up": {"motion_bucket_id": 100, "description": "Tilt upward"},
        "tilt_down": {"motion_bucket_id": 100, "description": "Tilt downward"},
        "dolly_in": {"motion_bucket_id": 127, "description": "Zoom in (dolly)"},
        "smooth": {"motion_bucket_id": 80, "description": "Smooth natural motion"},
        "dynamic": {"motion_bucket_id": 150, "description": "Dynamic movement"},
    }
    
    # Visual styles (like LitVideo)
    VISUAL_STYLES = {
        "none": {"description": "No style (realistic)", "prompt_suffix": ""},
        "anime": {"description": "Anime style", "prompt_suffix": ", anime style, vibrant colors"},
        "comic": {"description": "Comic book style", "prompt_suffix": ", comic book style, bold lines"},
        "3d": {"description": "3D Animation", "prompt_suffix": ", 3D animation style, CGI"},
        "clay": {"description": "Claymation", "prompt_suffix": ", clay animation style, stop motion"},
        "cyberpunk": {"description": "Cyberpunk", "prompt_suffix": ", cyberpunk style, neon lights, futuristic"},
        "cinematic": {"description": "Cinematic", "prompt_suffix": ", cinematic style, film grain, professional"},
        "fantasy": {"description": "Fantasy", "prompt_suffix": ", fantasy style, magical, dreamy"},
    }
    
    # Quality modes
    QUALITY_MODES = {
        "standard": {"steps": 40, "fps": 24, "description": "Standard quality"},
        "smooth": {"steps": 50, "fps": 30, "description": "Ultra smooth (highest quality)"},
        "fast": {"steps": 30, "fps": 18, "description": "Fast generation"},
    }
    
    # Technical parameters (Enhanced for maximum quality)
    FPS: int = 24  # Increased from 12 to 24 for smoother video
    STEPS: int = 40  # Increased from 24 to 40 for better quality
    GUIDANCE_SCALE: float = 1.0
    NOISE_AUGMENTATION: float = 0.1
    ENHANCE_OUTPUT: bool = True  # Enable post-processing enhancements
    
    # Queue settings
    MAX_QUEUE_SIZE: int = 10
    RETRY_COUNT: int = 3
    RETRY_DELAY: int = 60  # seconds (increased for longer processing time)
    TIMEOUT: int = 600  # seconds (10 minutes - enough for model loading + generation on 12GB VRAM)


# Ensure storage directories exist
def init_storage():
    """Initialize storage directories if they don't exist."""
    settings.storage_hot_path.mkdir(parents=True, exist_ok=True)
    settings.storage_archive_path.mkdir(parents=True, exist_ok=True)
    settings.torch_home.mkdir(parents=True, exist_ok=True)
    settings.svd_model_cache.mkdir(parents=True, exist_ok=True)


# Resolution type alias
ResolutionType = Literal["360p", "480p", "720p", "1080p"]
MotionPresetType = Literal["micro", "pan_l", "pan_r", "tilt_up", "tilt_down", "dolly_in"]

