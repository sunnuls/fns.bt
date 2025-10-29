"""
Setup verification script to check if all dependencies are installed correctly.
Run this after installing dependencies to verify the setup.
"""
import sys
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported."""
    print("🔍 Testing package imports...\n")
    
    tests = {
        "FastAPI": lambda: __import__("fastapi"),
        "Uvicorn": lambda: __import__("uvicorn"),
        "Aiogram": lambda: __import__("aiogram"),
        "Redis": lambda: __import__("redis"),
        "RQ": lambda: __import__("rq"),
        "PyTorch": lambda: __import__("torch"),
        "Diffusers": lambda: __import__("diffusers"),
        "Transformers": lambda: __import__("transformers"),
        "Pillow": lambda: __import__("PIL"),
        "ImageIO": lambda: __import__("imageio"),
        "OpenCV": lambda: __import__("cv2"),
        "NumPy": lambda: __import__("numpy"),
        "Pydantic": lambda: __import__("pydantic"),
        "HTTPX": lambda: __import__("httpx"),
        "Dotenv": lambda: __import__("dotenv"),
    }
    
    passed = 0
    failed = 0
    
    for name, test_func in tests.items():
        try:
            test_func()
            print(f"✅ {name:20s} OK")
            passed += 1
        except ImportError as e:
            print(f"❌ {name:20s} FAILED - {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")
    
    return failed == 0


def test_cuda():
    """Test CUDA availability."""
    print("🎮 Testing CUDA availability...\n")
    
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            print(f"✅ CUDA is available")
            print(f"   GPU Device: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA Version: {torch.version.cuda}")
            print(f"   PyTorch Version: {torch.__version__}")
            
            # Test GPU memory
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"   Total GPU Memory: {gpu_memory:.2f} GB")
            
            # Recommendation based on memory
            if gpu_memory >= 12:
                print("\n   💡 Your GPU can handle 1080p generation")
            elif gpu_memory >= 8:
                print("\n   💡 Your GPU is suitable for 720p generation")
            else:
                print("\n   ⚠️  Your GPU has limited VRAM - recommend 360p/480p")
        else:
            print("⚠️  CUDA not available - will use CPU (very slow)")
            print("   Install CUDA: https://developer.nvidia.com/cuda-downloads")
        
        return cuda_available
    except Exception as e:
        print(f"❌ Error checking CUDA: {e}")
        return False


def test_redis():
    """Test Redis connection."""
    print("\n🔌 Testing Redis connection...\n")
    
    try:
        import redis
        from config import settings
        
        r = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db
        )
        
        # Ping Redis
        r.ping()
        print(f"✅ Redis is running at {settings.redis_host}:{settings.redis_port}")
        
        # Get Redis info
        info = r.info()
        print(f"   Redis Version: {info['redis_version']}")
        print(f"   Connected Clients: {info['connected_clients']}")
        
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("   Start Redis: redis-server")
        print("   Download: https://github.com/microsoftarchive/redis/releases")
        return False


def test_directories():
    """Test if required directories exist."""
    print("\n📁 Checking directories...\n")
    
    from config import settings
    
    dirs = {
        "Hot Storage": settings.storage_hot_path,
        "Archive Storage": settings.storage_archive_path,
        "Torch Cache": settings.torch_home,
        "Model Cache": settings.svd_model_cache,
    }
    
    all_exist = True
    for name, path in dirs.items():
        if path.exists():
            print(f"✅ {name:20s} {path}")
        else:
            print(f"⚠️  {name:20s} {path} (will be created)")
            path.mkdir(parents=True, exist_ok=True)
            print(f"   Created: {path}")
    
    return True


def test_env():
    """Test environment configuration."""
    print("\n⚙️  Checking environment...\n")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("   Copy env.example to .env and configure it")
        return False
    
    from config import settings
    
    checks = {
        "BOT_TOKEN": settings.bot_token,
        "BACKEND_URL": settings.backend_url,
        "REDIS_URL": settings.redis_url,
    }
    
    all_ok = True
    for name, value in checks.items():
        if value and value != "your_telegram_bot_token_here":
            print(f"✅ {name:20s} configured")
        else:
            print(f"⚠️  {name:20s} not configured")
            all_ok = False
    
    if not all_ok:
        print("\n   Please configure .env file with your settings")
    
    return all_ok


def main():
    """Run all tests."""
    print("="*60)
    print("      FanslyMotion Setup Verification")
    print("="*60)
    print()
    
    results = {
        "Imports": test_imports(),
        "CUDA": test_cuda(),
        "Redis": test_redis(),
        "Directories": test_directories(),
        "Environment": test_env(),
    }
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s} {status}")
    
    all_passed = all(results.values())
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("  1. Configure .env with your BOT_TOKEN")
        print("  2. Run: .\\run_local.ps1")
        print("  3. Start using your Telegram bot!")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("   Refer to README.md for detailed setup instructions.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

