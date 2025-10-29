"""Quick test to see if imports work."""
import sys
import time
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 >nul 2>&1')  # UTF-8
    except:
        pass

print("[TEST] Starting import test...")
print(f"[TEST] Python: {sys.version}")
sys.stdout.flush()

print("[TEST] Importing config...")
sys.stdout.flush()
try:
    from config import settings
    print("[OK] config imported")
    sys.stdout.flush()
except Exception as e:
    print(f"[FAIL] config failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("[TEST] Importing aiogram (this may take 10-30 seconds)...")
sys.stdout.flush()
start = time.time()
try:
    from aiogram import Bot, Dispatcher
    elapsed = time.time() - start
    print(f"[OK] aiogram imported in {elapsed:.1f}s")
    sys.stdout.flush()
except Exception as e:
    elapsed = time.time() - start
    print(f"[FAIL] aiogram failed after {elapsed:.1f}s: {e}")
    import traceback
    traceback.print_exc()
    sys.stdout.flush()
    sys.exit(1)

print("[TEST] All imports OK!")
sys.stdout.flush()

