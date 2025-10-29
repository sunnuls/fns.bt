#!/bin/bash
# RunPod Automated Setup Script for FanslyMotion
# This script sets up everything needed on a fresh RunPod instance

set -e

echo "🚀 Starting FanslyMotion setup on RunPod..."

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get install -y git python3-pip ffmpeg redis-server wget curl

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Clone repository (if not already present)
if [ ! -d "/workspace/fanslymotion" ]; then
    echo "📥 Cloning repository..."
    cd /workspace
    git clone https://github.com/yourusername/fanslymotion.git
fi

cd /workspace/fanslymotion

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOF
BOT_TOKEN=${BOT_TOKEN:-your_telegram_bot_token_here}
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_URL=http://localhost:8000
CUDA_VISIBLE_DEVICES=0
STORAGE_HOT_PATH=./storage/hot
STORAGE_ARCHIVE_PATH=./storage/archive
SVD_MODEL_CACHE=./cache/models
TORCH_HOME=./cache/torch
HF_HOME=./cache/huggingface
EOF
    echo "⚠️ Please edit .env file and add your BOT_TOKEN!"
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p storage/hot storage/archive cache/models cache/torch cache/huggingface

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Download models (optional, will happen on first run anyway)
echo "🤖 Models will be downloaded on first use..."

# Setup systemd services for auto-restart
echo "🔧 Setting up services..."

# Redis service
cat > /etc/systemd/system/fanslymotion-redis.service << 'EOF'
[Unit]
Description=Redis for FanslyMotion
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/redis-server
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Backend service
cat > /etc/systemd/system/fanslymotion-backend.service << 'EOF'
[Unit]
Description=FanslyMotion Backend API
After=network.target fanslymotion-redis.service

[Service]
Type=simple
WorkingDirectory=/workspace/fanslymotion
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Worker service
cat > /etc/systemd/system/fanslymotion-worker.service << 'EOF'
[Unit]
Description=FanslyMotion Worker
After=network.target fanslymotion-redis.service

[Service]
Type=simple
WorkingDirectory=/workspace/fanslymotion
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m rq worker --url redis://localhost:6379/0 svd_jobs
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Bot service
cat > /etc/systemd/system/fanslymotion-bot.service << 'EOF'
[Unit]
Description=FanslyMotion Telegram Bot
After=network.target fanslymotion-backend.service

[Service]
Type=simple
WorkingDirectory=/workspace/fanslymotion
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m bot.bot
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
echo "🚀 Starting services..."
systemctl daemon-reload
systemctl enable fanslymotion-redis
systemctl enable fanslymotion-backend
systemctl enable fanslymotion-worker
systemctl enable fanslymotion-bot

systemctl start fanslymotion-redis
sleep 2
systemctl start fanslymotion-backend
sleep 2
systemctl start fanslymotion-worker
systemctl start fanslymotion-bot

# GPU optimization
echo "⚡ Optimizing GPU settings..."
nvidia-smi -pm 1 || echo "Could not enable persistence mode"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Service status:"
systemctl status fanslymotion-redis --no-pager | head -3
systemctl status fanslymotion-backend --no-pager | head -3
systemctl status fanslymotion-worker --no-pager | head -3
systemctl status fanslymotion-bot --no-pager | head -3
echo ""
echo "🔍 Useful commands:"
echo "  - Check logs: journalctl -u fanslymotion-worker -f"
echo "  - Check GPU: nvidia-smi"
echo "  - Test API: curl http://localhost:8000/health"
echo ""
echo "⚠️ Don't forget to set your BOT_TOKEN in .env and restart services!"
echo "   systemctl restart fanslymotion-bot"

