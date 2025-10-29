#!/usr/bin/env python3
"""
System check script for FanslyMotion v2.0
Verifies all optimizations and requirements are properly configured.
"""
import sys
import os

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f" {text}")
    print(f"{'='*60}\n")

def check_python():
    """Check Python version."""
    print("🐍 Python Version:")
    version = sys.version_info
    print(f"   Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10:
        print("   ✅ Python version OK")
        return True
    else:
        print("   ❌ Python 3.10+ required")
        return False

def check_cuda():
    """Check CUDA availability."""
    print("\n🎮 CUDA Status:")
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            print(f"   ✅ CUDA available: {torch.version.cuda}")
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            
            # Check compute capability
            capability = torch.cuda.get_device_capability()
            print(f"   Compute capability: {capability[0]}.{capability[1]}")
            
            if capability[0] >= 8:
                print(f"   ✅ Ampere or newer - TF32 available")
            else:
                print(f"   ℹ️  Pre-Ampere - TF32 not available")
            
            return True
        else:
            print("   ❌ CUDA not available")
            return False
    except ImportError:
        print("   ❌ PyTorch not installed")
        return False

def check_packages():
    """Check required packages."""
    print("\n📦 Required Packages:")
    
    packages = {
        'torch': '2.1+',
        'torchvision': '0.16+',
        'diffusers': '0.25+',
        'transformers': '4.36+',
        'xformers': '0.0.23',
        'fastapi': '0.109+',
        'aiogram': '3.3+',
        'redis': '5.0+',
        'rq': '1.16+',
        'imageio': '2.33+',
        'opencv-python': '4.9+',
        'Pillow': '10.2+',
    }
    
    all_ok = True
    
    for package, version in packages.items():
        try:
            if package == 'opencv-python':
                module = __import__('cv2')
            elif package == 'Pillow':
                module = __import__('PIL')
            else:
                module = __import__(package)
            
            pkg_version = getattr(module, '__version__', 'unknown')
            
            if package == 'xformers':
                # xformers is critical
                print(f"   ✅ {package}: {pkg_version} (CRITICAL for performance)")
            else:
                print(f"   ✅ {package}: {pkg_version}")
                
        except ImportError:
            if package == 'xformers':
                print(f"   ⚠️  {package}: NOT INSTALLED (CRITICAL - install with: pip install xformers==0.0.23)")
                print(f"       Without xformers, generation will be 2x slower!")
            else:
                print(f"   ❌ {package}: NOT INSTALLED (required: {version})")
            all_ok = False
    
    return all_ok

def check_optimizations():
    """Check if optimizations are enabled."""
    print("\n⚡ Optimizations:")
    
    try:
        import torch
        
        # Check TF32
        if hasattr(torch.backends.cuda, 'matmul'):
            tf32_enabled = torch.backends.cuda.matmul.allow_tf32
            if tf32_enabled:
                print(f"   ✅ TF32 enabled for matmul")
            else:
                print(f"   ℹ️  TF32 not enabled (auto-enabled for Ampere+ GPUs)")
        
        # Check xformers
        try:
            import xformers
            print(f"   ✅ xformers available: {xformers.__version__}")
        except ImportError:
            print(f"   ❌ xformers NOT available - Performance will be degraded!")
            print(f"      Install with: pip install xformers==0.0.23")
        
        return True
    except ImportError:
        print("   ❌ Cannot check optimizations - PyTorch not available")
        return False

def check_config():
    """Check configuration files."""
    print("\n⚙️  Configuration:")
    
    # Check .env
    if os.path.exists('.env'):
        print("   ✅ .env file found")
        
        # Check BOT_TOKEN
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'BOT_TOKEN=' in env_content:
                if 'your_telegram_bot_token' not in env_content:
                    print("   ✅ BOT_TOKEN configured")
                else:
                    print("   ⚠️  BOT_TOKEN not set (using placeholder)")
            else:
                print("   ❌ BOT_TOKEN not found in .env")
    else:
        print("   ❌ .env file not found")
        print("      Create from env.example: copy env.example .env")
    
    # Check directories
    dirs = ['storage/hot', 'storage/archive', 'cache/models', 'cache/torch']
    for dir_path in dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path} exists")
        else:
            print(f"   ℹ️  {dir_path} not found (will be created on startup)")

