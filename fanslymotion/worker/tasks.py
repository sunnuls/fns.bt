"""
Worker tasks for video generation processing.
These tasks are executed by RQ workers with GPU access.
"""
import json
import traceback
from pathlib import Path
from datetime import datetime
import redis
from rq import get_current_job

from config import settings, VideoConfig
from svd.renderer import get_renderer, VideoGenerationParams


def update_job_progress(redis_client: redis.Redis, job_id: str, 
                       progress: float, message: str = None):
    """
    Update job progress in Redis and RQ job metadata.
    
    Args:
        redis_client: Redis client instance
        job_id: Job identifier
        progress: Progress percentage (0-100)
        message: Optional status message
    """
    try:
        # Update RQ job meta
        current_job = get_current_job()
        if current_job:
            current_job.meta["progress"] = progress
            if message:
                current_job.meta["message"] = message
            current_job.save_meta()
        
        # Update job metadata in Redis
        metadata_key = f"job:{job_id}:metadata"
        metadata_json = redis_client.get(metadata_key)
        
        if metadata_json:
            metadata = json.loads(metadata_json)
            metadata["progress"] = progress
            if message:
                metadata["message"] = message
            redis_client.set(metadata_key, json.dumps(metadata), ex=86400)
            
    except Exception as e:
        print(f"Error updating progress: {e}")


