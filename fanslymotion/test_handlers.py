"""Test handlers import."""
import sys
import traceback

print("Testing handlers import...")
try:
    from bot.handlers import router
    print("SUCCESS: Handlers imported!")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

