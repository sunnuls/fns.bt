"""
Test model download with progress tracking
"""
import torch
from diffusers import StableVideoDiffusionPipeline
from tqdm import tqdm
import sys

print("=" * 50)
print("Testing SVD Model Download")
print("=" * 50)
print()

# Check CUDA
if torch.cuda.is_available():
    print(f"[OK] CUDA available: {torch.cuda.get_device_name(0)}")
    print(f"     VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print("[ERROR] CUDA not available!")
    sys.exit(1)

print()
print("Downloading SVD-XT model (this may take 10-60 minutes on first run)...")
print("Model size: ~15 GB")
print()

try:
    pipeline = StableVideoDiffusionPipeline.from_pretrained(
        "stabilityai/stable-video-diffusion-img2vid-xt",
        torch_dtype=torch.float16,
        variant="fp16",
        cache_dir="./cache/models",
    )
    
    print()
    print("[OK] Model downloaded successfully!")
    print()
    
    print("Loading to GPU...")
    pipeline.to("cuda")
    
    # Enable optimizations
    pipeline.enable_attention_slicing()
    
    print(f"[OK] Model loaded to GPU")
    print(f"     VRAM usage: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
    print()
    print("SUCCESS! Model is ready to use.")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

