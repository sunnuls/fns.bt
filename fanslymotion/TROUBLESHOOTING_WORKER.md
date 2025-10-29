# 🔧 Решение проблем с Worker

## Проблема: AbandonedJobError

**Симптомы:**
- Job создается и попадает в очередь ✅
- Worker начинает обработку ✅
- Но затем: "AbandonedJobError" ❌
- GPU не нагружается или падает до 10%

## Причины:

### 1. Worker падает при импорте модулей
**Решение:** Проверьте окно Worker - должны быть логи импорта

### 2. Worker падает при загрузке модели (OOM)
**Решение:** 
- Используйте 720p вместо 1080p
- Включен CPU offload (автоматически для <16GB VRAM)

### 3. Worker таймаутится (Windows SimpleWorker)
**Решение:**
- Таймауты увеличены до 600s (10 минут)
- Используется NoOp death penalty

### 4. Ошибки в процессе генерации
**Решение:** Проверьте логи worker на наличие ERROR

## Диагностика:

### Шаг 1: Проверьте Worker окно

После запуска задания должны быть:

```
[WORKER] Starting job: ...
[WORKER] Job func: worker.tasks.process_video_generation
[START] Job ...
[DEBUG] Metadata loaded...
[INFO] Getting renderer...
```

**Если логов нет после `[WORKER] Starting job` →**
- Worker падает при импорте
- Проверьте ошибки выше

**Если видите `[INFO] Getting renderer...` но дальше ничего →**
- Падает при загрузке модели
- Проверьте VRAM и ошибки

### Шаг 2: Проверьте GPU

```powershell
nvidia-smi -l 1
```

**Ожидаемое:**
- 0% → 50-60% (модель) → 80-100% (генерация) → 0%
- Если GPU не поднимается → модель не загружается

### Шаг 3: Проверьте логи

В Worker окне найдите строки с:
- `[ERROR]` - ошибки
- `[WARN]` - предупреждения
- `Traceback` - стек вызовов при ошибке

## Быстрое решение:

### Если Worker не обрабатывает:

1. **Проверьте что Worker запущен:**
```powershell
Get-Process python | Where-Object { try { $proc = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)"; $proc.CommandLine -like "*worker*" } catch { $false } }
```

2. **Перезапустите Worker:**
```powershell
.\restart_worker.ps1
```

3. **Проверьте Redis:**
```powershell
python -c "import redis; r = redis.Redis(); print('Redis OK' if r.ping() else 'Redis FAILED')"
```

### Если GPU не загружается:

1. **Проверьте CUDA:**
```powershell
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

2. **Проверьте модель:**
```powershell
python -c "from svd.renderer import get_renderer; r = get_renderer(); r.load_model()"
```

3. **Используйте меньшие настройки:**
- Разрешение: 720p (не 1080p)
- Длительность: 6s (не 12s)
- Quality: Standard (не Smooth)

## Типичные ошибки:

### "Out of Memory" или "CUDA OOM"
**Решение:**
- Используйте 720p или 480p
- Убедитесь что CPU offload включен
- Закройте другие GPU приложения

### "Module not found: worker.tasks"
**Решение:**
- Запускайте worker из директории `fanslymotion`
- Проверьте что `worker/tasks.py` существует

### "Model loading timeout"
**Решение:**
- Первая загрузка может занять 5-10 минут
- Убедитесь что модель скачана (проверьте `cache/models/`)

---

**После исправлений перезапустите: `.\restart_worker.ps1`**

