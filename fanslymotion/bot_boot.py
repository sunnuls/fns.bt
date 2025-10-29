"""Bot boot script with maximum error handling."""
import sys
import time
import traceback
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("FANSLYMOTION BOT - BOOT SEQUENCE")
print("=" * 70)
sys.stdout.flush()

errors = []

def step(name, func):
    """Execute a step and catch errors."""
    print(f"\n[STEP] {name}...")
    sys.stdout.flush()
    try:
        result = func()
        print(f"[OK] {name} completed")
        sys.stdout.flush()
        return result
    except Exception as e:
        error_msg = f"{name} failed: {type(e).__name__}: {e}"
        print(f"[ERROR] {error_msg}")
        print(f"[TRACEBACK]")
        traceback.print_exc()
        sys.stdout.flush()
        errors.append(error_msg)
        return None

# Step 1: Config
config_result = step("Loading config", lambda: __import__('config').settings)
if not config_result or not config_result.bot_token:
    print("[FATAL] BOT_TOKEN not set!")
    input("Press Enter to exit...")
    sys.exit(1)

# Step 2: Basic aiogram imports
step("Importing aiogram Bot", lambda: __import__('aiogram').Bot)
step("Importing aiogram Dispatcher", lambda: __import__('aiogram').Dispatcher)
step("Importing MemoryStorage", lambda: __import__('aiogram.fsm.storage.memory').MemoryStorage)

# Step 3: Create basic instances
storage = None
def create_storage():
    global storage
    from aiogram.fsm.storage.memory import MemoryStorage
    storage = MemoryStorage()
    return storage
    
storage_result = step("Creating storage", create_storage)

dp = None
def create_dispatcher():
    global dp
    from aiogram import Dispatcher
    dp = Dispatcher(storage=storage)
    return dp
    
dp_result = step("Creating dispatcher", create_dispatcher)

# Step 4: Import handlers VERY CAREFULLY
def import_handlers():
    print("\n[STEP] Importing handlers...")
    sys.stdout.flush()
    try:
        # Try importing router directly
        from bot import handlers
        router = handlers.router
        print("[OK] Handlers imported successfully")
        sys.stdout.flush()
        return router
    except Exception as e:
        print(f"[ERROR] Handler import failed: {type(e).__name__}: {e}")
        traceback.print_exc()
        sys.stdout.flush()
        return None

router = import_handlers()

if router and dp_result:
    try:
        print("\n[STEP] Registering router...")
        sys.stdout.flush()
        dp.include_router(router)
        print("[OK] Router registered")
        sys.stdout.flush()
    except Exception as e:
        print(f"[ERROR] Router registration failed: {e}")
        traceback.print_exc()
        sys.stdout.flush()
        errors.append(f"Router registration: {e}")

# Step 5: Create bot
bot = None
def create_bot():
    global bot
    from aiogram import Bot
    from config import settings
    bot = Bot(token=settings.bot_token)
    return bot

bot_result = step("Creating bot instance", create_bot)

if errors:
    print(f"\n[WARNING] {len(errors)} error(s) encountered:")
    for err in errors:
        print(f"  - {err}")
    print("\nAttempting to start bot anyway...")
    sys.stdout.flush()

if bot_result and dp_result:
    print("\n" + "=" * 70)
    print("STARTING BOT...")
    print("=" * 70)
    sys.stdout.flush()
    
    async def main():
        try:
            me = await bot.get_me()
            print(f"[OK] Bot connected: @{me.username} ({me.first_name})")
            print(f"[OK] Bot ID: {me.id}")
            print("=" * 70)
            print("[READY] Bot is ready! Waiting for messages...")
            print("=" * 70)
            sys.stdout.flush()
            
            await dp.start_polling(bot, drop_pending_updates=False)
        except KeyboardInterrupt:
            print("\n[INFO] Bot stopped by user")
        except Exception as e:
            print(f"\n[FATAL] Bot error: {e}")
            traceback.print_exc()
        finally:
            await bot.session.close()
            print("[INFO] Bot session closed")
    
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Stopped")
    except Exception as e:
        print(f"\n[FATAL] Runtime error: {e}")
        traceback.print_exc()
else:
    print("\n[FATAL] Cannot start bot - critical components failed")
    print(f"Errors: {errors}")
    input("\nPress Enter to exit...")