def check_redis():
    """Check Redis connection."""
    print("\n🔴 Redis:")
    
    try:
        import redis
        
        # Try to connect
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
        r.ping()
        print("   ✅ Redis is running and accessible")
        
        # Check queue
        from rq import Queue
        queue = Queue(connection=r)
        print(f"   ✅ RQ Queue accessible, jobs in queue: {len(queue)}")
        
        return True
    except Exception as e:
        print(f"   ❌ Redis not accessible: {e}")
        print(f"      Start Redis with: redis-server")
        return False

def check_model():
    """Check if model is downloaded."""
    print("\n🤖 Model Status:")
    
    cache_dirs = [
        'cache/models/models--stabilityai--stable-video-diffusion-img2vid-xt',
        'cache/models/stable-video-diffusion-img2vid-xt'
    ]
    
    model_found = False
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            print(f"   ✅ Model found in: {cache_dir}")
            
            # Check size
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(cache_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            
            size_gb = total_size / (1024**3)
            print(f"   Model size: {size_gb:.2f} GB")
            
            if size_gb > 5:
                print(f"   ✅ Model appears to be complete")
            else:
                print(f"   ⚠️  Model size seems small, might be incomplete")
            
            model_found = True
            break
    
    if not model_found:
        print("   ℹ️  Model not found in cache")
        print("      Will be downloaded on first use (~7GB)")
    
    return True

def check_gpu_memory():
    """Check available GPU memory."""
    print("\n💾 GPU Memory:")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            allocated = torch.cuda.memory_allocated(0) / 1024**3
            reserved = torch.cuda.memory_reserved(0) / 1024**3
            free = total_memory - allocated
            
            print(f"   Total VRAM: {total_memory:.1f} GB")
            print(f"   Allocated: {allocated:.1f} GB")
            print(f"   Reserved: {reserved:.1f} GB")
            print(f"   Free: {free:.1f} GB")
            
            # Recommendations based on VRAM
            if total_memory >= 20:
                print(f"   ✅ Sufficient for 1080p generation")
            elif total_memory >= 16:
                print(f"   ✅ Recommended for 720p generation")
                print(f"   ⚠️  1080p might be tight")
            elif total_memory >= 12:
                print(f"   ⚠️  Recommended to use 720p or lower")
            else:
                print(f"   ⚠️  Low VRAM - use 480p or 360p")
            
            return True
        else:
            print("   ❌ No GPU available")
            return False
    except ImportError:
        print("   ❌ Cannot check GPU memory - PyTorch not available")
        return False

def print_summary(results):
    """Print summary of checks."""
    print_header("Summary")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"Checks passed: {passed}/{total}\n")
    
    for check, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    print()
    
    if passed == total:
        print("🎉 All checks passed! System is ready.")
        print("\n📚 Next steps:")
        print("   1. Make sure BOT_TOKEN is set in .env")
        print("   2. Start Redis: redis-server")
        print("   3. Run: python -m bot.bot")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\n📖 Documentation:")
        print("   - UPDATE_GUIDE.md - Update instructions")
        print("   - TROUBLESHOOTING_RU.md - Common problems")
        print("   - PERFORMANCE_TIPS.md - Optimization guide")
        return 1

def main():
    """Main check function."""
    print_header("FanslyMotion v2.0 - System Check")
    
    results = {}
    
    results['Python Version'] = check_python()
    results['CUDA'] = check_cuda()
    results['Packages'] = check_packages()
    results['Optimizations'] = check_optimizations()
    results['Configuration'] = check_config()
    results['Redis'] = check_redis()
    results['Model'] = check_model()
    results['GPU Memory'] = check_gpu_memory()
    
    exit_code = print_summary(results)
    sys.exit(exit_code)

if __name__ == '__main__':
    main()

