"""
FastAPI backend application for job management.
Provides REST API endpoints for video generation jobs.
"""
import base64
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import redis
from rq import Queue
from rq.job import Job

from config import settings, VideoConfig, init_storage
from backend.models import (
    JobCreateRequest, JobCreateResponse, JobStatusResponse,
    JobResultResponse, JobStatus, ErrorResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="FanslyMotion API",
    description="Video generation API using Stable Video Diffusion",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis connection and RQ queue
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=False
)

# RQ Queue for job processing
# Note: default_timeout removed for Windows compatibility (no SIGALRM support)
job_queue = Queue(
    name=settings.worker_queue_name,
    connection=redis_client
)


@app.on_event("startup")
async def startup_event():
    """Initialize storage directories on startup."""
    init_storage()
    print("[OK] FastAPI backend started")
    print(f"[STORAGE] Initialized at {settings.storage_hot_path}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "FanslyMotion API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "create_job": "/job/create",
            "job_status": "/job/status/{job_id}",
            "job_result": "/job/result/{job_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check Redis connection
        redis_client.ping()
        queue_length = len(job_queue)
        
        return {
            "status": "healthy",
            "redis": "connected",
            "queue_length": queue_length,
            "max_queue_size": VideoConfig.MAX_QUEUE_SIZE
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.post("/job/create", response_model=JobCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_job(request: JobCreateRequest):
    """
    Create a new video generation job.
    
    Args:
        request: Job creation request with image data and parameters
        
    Returns:
        Job creation response with job ID and queue position
    """
    try:
        # Check queue limit
        current_queue_size = len(job_queue)
        if current_queue_size >= VideoConfig.MAX_QUEUE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Queue is full. Maximum {VideoConfig.MAX_QUEUE_SIZE} jobs allowed."
            )
        
        # Validate duration
        if request.duration not in VideoConfig.DURATIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid duration. Allowed: {VideoConfig.DURATIONS}"
            )
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Save image to temporary storage
        image_filename = f"{job_id}_input.png"
        image_path = settings.storage_hot_path / image_filename
        
        try:
            image_bytes = base64.b64decode(request.image_data)
            with open(image_path, "wb") as f:
                f.write(image_bytes)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image data: {str(e)}"
            )
        
        # Prepare job metadata with new fields
        job_metadata = {
            "job_id": job_id,
            "user_id": request.user_id,
            "image_path": str(image_path),
            "duration": request.duration,
            "resolution": request.resolution.value,
            "motion_preset": request.motion_preset.value,
            "visual_style": request.visual_style.value if request.visual_style else "none",
            "quality_mode": request.quality_mode.value if request.quality_mode else "standard",
            "user_prompt": request.user_prompt or "",
            "custom_fps": request.custom_fps,
            "custom_steps": request.custom_steps,
            "created_at": datetime.utcnow().isoformat(),
            "status": JobStatus.QUEUED.value
        }
        
        # Store job metadata in Redis
        redis_client.set(
            f"job:{job_id}:metadata",
            json.dumps(job_metadata),
            ex=86400  # 24 hours expiry
        )
        
        # Enqueue job for processing
        # Use string path to avoid importing heavy ML libraries in backend
        # Note: job_timeout is not supported by SimpleWorker on Windows
        # But we set result_ttl to keep results longer
        rq_job = job_queue.enqueue(
            'worker.tasks.process_video_generation',
            job_id,  # Pass as positional argument
            result_ttl=3600,  # Keep result for 1 hour
            job_timeout=settings.worker_timeout  # Worker timeout from settings
        )
        
        # Store RQ job ID
        redis_client.set(f"job:{job_id}:rq_id", rq_job.id, ex=86400)
        
        # Calculate queue position and estimated time
        queue_position = current_queue_size + 1
        estimated_time = queue_position * 60  # Rough estimate: 60s per job
        
        return JobCreateResponse(
            job_id=job_id,
            status=JobStatus.QUEUED,
            queue_position=queue_position,
            estimated_time=estimated_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@app.get("/job/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a specific job.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Job status information including progress and queue position
    """
    try:
        # Retrieve job metadata
        metadata_key = f"job:{job_id}:metadata"
        metadata_json = redis_client.get(metadata_key)
        
        if not metadata_json:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        metadata = json.loads(metadata_json)
        
        # Get RQ job for detailed status
        rq_job_id = redis_client.get(f"job:{job_id}:rq_id")
        rq_job = None
        queue_position = None
        progress = None
        
        if rq_job_id:
            try:
                rq_job = Job.fetch(rq_job_id.decode('utf-8'), connection=redis_client)
                
                # Determine status from RQ job
                if rq_job.is_queued:
                    metadata["status"] = JobStatus.QUEUED.value
                    # Calculate queue position
                    queue_position = job_queue.get_job_position(rq_job.id)
                    if queue_position is not None:
                        queue_position += 1
                elif rq_job.is_started:
                    metadata["status"] = JobStatus.PROCESSING.value
                    # Get progress from job meta
                    progress = rq_job.meta.get("progress", 0)
                elif rq_job.is_finished:
                    metadata["status"] = JobStatus.COMPLETED.value
                    progress = 100.0
                elif rq_job.is_failed:
                    metadata["status"] = JobStatus.FAILED.value
                    metadata["error"] = str(rq_job.exc_info) if rq_job.exc_info else "Unknown error"
                    
            except Exception as e:
                print(f"Error fetching RQ job: {e}")
        
        return JobStatusResponse(
            job_id=job_id,
            status=JobStatus(metadata.get("status", JobStatus.PENDING.value)),
            queue_position=queue_position,
            progress=progress,
            message=metadata.get("message"),
            created_at=datetime.fromisoformat(metadata["created_at"]),
            started_at=datetime.fromisoformat(metadata["started_at"]) if metadata.get("started_at") else None,
            completed_at=datetime.fromisoformat(metadata["completed_at"]) if metadata.get("completed_at") else None,
            error=metadata.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )


@app.get("/job/result/{job_id}", response_model=JobResultResponse)
async def get_job_result(job_id: str):
    """
    Get the result of a completed job.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Job result information including video download URL
    """
    try:
        # Retrieve job metadata
        metadata_key = f"job:{job_id}:metadata"
        metadata_json = redis_client.get(metadata_key)
        
        if not metadata_json:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        metadata = json.loads(metadata_json)
        job_status = JobStatus(metadata.get("status", JobStatus.PENDING.value))
        
        # Check if job is completed
        if job_status != JobStatus.COMPLETED:
            return JobResultResponse(
                job_id=job_id,
                status=job_status,
                created_at=datetime.fromisoformat(metadata["created_at"]),
                completed_at=None
            )
        
        # Get video file path
        video_path = metadata.get("video_path")
        if not video_path or not Path(video_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video file not found"
            )
        
        # Get file size
        file_size = Path(video_path).stat().st_size
        
        return JobResultResponse(
            job_id=job_id,
            status=job_status,
            video_url=f"/job/download/{job_id}",
            video_path=video_path,
            duration=metadata.get("duration"),
            resolution=metadata.get("resolution"),
            motion_preset=metadata.get("motion_preset"),
            created_at=datetime.fromisoformat(metadata["created_at"]),
            completed_at=datetime.fromisoformat(metadata["completed_at"]) if metadata.get("completed_at") else None,
            file_size=file_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job result: {str(e)}"
        )


@app.get("/job/download/{job_id}")
async def download_video(job_id: str):
    """
    Download the generated video file.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Video file as downloadable content
    """
    try:
        # Retrieve job metadata
        metadata_key = f"job:{job_id}:metadata"
        metadata_json = redis_client.get(metadata_key)
        
        if not metadata_json:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        metadata = json.loads(metadata_json)
        
        # Check if job is completed
        if metadata.get("status") != JobStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job not completed yet"
            )
        
        # Get video file path
        video_path = metadata.get("video_path")
        if not video_path or not Path(video_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video file not found"
            )
        
        return FileResponse(
            path=video_path,
            media_type="video/mp4",
            filename=f"video_{job_id}.mp4"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download video: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )

