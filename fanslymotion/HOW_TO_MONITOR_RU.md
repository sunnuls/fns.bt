# Как отслеживать работу системы

## 🪟 Какие окна должны быть открыты?

У вас должно быть **4 окна PowerShell**:

### 1. **REDIS SERVER** (красное/белое)
```
[PID] Redis Server v3.0.504
The server is now ready to accept connections on port 6379
```
**Что это:** База данных для очереди задач  
**Должно быть:** Работает постоянно, нет ошибок

---

### 2. **BACKEND API** (зелёное)
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```
**Что это:** API-сервер для связи бота с системой  
**Должно быть:** "Application startup complete", нет красных ERROR

---

### 3. **TELEGRAM BOT** (@LunaMotionBot, голубое)
```
INFO - Starting FanslyMotion Telegram Bot...
INFO - Start polling
INFO - Run polling for bot @LunaMotionBot
```
**Что это:** Ваш Telegram бот  
**Должно быть:** "Run polling", нет ошибок

---

### 4. **RQ WORKER** (жёлтое) ⭐ **САМОЕ ВАЖНОЕ**
```
Starting RQ Worker for video generation...
Connected to Redis: localhost:6379
Queue: svd_jobs
```
**Что это:** Обработчик задач, генератор видео  
**Должно быть:** "Connected to Redis", ждёт задач

---

## 🔍 Как понять, что модель скачивается?

### Когда вы отправите задачу, в окне **RQ WORKER** появится:

**1. Начало обработки:**
```
Starting job 33e500af-724a-454d-9b66-455f76bfcb06
```

**2. Загрузка модели (ПЕРВЫЙ РАЗ - долго!):**
```
Loading SVD model: stabilityai/stable-video-diffusion-img2vid-xt
Downloading (…)del.fp16.safetensors: 0%|          | 0/10.0G [00:00<?, ?B/s]
Downloading (…)del.fp16.safetensors: 1%|▏         | 100M/10.0G [00:30<45:00, 3.5MB/s]
Downloading (…)del.fp16.safetensors: 5%|▌         | 500M/10.0G [02:30<47:30, 3.4MB/s]
```

**Признаки скачивания:**
- ✅ Строка "Downloading (...)"
- ✅ Прогресс-бар с процентами: `5%|▌`
- ✅ Скорость скачивания: `3.5MB/s`
- ✅ Оставшееся время: `<45:00`

**3. После скачивания (быстро):**
```
Model loaded on cuda
✅ Generating video: 6s @ 480x640
Running inference with 24 steps, 72 frames...
Saving video to storage/hot/33e500af_output.mp4
✅ Video generated successfully
```

---

## 📊 Как проверить размер скачанной модели?

### PowerShell команда:
```powershell
# Проверить размер модели
$path = "C:\AI-cache\huggingface\hub"
$files = Get-ChildItem $path -Recurse -File
$size = ($files | Measure-Object -Property Length -Sum).Sum / 1GB
Write-Host "Model size: $([math]::Round($size, 2)) GB"

# Должно быть: ~9-10 GB когда скачана полностью
```

### Быстрая проверка:
```powershell
dir C:\AI-cache\huggingface\hub /s
```

**Если папка пустая (< 1 ГБ)** - модель не скачана  
**Если папка ~10 ГБ** - модель скачана

---

## ⏱️ Сколько времени займёт?

### Первый запуск (скачивание модели):
- **Быстрый интернет (50+ Мбит/с):** 10-15 минут
- **Средний интернет (20-50 Мбит/с):** 20-30 минут
- **Медленный интернет (< 20 Мбит/с):** 40-60 минут

### После скачивания модели:
- **360p, 6s:** ~1 минута
- **480p, 6s:** ~2 минуты
- **720p, 6s:** ~3-4 минуты
- **1080p, 6s:** ~5-7 минут

---

## 🚨 Типичные проблемы в окне RQ WORKER

### ❌ "Connection refused"
```
redis.exceptions.ConnectionError: Error 10061
```
**Причина:** Redis не запущен  
**Решение:** Запустите окно REDIS SERVER

---

### ❌ "ImportError: cannot import name 'cached_download'"
```
ImportError: cannot import name 'cached_download' from 'huggingface_hub'
```
**Причина:** Несовместимость библиотек  
**Решение:** 
```powershell
cd C:\fns_bot\fanslymotion
.\venv\Scripts\Activate.ps1
pip install --upgrade huggingface-hub diffusers
```

---

### ❌ "OSError: [WinError 1114] DLL initialization failed"
```
OSError: [WinError 1114] A dynamic link library (DLL) initialization routine failed
```
**Причина:** Проблема с PyTorch  
**Решение:** Переустановите PyTorch:
```powershell
pip uninstall torch torchvision -y
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

