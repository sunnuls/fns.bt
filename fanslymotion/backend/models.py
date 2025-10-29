"""
Pydantic models for API requests and responses.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ResolutionEnum(str, Enum):
    """Supported video resolutions."""
    RES_360P = "360p"
    RES_480P = "480p"
    RES_720P = "720p"
    RES_1080P = "1080p"


class MotionPresetEnum(str, Enum):
    """Motion preset options."""
    MICRO = "micro"
    SMOOTH = "smooth"
    PAN_L = "pan_l"
    PAN_R = "pan_r"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"
    DOLLY_IN = "dolly_in"
    DYNAMIC = "dynamic"


class VisualStyleEnum(str, Enum):
    """Visual style options (like LitVideo)."""
    NONE = "none"
    ANIME = "anime"
    COMIC = "comic"
    THREE_D = "3d"
    CLAY = "clay"
    CYBERPUNK = "cyberpunk"
    CINEMATIC = "cinematic"
    FANTASY = "fantasy"


class QualityModeEnum(str, Enum):
    """Quality/speed mode options."""
    FAST = "fast"
    STANDARD = "standard"
    SMOOTH = "smooth"


class JobCreateRequest(BaseModel):
    """Request model for creating a new video generation job."""
    user_id: int = Field(..., description="Telegram user ID")
    image_data: str = Field(..., description="Base64 encoded image data")
    duration: int = Field(..., ge=3, le=12, description="Video duration in seconds")
    resolution: ResolutionEnum = Field(..., description="Output video resolution")
    motion_preset: MotionPresetEnum = Field(..., description="Motion preset to apply")
    visual_style: Optional[VisualStyleEnum] = Field(None, description="Visual style (anime, comic, etc)")
    quality_mode: Optional[QualityModeEnum] = Field(None, description="Quality/speed mode")
    user_prompt: Optional[str] = Field(None, max_length=500, description="User description/prompt")
    custom_fps: Optional[int] = Field(None, ge=12, le=30, description="Custom FPS override")
    custom_steps: Optional[int] = Field(None, ge=20, le=60, description="Custom steps override")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123456789,
                "image_data": "base64_encoded_string_here",
                "duration": 6,
                "resolution": "720p",
                "motion_preset": "pan_l",
                "visual_style": "anime",
                "quality_mode": "standard",
                "user_prompt": "a beautiful anime scene with cherry blossoms"
            }
        }


class JobCreateResponse(BaseModel):
    """Response model for job creation."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Initial job status")
    queue_position: int = Field(..., description="Position in queue")
    estimated_time: int = Field(..., description="Estimated processing time in seconds")


class JobStatusResponse(BaseModel):
    """Response model for job status check."""
    job_id: str
    status: JobStatus
    queue_position: Optional[int] = None
    progress: Optional[float] = Field(None, ge=0.0, le=100.0, description="Progress percentage")
    message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class JobResultResponse(BaseModel):
    """Response model for job result retrieval."""
    job_id: str
    status: JobStatus
    video_url: Optional[str] = None
    video_path: Optional[str] = None
    duration: Optional[int] = None
    resolution: Optional[str] = None
    motion_preset: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    file_size: Optional[int] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None