def process_video_generation(job_id: str, job_timeout: int = 600,
                            retry_count: int = 3, retry_delay: int = 40):
    """
    Main task for processing video generation from image.
    
    This function is executed by RQ workers and handles the entire
    video generation pipeline including model loading, inference, and saving.
    
    Args:
        job_id: Unique job identifier
        job_timeout: Maximum execution time in seconds
        retry_count: Number of retries on failure
        retry_delay: Delay between retries in seconds
        
    Returns:
        Dictionary with result information
        
    Raises:
        Exception: If video generation fails after all retries
    """
    # Initialize Redis connection
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=False
    )
    
    try:
        print(f"[START] Job {job_id}")
        print(f"[DEBUG] Starting at: {datetime.utcnow().isoformat()}")
        
        # Retrieve job metadata
        metadata_key = f"job:{job_id}:metadata"
        metadata_json = redis_client.get(metadata_key)
        
        if not metadata_json:
            raise ValueError(f"Job metadata not found for {job_id}")
        
        try:
            metadata = json.loads(metadata_json)
            print(f"[DEBUG] Metadata loaded: duration={metadata.get('duration')}, resolution={metadata.get('resolution')}")
        except Exception as e:
            print(f"[ERROR] Failed to parse metadata: {e}")
            raise
        
        # Update status to processing
        metadata["status"] = "processing"
        metadata["started_at"] = datetime.utcnow().isoformat()
        redis_client.set(metadata_key, json.dumps(metadata), ex=86400)
        
        update_job_progress(redis_client, job_id, 5.0, "Initializing model...")
        print(f"[INFO] Starting model load for job {job_id}...")
        
        # Get or initialize renderer (this may take 1-2 minutes on first load)
        print(f"[INFO] Getting renderer for job {job_id}...")
        print(f"[INFO] Model ID: {settings.svd_model_id}")
        print(f"[INFO] Cache dir: {settings.svd_model_cache}")
        
        try:
            import torch
            if torch.cuda.is_available():
                print(f"[INFO] CUDA available: {torch.cuda.get_device_name(0)}")
                print(f"[INFO] VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
                # Clear any existing GPU memory before loading model
                torch.cuda.empty_cache()
                print(f"[INFO] GPU memory cleared before model load")
            
            renderer = get_renderer(
                model_id=settings.svd_model_id,
                cache_dir=settings.svd_model_cache
            )
            print(f"[INFO] Renderer obtained successfully")
            
            # Force model load
            if renderer.pipeline is None:
                print(f"[INFO] Model not loaded, loading now...")
                renderer.load_model()
            
            print(f"[INFO] Model loaded successfully for job {job_id}")
            if torch.cuda.is_available():
                print(f"[INFO] GPU memory after load: {torch.cuda.memory_allocated() / 1024**3:.2f}GB")
                print(f"[INFO] GPU will be used for generation!")
            
        except Exception as e:
            error_msg = f"Failed to load model: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Full traceback:")
            print(traceback.format_exc())
            update_job_progress(redis_client, job_id, 5.0, f"Error loading model: {str(e)}")
            raise ValueError(error_msg)
        
        update_job_progress(redis_client, job_id, 20.0, "Model loaded, preprocessing image...")
        
        # Prepare generation parameters
        image_path = Path(metadata["image_path"])
        output_filename = f"{job_id}_output.mp4"
        output_path = settings.storage_hot_path / output_filename
        
        resolution = VideoConfig.RESOLUTIONS[metadata["resolution"]]
        
        # Get motion preset configuration
        motion_preset = metadata["motion_preset"]
        motion_config = VideoConfig.MOTION_PRESETS.get(motion_preset, {})
        
        # Use custom FPS and steps if provided, otherwise use defaults
        custom_fps = metadata.get("custom_fps") or VideoConfig.FPS
        custom_steps = metadata.get("custom_steps") or VideoConfig.STEPS
        
        # Get quality mode settings if not custom
        quality_mode = metadata.get("quality_mode", "standard")
        if not metadata.get("custom_fps") or not metadata.get("custom_steps"):
            quality_settings = VideoConfig.QUALITY_MODES.get(quality_mode, {})
            custom_fps = quality_settings.get("fps", VideoConfig.FPS)
            custom_steps = quality_settings.get("steps", VideoConfig.STEPS)
        
        params = VideoGenerationParams(
            image_path=image_path,
            output_path=output_path,
            duration=metadata["duration"],
            resolution=resolution,
            motion_preset=motion_preset,
            fps=custom_fps,
            steps=custom_steps,
            guidance_scale=VideoConfig.GUIDANCE_SCALE,
            noise_aug_strength=VideoConfig.NOISE_AUGMENTATION,
            motion_bucket_id=motion_config.get("motion_bucket_id", 127),
            enhance_output=VideoConfig.ENHANCE_OUTPUT
        )
        
        print(f"[CONFIG] Using FPS: {custom_fps}, Steps: {custom_steps}")
        print(f"[CONFIG] Style: {metadata.get('visual_style', 'none')}, Quality: {quality_mode}")
        if metadata.get("user_prompt"):
            print(f"[CONFIG] Prompt: {metadata['user_prompt'][:100]}...")
        
        update_job_progress(redis_client, job_id, 30.0, "Generating video frames...")
        
        print(f"[INFO] Starting video generation with params:")
        print(f"       Resolution: {params.resolution}")
        print(f"       Duration: {params.duration}s")
        print(f"       FPS: {params.fps}")
        print(f"       Steps: {params.steps}")
        print(f"       Motion preset: {params.motion_preset}")
        
        # Define progress callback for detailed updates
        def on_progress(step, total_steps):
            # Map steps to progress 30%-85%
            progress = 30.0 + (step / total_steps) * 55.0
            print(f"[PROGRESS] Step {step}/{total_steps} ({progress:.1f}%)")
            update_job_progress(redis_client, job_id, progress, f"Generating frame step {step}/{total_steps}...")
        
        # Generate video with progress callback
        print(f"[INFO] Calling renderer.generate_video()...")
        try:
            video_path = renderer.generate_video(params, progress_callback=on_progress)
            print(f"[INFO] Video generation completed: {video_path}")
        except Exception as e:
            print(f"[ERROR] Video generation failed: {e}")
            print(f"[ERROR] Traceback:")
            print(traceback.format_exc())
            raise
        
        update_job_progress(redis_client, job_id, 90.0, "Finalizing video...")
        
        # Update metadata with result
        metadata["status"] = "completed"
        metadata["video_path"] = str(video_path)
        metadata["completed_at"] = datetime.utcnow().isoformat()
        metadata["progress"] = 100.0
        metadata["message"] = "Video generation completed successfully"
        
        redis_client.set(metadata_key, json.dumps(metadata), ex=86400)
        
        update_job_progress(redis_client, job_id, 100.0, "Completed!")
        
        print(f"[SUCCESS] Job {job_id} completed")
        
        # Clear GPU memory after job completion to prevent leaks
        if torch.cuda.is_available():
            print(f"[CLEANUP] Clearing GPU memory after job completion...")
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()  # Collect shared memory
            print(f"[CLEANUP] GPU memory after cleanup: {torch.cuda.memory_allocated() / 1024**3:.2f}GB")
        
        return {
            "job_id": job_id,
            "status": "completed",
            "video_path": str(video_path),
            "duration": metadata["duration"],
            "resolution": metadata["resolution"],
            "motion_preset": motion_preset
        }
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        print(f"[FAILED] Job {job_id}: {error_msg}")
        print(error_trace)
        
        # Update metadata with error
        try:
            metadata_json = redis_client.get(f"job:{job_id}:metadata")
            if metadata_json:
                metadata = json.loads(metadata_json)
                metadata["status"] = "failed"
                metadata["error"] = error_msg
                metadata["error_trace"] = error_trace
                metadata["completed_at"] = datetime.utcnow().isoformat()
                redis_client.set(f"job:{job_id}:metadata", json.dumps(metadata), ex=86400)
        except Exception as update_error:
            print(f"Failed to update error status: {update_error}")
        
        raise e


def cleanup_old_files(days: int = 7):
    """
    Cleanup task to remove old files from storage.
    
    Args:
        days: Number of days to keep files
    """
    from datetime import timedelta
    import time
    
    cutoff_time = time.time() - (days * 86400)
    
    for storage_path in [settings.storage_hot_path, settings.storage_archive_path]:
        if not storage_path.exists():
            continue
            
        for file_path in storage_path.glob("*"):
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        print(f"🗑️ Deleted old file: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")

