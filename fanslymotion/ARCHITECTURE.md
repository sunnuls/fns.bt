# FanslyMotion Architecture Documentation

This document describes the technical architecture and design decisions of the FanslyMotion system.

## System Overview

FanslyMotion is a distributed system for AI-powered photo-to-video generation using Stable Video Diffusion. It consists of four main components:

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                      (Telegram Bot - aiogram 3)                  │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTP Requests
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API Gateway                                 │
│                    (FastAPI Backend)                             │
│  Endpoints: /job/create, /job/status/{id}, /job/result/{id}    │
└────────────────┬────────────────────────────────────────────────┘
                 │ Job Enqueue
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Message Queue                               │
│                      (Redis + RQ)                                │
│           Job Queue, Status Tracking, Metadata                   │
└────────────────┬────────────────────────────────────────────────┘
                 │ Job Dequeue
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Processing Worker                            │
│                   (RQ Worker + GPU)                              │
│          SVD Model Inference, Video Generation                   │
└────────────────┬────────────────────────────────────────────────┘
                 │ Save Results
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Storage Layer                                │
│              Hot Storage + Archive Storage                        │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Telegram Bot (User Interface)

**Location**: `bot/`

**Responsibilities**:
- User interaction and conversation flow
- Parameter collection (duration, resolution, motion)
- Image upload handling
- Progress tracking and updates
- Result delivery

**Key Technologies**:
- `aiogram 3.x` - Modern async Telegram Bot framework
- FSM (Finite State Machine) for conversation flow
- Inline keyboards for user interaction

**Flow**:
1. User sends `/start`
2. Bot displays main menu
3. User selects "photo→video"
4. Bot guides through parameter selection
5. User uploads photo
6. Bot creates job via API
7. Bot polls job status and updates user
8. Bot delivers final video

**Key Files**:
- `bot/bot.py` - Main bot entry point
- `bot/handlers.py` - Command and callback handlers
- `bot/keyboards.py` - Inline keyboard builders
- `bot/states.py` - FSM state definitions

### 2. FastAPI Backend (API Gateway)

**Location**: `backend/`

**Responsibilities**:
- RESTful API for job management
- Job creation and validation
- Status tracking
- Result retrieval and download
- Queue management

**Endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/job/create` | POST | Create new job |
| `/job/status/{id}` | GET | Get job status |
| `/job/result/{id}` | GET | Get job result |
| `/job/download/{id}` | GET | Download video |

**Key Technologies**:
- `FastAPI` - Modern async web framework
- `Pydantic` - Data validation
- `Redis` - Job metadata storage
- `RQ` - Job queue integration

**Key Files**:
- `backend/app.py` - FastAPI application
- `backend/models.py` - Pydantic request/response models

### 3. Redis Queue (Message Queue)

**Responsibilities**:
- Job queue management
- Job metadata storage
- Status synchronization
- Worker coordination

**Data Structures**:

```
Redis Keys:
├── job:{job_id}:metadata     # Job configuration and status (JSON)
├── job:{job_id}:rq_id        # RQ job ID mapping
└── rq:queue:svd_jobs         # Job queue (managed by RQ)
```

**Job Metadata Schema**:
```json
{
  "job_id": "uuid",
  "user_id": 123456789,
  "image_path": "/path/to/image.png",
  "duration": 6,
  "resolution": "720p",
  "motion_preset": "pan_l",
  "status": "processing",
  "created_at": "2024-01-01T00:00:00Z",
  "started_at": "2024-01-01T00:00:10Z",
  "completed_at": null,
  "progress": 45.0,
  "message": "Generating video frames...",
  "error": null
}
```

### 4. RQ Worker (Processing)

**Location**: `worker/`

**Responsibilities**:
- Job processing from queue
- GPU-accelerated video generation
- Progress reporting
- Error handling and retries
- Result persistence

**Processing Pipeline**:
1. Dequeue job from Redis
2. Load job metadata
3. Initialize/get SVD model
4. Preprocess input image
5. Run video generation
6. Save video to storage
7. Update job status
8. Report completion

**Key Technologies**:
- `RQ (Redis Queue)` - Job processing
- `PyTorch` - Deep learning framework
- `CUDA` - GPU acceleration
- `Diffusers` - Hugging Face diffusion models

**Key Files**:
- `worker/worker.py` - Worker entry point
- `worker/tasks.py` - Job processing logic

### 5. SVD Renderer (AI Model)

**Location**: `svd/`

**Responsibilities**:
- SVD model loading and management
- Image preprocessing
- Video frame generation
- Motion preset application
- Video encoding

**Technical Details**:

**Model**: `stabilityai/stable-video-diffusion-img2vid-xt`
- **Type**: Latent Video Diffusion Model
- **Input**: Single RGB image
- **Output**: Video frames sequence
- **Precision**: FP16 (half precision for GPU efficiency)

**Processing Pipeline**:
```
Input Image
    ↓
