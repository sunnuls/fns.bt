# Deployment Guide

This guide covers deploying FanslyMotion to production environments.

## Deployment Options

### Option 1: Single Windows Server (Recommended for Start)

**Requirements**:
- Windows Server 2019+ or Windows 10/11 Pro
- NVIDIA GPU (RTX series)
- 32GB+ RAM
- 100GB+ SSD storage
- Static IP or domain name

**Setup Steps**:

1. **Install Prerequisites**:
   ```powershell
   # Install Python 3.10+
   # Install CUDA Toolkit
   # Install Redis
   # Install Git
   ```

2. **Clone and Configure**:
   ```powershell
   git clone <your-repo-url>
   cd fanslymotion
   copy env.example .env
   # Edit .env with production settings
   ```

3. **Install as Windows Service**:
   
   Create `install_service.ps1`:
   ```powershell
   # Install NSSM (Non-Sucking Service Manager)
   # Download from: https://nssm.cc/download
   
   # Create services for each component
   nssm install FanslyMotion_Backend "C:\path\to\python.exe" "C:\path\to\backend\app.py"
   nssm install FanslyMotion_Worker "C:\path\to\python.exe" "C:\path\to\worker\worker.py"
   nssm install FanslyMotion_Bot "C:\path\to\python.exe" "C:\path\to\bot\bot.py"
   
   # Start services
   nssm start FanslyMotion_Backend
   nssm start FanslyMotion_Worker
   nssm start FanslyMotion_Bot
   ```

4. **Configure Firewall**:
   ```powershell
   # Allow FastAPI port
   New-NetFirewallRule -DisplayName "FanslyMotion API" -Direction Inbound -Port 8000 -Protocol TCP -Action Allow
   ```

5. **Setup Reverse Proxy** (Optional, for HTTPS):
   - Install nginx for Windows
   - Configure SSL with Let's Encrypt
   - Proxy requests to FastAPI backend

### Option 2: Docker Deployment

**Docker Compose Setup**:

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - BOT_TOKEN=${BOT_TOKEN}
    depends_on:
      - redis
    restart: unless-stopped

  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      - REDIS_URL=redis://redis:6379/0
      - CUDA_VISIBLE_DEVICES=0
    depends_on:
      - redis
    runtime: nvidia
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  redis_data:
```

**Dockerfiles**:

`Dockerfile.backend`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY config.py .

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

`Dockerfile.worker`:
```dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y python3.10 python3-pip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker/ ./worker/
COPY svd/ ./svd/
COPY config.py .

CMD ["python3", "worker/worker.py"]
```

`Dockerfile.bot`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ ./bot/
COPY config.py .

CMD ["python3", "bot/bot.py"]
```

**Deploy**:
```bash
docker-compose up -d
```

### Option 3: Cloud Deployment (AWS)

**Architecture**:
```
Internet
   ↓
Telegram Bot API
   ↓
EC2 (Bot) ←→ ALB ←→ ECS (Backend)
                ↓
            ElastiCache (Redis)
                ↓
            EC2 GPU (Worker)
                ↓
            S3 (Storage)
```

**Steps**:

1. **Setup Infrastructure**:
   - EC2 instance for bot (t3.small)
   - ECS cluster for backend (Fargate)
   - EC2 GPU instance for worker (g4dn.xlarge)
   - ElastiCache Redis
   - S3 bucket for storage
   - Application Load Balancer

2. **Configure Services**:
   ```bash
   # Bot EC2
   sudo systemctl enable fanslymotion-bot
   sudo systemctl start fanslymotion-bot
   
   # Worker EC2 (GPU)
   sudo systemctl enable fanslymotion-worker
   sudo systemctl start fanslymotion-worker
   ```

3. **Environment Variables**:
   - Use AWS Secrets Manager
   - Reference secrets in ECS task definitions
   - Use IAM roles for S3 access

### Option 4: Kubernetes (Advanced)

**Helm Chart Structure**:
```
fanslymotion-chart/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── backend-deployment.yaml
    ├── worker-deployment.yaml
    ├── bot-deployment.yaml
    ├── redis-statefulset.yaml
    ├── services.yaml
    └── ingress.yaml
```

**Deploy**:
```bash
helm install fanslymotion ./fanslymotion-chart
```

## Production Considerations

### Security

1. **Environment Variables**:
   - Never commit `.env` file
   - Use secrets management (AWS Secrets, Azure Key Vault)
   - Rotate bot token regularly

2. **Network Security**:
   - Use HTTPS/TLS for API
   - Restrict Redis access to internal network
   - Implement rate limiting
   - Add authentication to API endpoints

3. **Input Validation**:
   - Verify image file types
   - Limit file sizes (max 10MB)
   - Sanitize user inputs
   - Validate callback data

### Performance Optimization

1. **Caching**:
   - Cache model weights on fast SSD
   - Use Redis for hot data
   - Implement CDN for video delivery

