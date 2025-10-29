"""Quick bot connection test."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("QUICK BOT TEST")
print("=" * 70)

print("\n[1] Importing config...")
from config import settings
print(f"   ✅ Config loaded, BOT_TOKEN: {'SET' if settings.bot_token else 'NOT SET'}")

print("\n[2] Importing aiogram...")
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
print("   ✅ aiogram imported")

print("\n[3] Importing handlers...")
from bot.handlers import router
print("   ✅ handlers imported")

print("\n[4] Creating bot and dispatcher...")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)
bot = Bot(token=settings.bot_token)
print("   ✅ Bot and dispatcher created")

print("\n[5] Testing Telegram connection...")
import asyncio
async def test():
    me = await bot.get_me()
    print(f"   ✅ Connected: @{me.username} ({me.first_name})")
    await bot.session.close()

asyncio.run(test())

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("Bot should work now!")
print("=" * 70)

