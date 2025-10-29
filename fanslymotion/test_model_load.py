"""
Simple test to check if model loads successfully
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 50)
print("Testing SVD Model Loading")
print("=" * 50)
print()

try:
    import torch
    print(f"[OK] PyTorch imported: {torch.__version__}")
    
    if torch.cuda.is_available():
        print(f"[OK] CUDA available: {torch.cuda.get_device_name(0)}")
        print(f"     VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        print("[ERROR] CUDA not available!")
        sys.exit(1)
    
    print()
    print("Loading SVD renderer...")
    
    from svd.renderer import get_renderer
    from config import settings
    
    print(f"Model cache: {settings.svd_model_cache}")
    print()
    
    # Try to load the model
    renderer = get_renderer(
        model_id=settings.svd_model_id,
        cache_dir=settings.svd_model_cache
    )
    
    print()
    print("[SUCCESS] Model loaded successfully!")
    print(f"Device: {renderer.device}")
    print(f"VRAM allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
    print()
    print("Bot is ready to generate videos!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)




