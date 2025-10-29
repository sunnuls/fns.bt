# Быстрое решение проблемы с ботом

## Проблема
Бот не запускается или окно остается пустым. Импорт aiogram зависает.

## Быстрое решение

### Вариант 1: Переустановка зависимостей

```powershell
# Остановите все процессы
Get-Process python | Stop-Process -Force

# Переустановите пакеты
pip uninstall -y aiogram pydantic pydantic-core pydantic-settings
pip install aiogram>=3.22.0 pydantic>=2.11.10 pydantic-settings>=2.11.0

# Проверьте
python -c "from aiogram import Bot; print('OK')"
```

### Вариант 2: Запуск через простой скрипт

Создайте файл `run_bot_simple.py`:
```python
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("Starting...")
sys.stdout.flush()

try:
    print("Importing...")
    sys.stdout.flush()
    from aiogram import Bot, Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    from config import settings
    from bot.handlers import router
    
    print("Starting bot...")
    sys.stdout.flush()
    
    async def main():
        bot = Bot(token=settings.bot_token)
        dp = Dispatcher(storage=MemoryStorage())
        dp.include_router(router)
        
        me = await bot.get_me()
        print(f"Bot: @{me.username}")
        
        await dp.start_polling(bot)
    
    import asyncio
    asyncio.run(main())
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter...")
```

Запустите:
```powershell
python run_bot_simple.py
```

### Вариант 3: Проверка окружения

Возможно проблема в поврежденных пакетах. Попробуйте:

```powershell
# Создайте виртуальное окружение заново
python -m venv venv_new
venv_new\Scripts\activate
pip install -r requirements.txt

# Затем запустите бота
python -m bot.bot
```

## Диагностика

Если ничего не помогает, проверьте:

1. **Версия Python**: Должна быть 3.10+
   ```powershell
   python --version
   ```

2. **Путь к Python**: Убедитесь что используете правильный Python
   ```powershell
   where python
   ```

3. **Логи Windows**: Проверьте Event Viewer на ошибки Python

4. **Альтернативный запуск**: Попробуйте напрямую
   ```powershell
   cd C:\fns_bot\fanslymotion
   python.exe -u bot\bot.py
   ```