2. **Queue Management**:
   - Monitor queue length
   - Implement priority queues
   - Auto-scale workers based on load

3. **GPU Utilization**:
   - Batch similar resolutions together
   - Keep model loaded in memory
   - Use multiple workers for multiple GPUs

### Monitoring

1. **Application Monitoring**:
   - Prometheus + Grafana for metrics
   - Sentry for error tracking
   - Custom metrics:
     - Jobs per hour
     - Average processing time
     - Success/failure rate
     - GPU utilization

2. **Infrastructure Monitoring**:
   - CPU/Memory usage
   - GPU temperature/utilization
   - Disk space
   - Network throughput

3. **Alerting**:
   - Queue length exceeds threshold
   - Worker crashes
   - High error rate
   - GPU temperature warning

### Logging

**Centralized Logging**:
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
handler = RotatingFileHandler(
    'logs/fanslymotion.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler]
)
```

**Log Aggregation**:
- Use ELK Stack (Elasticsearch, Logstash, Kibana)
- Or Grafana Loki
- Or CloudWatch Logs (AWS)

### Backup & Recovery

1. **Data Backup**:
   ```powershell
   # Backup script
   $date = Get-Date -Format "yyyy-MM-dd"
   $backupPath = "C:\backups\fanslymotion_$date"
   
   # Backup Redis
   redis-cli BGSAVE
   Copy-Item "C:\Redis\dump.rdb" "$backupPath\redis_dump.rdb"
   
   # Backup storage
   Copy-Item -Recurse "storage\" "$backupPath\storage"
   
   # Backup configuration
   Copy-Item ".env" "$backupPath\.env"
   ```

2. **Disaster Recovery**:
   - Document recovery procedures
   - Test recovery process regularly
   - Keep offsite backups
   - Implement automated backups

### Scaling Strategy

**Vertical Scaling** (Single Server):
- Upgrade to better GPU (RTX 4090)
- Increase RAM (64GB+)
- Use faster storage (NVMe SSD)

**Horizontal Scaling** (Multiple Servers):
```
Load Balancer
    ↓
┌───┴───┬───────┬───────┐
│       │       │       │
Backend Backend Backend Backend
│       │       │       │
└───┬───┴───────┴───────┘
    ↓
Redis Cluster
    ↓
┌───┴───┬───────┬───────┐
│       │       │       │
Worker  Worker  Worker  Worker
(GPU)   (GPU)   (GPU)   (GPU)
```

**Auto-scaling Rules**:
- Scale workers: Queue length > 20
- Scale backend: CPU > 80%
- Scale down: Queue empty for 10 minutes

### Cost Optimization

1. **GPU Instance Management**:
   - Use spot instances for workers
   - Stop workers during low usage
   - Schedule based on traffic patterns

2. **Storage Optimization**:
   - Implement automatic cleanup
   - Move old files to archive/S3 Glacier
   - Compress videos if possible

3. **Model Optimization**:
   - Use quantized models
   - Implement model distillation
   - Cache frequently used parameters

## Maintenance

### Regular Tasks

**Daily**:
- Monitor queue length
- Check error logs
- Verify GPU health

**Weekly**:
- Review performance metrics
- Clear old job data
- Update dependencies

**Monthly**:
- Security updates
- Backup verification
- Capacity planning review

### Troubleshooting

**Bot Not Responding**:
```bash
# Check bot process
ps aux | grep bot.py

# Check logs
tail -f logs/bot.log

# Restart bot
systemctl restart fanslymotion-bot
```

**Worker Issues**:
```bash
# Check GPU
nvidia-smi

# Check worker logs
tail -f logs/worker.log

# Clear stuck jobs
redis-cli DEL rq:queue:svd_jobs
```

**Backend Errors**:
```bash
# Check API health
curl http://localhost:8000/health

# Check logs
tail -f logs/backend.log

# Restart backend
systemctl restart fanslymotion-backend
```

## Environment-Specific Configurations

### Development
```ini
DEBUG=true
LOG_LEVEL=DEBUG
WORKER_MAX_JOBS=1
QUEUE_LIMIT=5
```

### Staging
```ini
DEBUG=false
LOG_LEVEL=INFO
WORKER_MAX_JOBS=5
QUEUE_LIMIT=10
```

### Production
```ini
DEBUG=false
LOG_LEVEL=WARNING
WORKER_MAX_JOBS=10
QUEUE_LIMIT=50
SENTRY_DSN=your_sentry_dsn
METRICS_ENABLED=true
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Security hardening completed
- [ ] Monitoring setup
- [ ] Logging configured
- [ ] Backup system in place
- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured
- [ ] Health checks working
- [ ] Error tracking enabled
- [ ] Documentation updated
- [ ] Team trained on operations
- [ ] Runbook created
- [ ] Disaster recovery tested

## Support & Resources

- GitHub Issues: [Your repo]
- Documentation: [Your docs site]
- Status Page: [Your status page]
- Contact: [Your contact]

---

**Deploy with confidence! 🚀**