Resize & Crop → Target Resolution
    ↓
VAE Encoding → Latent Space
    ↓
Denoising Process → Motion Application (24 steps)
    ↓
VAE Decoding → Video Frames
    ↓
Frame Sequencing → Duration × FPS
    ↓
Video Encoding → MP4 (H.264)
    ↓
Output Video
```

**Motion Presets**:

| Preset | Bucket ID | Description | Use Case |
|--------|-----------|-------------|----------|
| micro | 50 | Subtle movements | Static scenes, portraits |
| pan_l | 100 | Pan left | Landscape, panorama |
| pan_r | 100 | Pan right | Landscape, panorama |
| tilt_up | 100 | Tilt upward | Buildings, vertical scenes |
| tilt_down | 100 | Tilt downward | Aerial views, top-down |
| dolly_in | 127 | Zoom in | Focus, emphasis |

**Key Files**:
- `svd/renderer.py` - SVD pipeline and generation logic

## Data Flow

### Job Creation Flow

```
1. User uploads image via Telegram
        ↓
2. Bot encodes image to base64
        ↓
3. Bot sends POST /job/create with parameters
        ↓
4. Backend validates parameters
        ↓
5. Backend saves image to hot storage
        ↓
6. Backend creates job metadata in Redis
        ↓
7. Backend enqueues job to RQ
        ↓
8. Backend returns job_id and queue position
        ↓
9. Bot receives job_id and starts polling
```

### Job Processing Flow

```
1. Worker dequeues job from Redis
        ↓
2. Worker updates status to "processing"
        ↓
3. Worker loads SVD model (if not loaded)
        ↓
4. Worker preprocesses image (resize, crop)
        ↓
5. Worker generates video frames (GPU)
        ↓
6. Worker encodes frames to MP4
        ↓
7. Worker saves video to hot storage
        ↓
8. Worker updates status to "completed"
        ↓
9. Worker updates metadata with video_path
```

### Progress Tracking Flow

```
Bot polling loop:
    1. GET /job/status/{job_id} every 3 seconds
    2. Backend queries Redis for metadata
    3. Backend queries RQ for job state
    4. Backend returns status + progress
    5. Bot updates user with progress bar
    6. Repeat until completed/failed
```

## Configuration System

**Location**: `config.py`

Centralized configuration using environment variables:

```python
class Settings:
    # Telegram
    bot_token: str
    
    # Redis
    redis_url: str
    redis_host: str
    redis_port: int
    
    # Backend
    backend_host: str
    backend_port: int
    backend_url: str
    
    # Storage
    storage_hot_path: Path
    storage_archive_path: Path
    
    # GPU
    cuda_visible_devices: str
    
    # Model
    svd_model_id: str
    svd_model_cache: Path
```

**Constants**:
```python
class VideoConfig:
    RESOLUTIONS = {"360p": (480, 360), ...}
    DURATIONS = [3, 6, 8, 10, 12]
    MOTION_PRESETS = {...}
    FPS = 12
    STEPS = 24
    GUIDANCE_SCALE = 1.0
    NOISE_AUGMENTATION = 0.1
