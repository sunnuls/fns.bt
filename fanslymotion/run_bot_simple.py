"""Simplified bot launcher with better error handling."""
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("FANSLYMOTION BOT - SIMPLE LAUNCHER")
print("=" * 60)
sys.stdout.flush()

# Step 1: Config
print("\n[1/6] Loading config...")
sys.stdout.flush()
try:
    from config import settings
    if not settings.bot_token:
        print("❌ BOT_TOKEN not set!")
        input("Press Enter...")
        sys.exit(1)
    print("✅ Config loaded")
    sys.stdout.flush()
except Exception as e:
    print(f"❌ Config error: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter...")
    sys.exit(1)

# Step 2: Basic imports
print("[2/6] Importing aiogram (may take 15-30 seconds)...")
sys.stdout.flush()
start = time.time()
try:
    from aiogram import Bot
    from aiogram import Dispatcher
    elapsed = time.time() - start
    print(f"✅ aiogram imported in {elapsed:.1f}s")
    sys.stdout.flush()
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ aiogram import failed after {elapsed:.1f}s: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter...")
    sys.exit(1)

# Step 3: Storage
print("[3/6] Setting up storage...")
sys.stdout.flush()
try:
    from aiogram.fsm.storage.memory import MemoryStorage
    storage = MemoryStorage()
    print("✅ Storage ready")
    sys.stdout.flush()
except Exception as e:
    print(f"❌ Storage error: {e}")
    input("Press Enter...")
    sys.exit(1)

# Step 4: Handlers
print("[4/6] Loading handlers...")
sys.stdout.flush()
try:
    # Import Dispatcher first to catch pydantic errors early
    from aiogram import Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    
    # Create dispatcher instance
    temp_storage = MemoryStorage()
    temp_dp = Dispatcher(storage=temp_storage)
    print("✅ Dispatcher created")
    sys.stdout.flush()
    
    # Now import handlers
    from bot.handlers import router
    temp_dp.include_router(router)
    print("✅ Handlers loaded")
    sys.stdout.flush()
except Exception as e:
    print(f"❌ Handlers error: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter...")
    sys.exit(1)

# Step 5: Create bot and dispatcher
print("[5/6] Creating bot instance...")
sys.stdout.flush()
try:
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    print("✅ Bot instance created")
    sys.stdout.flush()
except Exception as e:
    print(f"❌ Bot creation error: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter...")
    sys.exit(1)

# Step 6: Run
print("[6/6] Starting bot...")
print("=" * 60)
sys.stdout.flush()

async def main():
    try:
        me = await bot.get_me()
        print(f"✅ Bot connected: @{me.username} ({me.first_name})")
        print(f"   Bot ID: {me.id}")
        print("=" * 60)
        print("✅ Bot is READY! Waiting for messages...")
        print("=" * 60)
        sys.stdout.flush()
        
        await dp.start_polling(bot, drop_pending_updates=False)
    except KeyboardInterrupt:
        print("\n⚠️  Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot.session.close()
        print("✅ Bot session closed")

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Stopped")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to close...")