---

### ❌ "CUDA out of memory"
```
RuntimeError: CUDA out of memory
```
**Причина:** Недостаточно VRAM на GPU  
**Решение:** 
1. Используйте меньшее разрешение (360p или 480p)
2. Закройте другие программы, использующие GPU
3. Перезапустите Worker

---

## 📈 Как следить за прогрессом в реальном времени?

### В Telegram боте:
```
✅ Job created!
🆔 Job ID: 33e500af-724a-454d-9b66-455f76bfcb06
📊 Queue position: 1

⏳ Starting processing...

🎬 Generating video...
[████████░░] 80%

✅ Your video is ready!
[Отправляет видео]
```

### В окне RQ WORKER:
- Смотрите на строки с процентами
- Ищите "Downloading" - значит скачивается
- Ищите "Generating" - значит создаёт видео
- Ищите "✅" - значит готово

---

## 🔄 Как перезапустить Worker, если что-то пошло не так?

### Вариант 1: Закрыть окно и запустить заново
1. Закройте окно "RQ WORKER"
2. Откройте новый PowerShell
3. Выполните:
```powershell
cd C:\fns_bot\fanslymotion
.\venv\Scripts\Activate.ps1
python worker/worker.py
```

### Вариант 2: Остановить через Task Manager
1. Ctrl+Shift+Esc
2. Найдите `python.exe` (3-4 процесса)
3. Завершите все
4. Запустите заново через `run_local_clean.ps1`

---

## 💡 Полезные команды для проверки

### Проверить, что Redis работает:
```powershell
cd C:\Redis-x64-3.0.504
.\redis-cli.exe ping
# Должно вернуть: PONG
```

### Проверить, сколько задач в очереди:
```powershell
.\redis-cli.exe llen rq:queue:svd_jobs
# 0 = пусто, 1+ = есть задачи
```

### Проверить статус задачи:
```powershell
.\redis-cli.exe get "job:ВАШ_JOB_ID:metadata"
# Покажет JSON с информацией о задаче
```

### Проверить Backend:
```powershell
curl http://127.0.0.1:8000/health
# Должно вернуть: {"status":"healthy","redis":"connected"}
```

### Проверить, запущены ли Python процессы:
```powershell
Get-Process python | Where-Object { $_.Path -like "*fanslymotion*" }
# Должно показать 2-3 процесса
```

---

## 🎯 Чек-лист перед генерацией видео

- [ ] 4 окна PowerShell открыты (Redis, Backend, Bot, Worker)
- [ ] В окне Worker написано "Connected to Redis"
- [ ] Backend отвечает на /health (status: healthy)
- [ ] Бот отвечает на /start
- [ ] Есть хотя бы 20 ГБ свободного места на диске C:
- [ ] Интернет работает (для первого раза)

---

## 📞 Что делать, если ничего не работает?

1. **Посмотрите на окно RQ WORKER** - там должны быть ошибки
2. **Сделайте скриншот ошибки**
3. **Проверьте, что все 4 окна открыты**
4. **Перезапустите всё:**
   ```powershell
   # Остановить всё
   Get-Process python,redis-server -ErrorAction SilentlyContinue | Stop-Process -Force
   
   # Запустить заново
   cd C:\fns_bot\fanslymotion
   .\run_local_clean.ps1
   ```

---

Теперь вы знаете, как следить за работой системы! 📊

