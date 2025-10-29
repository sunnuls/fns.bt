# Redis Installation for Windows

Redis is required for the job queue system. Here are your options:

## Option 1: Download Redis for Windows (Easiest)

1. Download latest release: https://github.com/microsoftarchive/redis/releases
2. Extract the ZIP file (e.g., to `C:\Redis`)
3. Run `redis-server.exe`
4. Leave the terminal window open (Redis running)

## Option 2: Use WSL (Windows Subsystem for Linux)

```powershell
# Install WSL if not already installed
wsl --install

# In WSL terminal:
sudo apt update
sudo apt install redis-server

# Start Redis
sudo service redis-server start

# Verify
redis-cli ping
```

## Option 3: Use Docker (if installed)

```powershell
docker run -d --name fanslymotion-redis -p 6379:6379 redis:7
```

## Verify Redis is Running

In PowerShell:
```powershell
# If using downloaded Redis:
.\redis-cli.exe ping
# Should return: PONG

# If using WSL:
wsl redis-cli ping
# Should return: PONG
```

## Troubleshooting

### Port 6379 already in use
- Another Redis instance or service is using that port
- Stop it or change port in `.env` file

### Connection refused
- Redis is not running
- Start redis-server

### redis-cli not found
- Redis not in PATH
- Navigate to Redis folder first
- Or add to PATH environment variable

