"""
Telegram bot main entry point.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings, init_storage
from bot.handlers import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main bot entry point."""
    # Initialize storage
    init_storage()
    
    # Check bot token
    if not settings.bot_token:
        logger.error("BOT_TOKEN not set in environment variables!")
        print("ERROR: BOT_TOKEN not set!")
        return
    
    # Initialize bot and dispatcher
    bot = Bot(token=settings.bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register routers
    dp.include_router(router)
    
    logger.info("🤖 Starting FanslyMotion Telegram Bot...")
    logger.info(f"📡 Backend URL: {settings.backend_url}")
    print("=" * 60)
    print("🤖 FANSLYMOTION BOT STARTING")
    print("=" * 60)
    
    # Get bot info to verify connection
    try:
        me = await bot.get_me()
        logger.info(f"✅ Bot connected: @{me.username} ({me.first_name})")
        print(f"✅ Bot connected: @{me.username} ({me.first_name})")
        print(f"   Bot ID: {me.id}")
        print(f"   Backend: {settings.backend_url}")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Telegram: {e}")
        print(f"❌ FAILED to connect to Telegram: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Register startup and shutdown handlers
    @dp.startup()
    async def on_startup():
        logger.info("🚀 Dispatcher started")
        print("🚀 Dispatcher ready to receive updates")
    
    @dp.shutdown()
    async def on_shutdown():
        logger.info("🛑 Dispatcher shutting down")
        print("🛑 Dispatcher stopped")
    
    try:
        # Start polling with explicit allowed updates
        logger.info("🔄 Starting polling...")
        print("🔄 Starting polling...")
        print("=" * 60)
        print("✅ Bot is READY! Waiting for messages...")
        print("=" * 60)
        await dp.start_polling(
            bot, 
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=False
        )
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
        print("\n⚠️  Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Polling error: {e}")
        print(f"❌ POLLING ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        traceback.print_exc()
    finally:
        await bot.session.close()
        logger.info("Bot session closed")
        print("✅ Bot session closed")


if __name__ == "__main__":
    print("=" * 70)
    print("🤖 FANSLYMOTION BOT - STARTING")
    print("=" * 70)
    try:
        print("[MAIN] Starting bot...")
        asyncio.run(main())
        print("[MAIN] Bot stopped normally")
    except KeyboardInterrupt:
        print("\n[MAIN] Bot stopped by user (Ctrl+C)")
        logger.info("Bot stopped by user")
    except Exception as e:
        print(f"\n[MAIN] FATAL ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        print("\nPress Enter to close...")
        try:
            input()
        except:
            pass

