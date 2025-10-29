# Решение проблем FanslyMotion

## 🔴 Бот не реагирует на /start

### Симптомы:
- Вы отправляете `/start`, но бот не отвечает
- Бот "застрял" в состоянии ожидания фото
- Повторные команды `/start` игнорируются

### Причина:
Бот завис в состоянии FSM (Finite State Machine) и не может выйти из него.

### Решение:

**Вариант 1: Перезапустить бота (быстро)**
```powershell
# Остановить Python процессы
Get-Process python | Where-Object { $_.Path -like "*fanslymotion*" } | Stop-Process -Force

# Подождать 2 секунды
Start-Sleep 2

# Запустить заново (откроется 3 окна)
cd C:\fns_bot\fanslymotion
.\run_local_clean.ps1
```

**Вариант 2: Отправить /cancel (если бот реагирует)**
Некоторые боты имеют команду отмены. Попробуйте:
```
/cancel
```

**Вариант 3: Нажать кнопку "Cancel"**
Если бот показывает кнопку ❌ Cancel - нажмите её.

**Вариант 4: Нажать "Back to Menu"**
Если есть кнопка ◀️ Back to Menu - используйте её.

---

## 🔴 Backend не отвечает

### Симптомы:
- Бот показывает "Submitting job to server..."
- Задача не создаётся
- Ошибка "Connection failed"

### Решение:

**Шаг 1: Проверить Backend**
```powershell
curl http://127.0.0.1:8000/health
```

Должно вернуть:
```json
{"status":"healthy","redis":"connected","queue_length":0}
```

**Шаг 2: Если Backend не отвечает**
Проверьте, открыто ли окно "BACKEND API" (зелёное).
Если нет - перезапустите:
```powershell
cd C:\fns_bot\fanslymotion
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

---

## 🔴 Redis не подключается

### Симптомы:
- Health endpoint возвращает: `"status":"unhealthy"`
- Ошибка: `"redis":"Connection refused"`

### Решение:

**Шаг 1: Проверить Redis**
```powershell
cd C:\Redis-x64-3.0.504
.\redis-cli.exe ping
```

Должно вернуть: `PONG`

**Шаг 2: Если Redis не отвечает**
Запустите Redis:
```powershell
cd C:\Redis-x64-3.0.504
.\redis-server.exe
```

Оставьте окно открытым!

---

## 🔴 Worker не обрабатывает задачи

### Симптомы:
- Задача создаётся
- Прогресс не идёт
- Застряло на "Queue position: X"

### Решение:

**Шаг 1: Проверить Worker**
Откройте окно "RQ WORKER" (жёлтое) и посмотрите на ошибки.

**Шаг 2: Проверить модель AI**
Если первый запуск - модель скачивается (10-30 минут).
Проверьте папку:
```powershell
dir C:\AI-cache\huggingface\hub
```

**Шаг 3: Перезапустить Worker**
```powershell
cd C:\fns_bot\fanslymotion
.\venv\Scripts\Activate.ps1
python worker/worker.py
```

---

## 🔴 "Technical error. Credits refunded"

### Возможные причины:

**1. PyTorch не установлен**
```powershell
cd C:\fns_bot\fanslymotion
.\venv\Scripts\Activate.ps1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**2. Diffusers не установлен**
```powershell
pip install diffusers transformers accelerate
```

**3. Недостаточно VRAM**
Используйте меньшее разрешение (360p или 480p).

**4. CUDA не доступна**
Проверьте:
```powershell
nvidia-smi
```

Должна показать вашу видеокарту.

---

## 🔴 Все окна закрылись

### Причина:
Произошла ошибка в одном из сервисов.

### Решение:

**Запустите каждый сервис вручную** в отдельных окнах:

**Окно 1 - Redis:**
```powershell
cd C:\Redis-x64-3.0.504
.\redis-server.exe
```

**Окно 2 - Backend:**
```powershell
cd C:\fns_bot\fanslymotion
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

**Окно 3 - Bot:**
```powershell
cd C:\fns_bot\fanslymotion
.\venv\Scripts\Activate.ps1
python bot/bot.py
```

**Окно 4 - Worker:**
```powershell
cd C:\fns_bot\fanslymotion
.\venv\Scripts\Activate.ps1
python worker/worker.py
```

Смотрите на ошибки в каждом окне!

---

## 🔴 Долгая обработка

### Нормально:
- **Первый запуск**: 10-30 минут (скачивание модели)
- **360p, 6s**: ~1 минута
- **480p, 6s**: ~2 минуты
- **720p, 6s**: ~3-5 минут
- **1080p, 6s**: ~5-10 минут

### Если дольше:
1. Проверьте Worker - есть ли ошибки?
2. Проверьте GPU: `nvidia-smi`
3. Проверьте VRAM не переполнена?

---

## 🔴 Порт 8000 занят

### Симптомы:
```
Error: [Errno 10048] address already in use
```

### Решение:

**Найти процесс:**
```powershell
netstat -ano | findstr :8000
```

**Убить процесс:**
```powershell
Stop-Process -Id <PID> -Force
```

Или измените порт в `.env`:
```ini
BACKEND_PORT=8001
```

---

## 🔴 Бот не видит фото

### Проблема:
Вы отправили фото, но бот не реагирует.

### Причина:
Вы не прошли все шаги выбора параметров!

### Решение:
Нужно пройти **ВСЕ** шаги:
1. `/start`
2. Кнопка "📸 photo→video 🎦"
3. Выбрать длительность
4. Выбрать разрешение
5. Выбрать движение
6. **ТОЛЬКО ПОТОМ** отправлять фото!

---

## 🛠️ Полный сброс системы

Если ничего не помогает:

```powershell
# 1. Остановить всё
Get-Process python,redis-server -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Очистить очередь Redis
cd C:\Redis-x64-3.0.504
.\redis-cli.exe FLUSHALL

# 3. Перезапустить всё
cd C:\fns_bot\fanslymotion

# Запустить Redis
cd C:\Redis-x64-3.0.504
Start-Process powershell -ArgumentList "-NoExit","-Command",".\redis-server.exe"

# Запустить сервисы
cd C:\fns_bot\fanslymotion
.\run_local_clean.ps1
```

---

## 📊 Проверка статуса системы

**Быстрая диагностика:**
```powershell
# Redis работает?
redis-cli ping

# Backend работает?
curl http://127.0.0.1:8000/health

# Сколько задач в очереди?
redis-cli llen svd_jobs

# Какие процессы Python запущены?
Get-Process python | Where-Object { $_.Path -like "*fanslymotion*" }
```

---

## 💡 Советы

1. **Не закрывайте окна** пока работаете с ботом
2. **Смотрите на логи** в окнах - там видны ошибки
3. **Начните с малого**: 480p, 6s, micro movement
4. **Первый запуск долгий** - это нормально (скачивание модели)
5. **Сохраняйте порядок**: Redis → Backend → Worker → Bot

---

Если проблема не решена - проверьте логи в окнах сервисов!

