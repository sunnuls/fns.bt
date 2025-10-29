# 🚀 Быстрая установка Redis для Windows

## ⚠️ ВАЖНО!
Redis **ОБЯЗАТЕЛЕН** для работы бота! Без него бот не сможет создавать задачи на генерацию видео.

---

## 📥 Вариант 1: Скачать Redis (5 минут)

### Шаг 1: Скачать
Откройте в браузере:
```
https://github.com/microsoftarchive/redis/releases/latest
```

Скачайте файл: **Redis-x64-X.X.XXX.zip**

### Шаг 2: Распаковать
1. Распакуйте ZIP в любую папку, например: `C:\Redis`
2. Вы увидите файлы: `redis-server.exe`, `redis-cli.exe` и др.

### Шаг 3: Запустить
Откройте PowerShell в папке Redis и выполните:
```powershell
cd C:\Redis
.\redis-server.exe
```

**ВАЖНО:** Оставьте это окно открытым! Redis должен работать постоянно.

### Шаг 4: Проверить
Откройте новое окно PowerShell:
```powershell
cd C:\Redis
.\redis-cli.exe ping
```

Должно вернуть: `PONG`

✅ **Redis установлен и работает!**

---

## 📥 Вариант 2: Через Chocolatey (если установлен)

```powershell
choco install redis-64
redis-server
```

---

## 📥 Вариант 3: WSL (если у вас Ubuntu/Debian)

```powershell
# Установить WSL (если нет)
wsl --install

# Перезагрузить компьютер

# В WSL терминале:
sudo apt update
sudo apt install redis-server
sudo service redis-server start

# Проверить:
redis-cli ping
```

---

## 🔄 После установки Redis

### 1. Перезапустите все сервисы:

В PowerShell:
```powershell
cd C:\fns_bot\fanslymotion

# Остановить старые процессы
Get-Process python | Where-Object { $_.Path -like "*fanslymotion*" } | Stop-Process -Force

# Запустить заново (откроется 3 окна)
.\run_local_clean.ps1
```

### 2. Проверьте работу:

```powershell
# Backend должен быть здоров
curl http://127.0.0.1:8000/health
```

Ответ должен быть:
```json
{
  "status": "healthy",
  "redis": "connected",
  "queue_length": 0
}
```

### 3. Попробуйте бота:

1. Отправьте `/start` в Telegram
2. Пройдите все шаги
3. Загрузите фото
4. **ТЕПЕРЬ ДОЛЖНО РАБОТАТЬ!** 🎉

---

## 🚫 Типичные проблемы

### Redis сразу закрывается
**Решение:** Запускайте через PowerShell, не двойным кликом!

### "Connection refused"
**Причина:** Redis не запущен
**Решение:** Запустите `redis-server.exe`

### "Port 6379 in use"
**Причина:** Redis уже запущен или порт занят
**Решение:** 
```powershell
# Найти процесс на порту 6379
netstat -ano | findstr :6379

# Убить процесс (замените PID)
Stop-Process -Id <PID> -Force
```

---

## 💡 Автозапуск Redis (опционально)

### Способ 1: Ярлык в автозагрузке

1. Создайте ярлык для `redis-server.exe`
2. Поместите в: `C:\Users\<ИМЯ>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

### Способ 2: Как служба Windows

```powershell
# Запустить PowerShell от администратора
cd C:\Redis
.\redis-server.exe --service-install
.\redis-server.exe --service-start
```

---

## 📊 Проверка статуса

В любое время можете проверить:

```powershell
# Redis работает?
redis-cli ping

# Сколько задач в очереди?
redis-cli llen svd_jobs

# Какие ключи есть?
redis-cli keys "*"
```

---

## 🎯 После установки Redis

Бот сможет:
- ✅ Создавать задачи на генерацию видео
- ✅ Отслеживать прогресс в реальном времени
- ✅ Показывать позицию в очереди
- ✅ Возвращать готовые видео

**Установите Redis прямо сейчас - это займет 5 минут!** 🚀