```

## Storage Architecture

### Hot Storage (`storage/hot/`)
- **Purpose**: Active job processing
- **Contents**: Input images, output videos
- **Naming**: `{job_id}_input.png`, `{job_id}_output.mp4`
- **Lifetime**: Until manually archived or deleted
- **Access**: Direct file access for workers

### Archive Storage (`storage/archive/`)
- **Purpose**: Long-term storage (future feature)
- **Contents**: Completed job artifacts
- **Lifecycle**: Move from hot after N days

### Model Cache (`cache/models/`)
- **Purpose**: Hugging Face model caching
- **Contents**: SVD model weights, configs
- **Size**: ~10GB
- **Persistence**: Permanent (speeds up subsequent runs)

## Performance Optimizations

### GPU Memory Management
1. **Half Precision (FP16)**: Reduces VRAM usage by 50%
2. **Model CPU Offload**: Keeps model on CPU until needed
3. **Attention Slicing**: Optional for low-VRAM GPUs
4. **Decode Chunk Size**: Process frames in chunks

### Queue Management
1. **Max Queue Size**: Limit concurrent jobs (default: 10)
2. **Timeout**: Job timeout to prevent hanging (default: 300s)
3. **Retry Logic**: 3 attempts with 40s delay
4. **Job Priority**: FIFO (First In, First Out)

### Caching Strategy
1. **Model Singleton**: Single model instance per worker
2. **Redis Metadata**: Fast status lookups
3. **Local File Cache**: Minimize network operations

## Error Handling

### Error Types

1. **Validation Errors**
   - Invalid parameters
   - Unsupported formats
   - Missing required fields
   - **Action**: Return 400 Bad Request

2. **Resource Errors**
   - Queue full
   - Out of GPU memory
   - Disk space full
   - **Action**: Return 429/503, retry or notify

3. **Processing Errors**
   - Model inference failure
   - Image preprocessing error
   - Video encoding failure
   - **Action**: Retry up to 3 times, then fail

4. **System Errors**
   - Redis connection lost
   - Worker crash
   - File system error
   - **Action**: Log, alert, attempt recovery

### Error Recovery

```python
# Worker retry logic
@job(retry=Retry(max=3, interval=[40, 80, 160]))
def process_video_generation(job_id):
    try:
        # Processing logic
        pass
    except Exception as e:
        # Update error status
        # Notify user
        # Log for debugging
        raise
```

## Security Considerations

1. **Input Validation**: All parameters validated via Pydantic
2. **File Upload**: Size limits, type checking
3. **Path Sanitization**: Prevent directory traversal
4. **Token Storage**: Environment variables, not hardcoded
5. **CORS**: Configured for specific origins
6. **Rate Limiting**: Queue size limits

## Scalability

### Horizontal Scaling

**Workers**:
- Multiple workers can run simultaneously
- Each worker processes one job at a time
- Workers share Redis queue
- GPU required per worker

**Backend**:
- Stateless design allows multiple instances
- Share Redis for coordination
- Load balancer for distribution

**Storage**:
- Switch to S3/Cloud Storage for distributed access
- Implement CDN for video delivery

### Vertical Scaling

**GPU**:
- Better GPU = faster generation
- More VRAM = higher resolutions
- Multi-GPU: Run multiple workers

**Redis**:
- Redis persistence for reliability
- Redis Cluster for high availability

## Monitoring & Observability

### Metrics to Track

1. **Job Metrics**
   - Jobs created/hour
   - Jobs completed/hour
   - Average processing time
   - Success rate
   - Error rate

2. **Resource Metrics**
   - GPU utilization
   - GPU memory usage
   - Queue length
   - Storage usage

3. **Performance Metrics**
   - API response time
   - Job latency (queue → complete)
   - Bot response time

### Logging

**Log Levels**:
- `INFO`: Normal operations (job created, started, completed)
- `WARNING`: Recoverable issues (retry, queue full)
- `ERROR`: Failures (job failed, connection lost)
- `DEBUG`: Detailed debugging (model loading, frame generation)

**Log Locations**:
- Backend: Console + file
- Worker: Console + file
- Bot: Console + file

## Future Enhancements

1. **Async Processing**: WebSocket for real-time updates
2. **Batch Processing**: Multiple images → single video
3. **Custom Trajectories**: User-defined motion paths
4. **Style Transfer**: Apply artistic styles to videos
5. **Cloud Deployment**: Docker + Kubernetes
6. **Web Dashboard**: Admin panel for monitoring
7. **Video Effects**: Filters, transitions, overlays
8. **Multi-language**: i18n for bot messages

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Bot | aiogram 3 | Telegram interaction |
| API | FastAPI | REST endpoints |
| Queue | Redis + RQ | Job management |
| Worker | PyTorch + CUDA | GPU processing |
| Model | Diffusers | SVD pipeline |
| Storage | Local FS | File persistence |
| Video | imageio-ffmpeg | MP4 encoding |
| Config | pydantic-settings | Configuration |

## Development Workflow

1. **Local Development**: Use `run_local.ps1`
2. **Testing**: Use `test_setup.py` for validation
3. **Debugging**: Check service windows for logs
4. **Iteration**: Modify code, services auto-reload
5. **Deployment**: Package for production environment

## Conclusion

FanslyMotion demonstrates a production-ready architecture for AI-powered media generation:
- **Modular**: Clear separation of concerns
- **Scalable**: Horizontal and vertical scaling support
- **Resilient**: Error handling and retries
- **Performant**: GPU optimization and caching
- **User-friendly**: Intuitive bot interface

This architecture can be adapted for other AI generation tasks (text-to-video, audio generation, etc.) by swapping the rendering module.

