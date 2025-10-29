"""
RQ Worker entry point for processing video generation jobs.
"""
import sys
import os
from pathlib import Path

# Add project root to path FIRST
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Change working directory to project root
os.chdir(project_root)

# CRITICAL: Patch RQ timeouts BEFORE importing Worker/SimpleWorker
# This prevents SIGALRM errors on Windows

# First, patch signal module
import signal
if not hasattr(signal, 'SIGALRM'):
    # Create a dummy SIGALRM to prevent AttributeError
    signal.SIGALRM = -1

import rq.timeouts
import rq.worker

# Replace death penalty with complete no-op to avoid SIGALRM on Windows
class NoOpDeathPenalty:
    """Death penalty that does nothing - no timeout enforcement on Windows."""
    def __init__(self, timeout, exception=None, **kwargs):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def setup_death_penalty(self):
        pass
    
    def cancel_death_penalty(self):
        pass

# Monkey-patch BEFORE any RQ imports - replace all death penalty classes
rq.timeouts.UnixSignalDeathPenalty = NoOpDeathPenalty
rq.timeouts.BaseDeathPenalty = NoOpDeathPenalty
rq.timeouts.JobTimeoutException = Exception

# Also patch Worker class to not use death penalty
original_perform_job = None

def patched_perform_job(self, job, queue):
    """Perform job without death penalty on Windows."""
    import rq.job
    from datetime import datetime, timezone
    import traceback
    
    print(f"\n[WORKER] Starting job: {job.id}")
    print(f"[WORKER] Job func: {job.func_name}")
    print(f"[WORKER] Job args: {job.args}")
    
    try:
        # Mark job as started
        job.started_at = datetime.now(timezone.utc)
        job.save()
        print(f"[WORKER] Job marked as started")
        
        # Execute job without timeout
        print(f"[WORKER] Executing job.perform()...")
        rv = job.perform()
        print(f"[WORKER] Job perform() completed, result: {rv}")
        
        # Mark as successful
        job.ended_at = datetime.now(timezone.utc)
        job._result = rv
        job._status = rq.job.JobStatus.FINISHED
        job.save()
        print(f"[WORKER] Job marked as finished successfully")
        
        return True
    except Exception as e:
        # Mark as failed
        error_trace = traceback.format_exc()
        print(f"[WORKER ERROR] Job failed: {e}")
        print(f"[WORKER ERROR] Traceback:\n{error_trace}")
        
        job.ended_at = datetime.now(timezone.utc)
        job._exc_info = error_trace
        job._status = rq.job.JobStatus.FAILED
        job.save()
        print(f"[WORKER] Job marked as failed")
        raise

from redis import Redis
from rq import Worker, Queue, SimpleWorker
from config import settings, init_storage

# Patch the perform_job method for Windows
if hasattr(SimpleWorker, 'perform_job'):
    original_perform_job = SimpleWorker.perform_job
    # Override perform_job with our patched version
    SimpleWorker.perform_job = patched_perform_job
    print("✅ Patched SimpleWorker.perform_job with enhanced logging")

# Initialize storage
init_storage()

# Connect to Redis
redis_conn = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db
)

# Create queue
queue = Queue(settings.worker_queue_name, connection=redis_conn)

if __name__ == "__main__":
    print("Starting RQ Worker for video generation...")
    print(f"Connected to Redis: {settings.redis_host}:{settings.redis_port}")
    print(f"Queue: {settings.worker_queue_name}")
    print(f"Timeout: {settings.worker_timeout}s")
    
    # Test import before starting worker
    try:
        from worker.tasks import process_video_generation
        print("✅ Successfully imported worker.tasks.process_video_generation")
    except Exception as e:
        print(f"❌ Failed to import worker.tasks: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Detect platform and use appropriate Worker
    # SimpleWorker is required for Windows (no fork support)
    is_windows = os.name == 'nt'
    
    if is_windows:
        print("Running in Windows mode (SimpleWorker with NoOp death penalty)")
        # Create worker with NoOp death penalty
        worker = SimpleWorker([queue], connection=redis_conn)
        # Force NoOp death penalty
        worker.death_penalty_class = NoOpDeathPenalty
        
        # Disable job timeout on Windows (SimpleWorker doesn't support it properly)
        # We rely on application-level timeouts instead
        print("⚠️  Job timeout disabled (Windows limitation)")
        print("    Using application-level timeout: 600s")
    else:
        print("Running in Unix mode (Worker)")
        worker = Worker([queue], connection=redis_conn)
    
    # Start processing jobs without scheduler
    print("Worker started, waiting for jobs...")
    print("Ready to process video generation jobs!")
    try:
        worker.work(with_scheduler=False)
    except KeyboardInterrupt:
        print("\nWorker stopped by user")
    except Exception as e:
        print(f"Worker crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

