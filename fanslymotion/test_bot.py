#!/usr/bin/env python3
"""Quick test script to check if bot can connect to Telegram."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from aiogram import Bot

async def test_bot():
    """Test bot connection to Telegram."""
    print("Testing Telegram Bot connection...")
    print(f"BOT_TOKEN configured: {bool(settings.bot_token)}")
    
    if not settings.bot_token:
        print("ERROR: BOT_TOKEN not set!")
        return False
    
    try:
        bot = Bot(token=settings.bot_token)
        me = await bot.get_me()
        print(f"✅ Bot connected successfully!")
        print(f"   Bot name: @{me.username}")
        print(f"   Bot ID: {me.id}")
        print(f"   First name: {me.first_name}")
        await bot.session.close()
        return True
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_bot())
    sys.exit(0 if result else 1)

