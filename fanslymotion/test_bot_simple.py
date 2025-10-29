"""Simple bot test to diagnose startup issues."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("[1] Importing modules...")
try:
    from config import settings
    print("    ✅ config imported")
except Exception as e:
    print(f"    ❌ config import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("[2] Checking bot token...")
if not settings.bot_token:
    print("    ❌ BOT_TOKEN not set!")
    sys.exit(1)
print(f"    ✅ BOT_TOKEN found: {settings.bot_token[:10]}...")

print("[3] Importing aiogram...")
try:
    from aiogram import Bot, Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    print("    ✅ aiogram imported")
except Exception as e:
    print(f"    ❌ aiogram import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("[4] Importing bot handlers...")
try:
    from bot.handlers import router
    print("    ✅ handlers imported")
except Exception as e:
    print(f"    ❌ handlers import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("[5] Creating bot instance...")
try:
    bot = Bot(token=settings.bot_token)
    print("    ✅ Bot instance created")
except Exception as e:
    print(f"    ❌ Bot creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("[6] Creating dispatcher...")
try:
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    print("    ✅ Dispatcher created and router registered")
except Exception as e:
    print(f"    ❌ Dispatcher creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All checks passed! Bot should start now.")
print("=" * 60)
print("NOW RUNNING: python -m bot.bot")
print("=" * 60)

