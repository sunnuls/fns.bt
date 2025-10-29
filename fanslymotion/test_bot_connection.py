"""Test bot connection to Telegram API."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from aiogram import Bot

async def test_connection():
    """Test bot connection."""
    print("=" * 50)
    print("Testing Bot Connection...")
    print("=" * 50)
    
    if not settings.bot_token:
        print("❌ BOT_TOKEN not set in environment!")
        return False
    
    print(f"✅ BOT_TOKEN found: {settings.bot_token[:10]}...")
    
    try:
        bot = Bot(token=settings.bot_token)
        print("✅ Bot instance created")
        
        print("🔄 Connecting to Telegram API...")
        me = await bot.get_me()
        
        print(f"✅ Bot connected successfully!")
        print(f"   Username: @{me.username}")
        print(f"   Name: {me.first_name} {me.last_name or ''}")
        print(f"   ID: {me.id}")
        print(f"   Can join groups: {me.can_join_groups}")
        print(f"   Can read all group messages: {me.can_read_all_group_messages}")
        
        await bot.session.close()
        print("✅ Session closed")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        print(traceback.format_exc())
        print("=" * 50)
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    sys.exit(0 if result else 1)

