# ☁️ Развертывание FanslyMotion на облачных GPU серверах

Это руководство поможет развернуть FanslyMotion на удаленных серверах с мощными GPU для максимальной производительности.

## 🚀 Рекомендуемые провайдеры

### 1. **RunPod** (Рекомендуется)
- ✅ Почасовая оплата
- ✅ RTX 4090, A100, H100
- ✅ Быстрый деплой с Docker
- 💰 От $0.34/час (RTX 3090)

### 2. **Vast.ai**
- ✅ Самые низкие цены
- ✅ Spot instances
- ✅ Широкий выбор GPU
- 💰 От $0.15/час

### 3. **Lambda Labs**
- ✅ Высокая надежность
- ✅ A100, H100
- ✅ Отличная сеть
- 💰 От $0.50/час

## 📦 Быстрый старт с Docker

### Шаг 1: Подготовка сервера

```bash
# Клонировать репозиторий
git clone <your-repo-url>
cd fanslymotion

# Создать .env файл
cat > .env << EOF
BOT_TOKEN=your_telegram_bot_token
REDIS_HOST=redis
REDIS_PORT=6379
BACKEND_URL=http://backend:8000
CUDA_VISIBLE_DEVICES=0
EOF
```

### Шаг 2: Запуск с Docker Compose

```bash
# Запустить все сервисы
docker-compose up -d

# Проверить логи
docker-compose logs -f

# Проверить статус
docker-compose ps
```

### Шаг 3: Проверка работоспособности

```bash
# Проверить API
curl http://localhost:8000/health

# Проверить очередь Redis
docker exec -it fanslymotion-redis redis-cli
> KEYS *
```

## 🏗️ Развертывание на RunPod

### Создание нового Pod

1. **Выбор GPU:**
   - Минимум: RTX 3090 (24GB VRAM)
   - Рекомендуется: RTX 4090 (24GB VRAM)
   - Оптимально: A100 (40GB VRAM)

2. **Настройка контейнера:**

```yaml
Image: nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04
Container Disk: 50GB
Volume Disk: 100GB (для моделей и кеша)
Expose Ports: 8000, 6379
```

3. **Команды установки:**

```bash
# Подключиться по SSH
ssh root@<runpod-ip> -p <port>

# Установка зависимостей
apt-get update && apt-get install -y git python3-pip ffmpeg redis-server

# Клонировать и настроить
git clone <your-repo>
cd fanslymotion
pip3 install -r requirements.txt

# Запустить сервисы
./start_all.ps1  # или используйте screen/tmux
```

## 🔧 Оптимизация для максимальной производительности

### 1. Настройки GPU

```bash
# Включить persistence mode
nvidia-smi -pm 1

# Установить максимальную частоту
nvidia-smi -lgc 2100

# Проверить статус
nvidia-smi
```

### 2. Настройки Python

Создайте `config_production.py`:

```python
# Производственные настройки
STEPS = 50  # Максимальное качество
FPS = 30    # Ультра-плавное видео
ENHANCE_OUTPUT = True
MAX_QUEUE_SIZE = 20  # Больше параллельных заданий
```

### 3. Redis оптимизация

```bash
# Увеличить maxmemory в redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru
```

## 📊 Мониторинг производительности

### GPU мониторинг

```bash
# Постоянный мониторинг
watch -n 1 nvidia-smi

# Или используйте nvtop
apt-get install nvtop
nvtop
```

### Логи приложения

```bash
# Backend логи
docker-compose logs -f backend

# Worker логи
docker-compose logs -f worker

# Bot логи
docker-compose logs -f bot
```

## 🌐 Настройка доменного имени (опционально)

### С использованием Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL с Let's Encrypt

```bash
apt-get install certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

## 💡 Советы по экономии

1. **Используйте Spot instances на Vast.ai** - экономия до 70%
2. **Автоматическое выключение** при простое:

```python
# В worker/tasks.py добавить:
import time
IDLE_TIMEOUT = 3600  # 1 час

def check_idle():
    if no_jobs_for(IDLE_TIMEOUT):
        shutdown_instance()
```

3. **Пакетная обработка** - обрабатывайте несколько заданий за раз

## 🔍 Решение проблем

### Out of Memory (OOM)

```python
# В svd/renderer.py уменьшить:
decode_chunk_size=4  # вместо 8
```

### Медленная генерация

```bash
# Проверить CUDA
python3 -c "import torch; print(torch.cuda.is_available())"

# Установить xformers
pip3 install xformers==0.0.23
```

### Redis connection refused

```bash
# Проверить Redis
redis-cli ping

# Перезапустить
docker-compose restart redis
```

## 📈 Ожидаемая производительность

| GPU | Resolution | Duration | Time | Quality |
|-----|------------|----------|------|---------|
| RTX 3090 | 1080p | 6s | ~45s | 10/10 |
| RTX 4090 | 1080p | 6s | ~30s | 11/10 |
| A100 | 1080p | 6s | ~25s | 11/10 |
| RTX 3090 | 720p | 6s | ~25s | 10/10 |

## 🎯 Следующие шаги

1. ✅ Развернуть на облачном сервере
2. ✅ Настроить мониторинг
3. ✅ Оптимизировать параметры
4. ✅ Настроить автоматическое масштабирование
5. ✅ Добавить CDN для видео

---

**Поддержка:** Если возникли проблемы, проверьте логи: `docker-compose logs -f`

