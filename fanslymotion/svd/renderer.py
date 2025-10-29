"""
SVD Renderer module for generating videos from images.
Uses Stable Video Diffusion XT model with CUDA acceleration.
Enhanced with advanced optimizations for maximum quality and performance.
"""
import torch
import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
from typing import Optional, Tuple
from dataclasses import dataclass
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video
import imageio
import cv2


@dataclass
class VideoGenerationParams:
    """Parameters for video generation."""
    image_path: Path
    output_path: Path
    duration: int  # seconds
    resolution: Tuple[int, int]  # (width, height)
    motion_preset: str
    fps: int = 24  # Increased from 12 to 24 for smoother video
    steps: int = 40  # Increased from 24 to 40 for better quality
    guidance_scale: float = 1.0
    noise_aug_strength: float = 0.1
    motion_bucket_id: int = 127
    enhance_output: bool = True  # Enable post-processing enhancements


class SVDRenderer:
    """
    Stable Video Diffusion renderer for image-to-video generation.
    
    This class handles loading the SVD-XT model and generating videos
    from static images with various motion presets and resolutions.
    """
    
    def __init__(self, model_id: str = "stabilityai/stable-video-diffusion-img2vid-xt",
                 cache_dir: Optional[Path] = None,
                 device: str = "cuda"):
        """
        Initialize the SVD renderer.
        
        Args:
            model_id: HuggingFace model identifier
            cache_dir: Directory to cache model files
            device: Device to run inference on ('cuda' or 'cpu')
        """
        self.model_id = model_id
        self.cache_dir = cache_dir
        self.device = device
        self.pipeline = None
        
        # Check CUDA availability
        if device == "cuda" and not torch.cuda.is_available():
            print("[WARNING] CUDA not available, falling back to CPU")
            self.device = "cpu"
    
    def load_model(self):
        """Load the SVD pipeline with half precision and maximum optimizations."""
        if self.pipeline is not None:
            return
        
        print(f"[LOADING] SVD model: {self.model_id}")
        
        # Load pipeline with optimal settings for RTX GPU
        self.pipeline = StableVideoDiffusionPipeline.from_pretrained(
            self.model_id,
            cache_dir=self.cache_dir,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            variant="fp16" if self.device == "cuda" else None,
        )
        
        # Enable advanced optimizations BEFORE moving to device
        if self.device == "cuda":
            # Check VRAM - use CPU offload ONLY if absolutely necessary
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"[INFO] GPU VRAM: {vram_gb:.1f}GB")
            
            # For RTX 4080 Laptop (12GB) - use regular CPU offload (more stable than sequential)
            if vram_gb < 16:
                # Use regular CPU offload for 12GB VRAM to prevent OOM
                try:
                    # Regular CPU offload is more stable than sequential
                    self.pipeline.enable_model_cpu_offload()
                    print(f"[OK] Enabled CPU offload for {vram_gb:.1f}GB VRAM")
                    print(f"[INFO] CPU offload prevents OOM by moving components to CPU when not needed")
                except Exception as e:
                    print(f"[ERROR] CPU offload failed: {e}")
                    print(f"[ERROR] This will likely cause OOM errors!")
                    # Only use GPU directly as last resort
                    self.pipeline.to(self.device)
            else:
                # 16GB+ VRAM - use GPU directly for better performance
                self.pipeline.to(self.device)
                print(f"[OK] Model loaded on GPU (no CPU offload for better performance)")
            
            # Enable attention slicing for better VRAM management (CRITICAL for 12GB VRAM)
            # But use larger slice size to avoid CUDA config errors
            try:
                # Use slice_size=2 instead of 1 to avoid "invalid configuration argument" error
                self.pipeline.enable_attention_slicing(2)  # Slice size 2 for memory savings + stability
                print("[OK] Enabled attention slicing (slice_size=2)")
            except Exception as e:
                print(f"[WARN] Attention slicing failed: {e}")
                # Try disabling attention slicing completely if it causes issues
                try:
                    self.pipeline.disable_attention_slicing()
                    print("[INFO] Disabled attention slicing to avoid CUDA errors")
                except:
                    pass
            
            # Enable VAE slicing for lower memory usage during decoding (CRITICAL for 12GB VRAM)
            if hasattr(self.pipeline, 'vae'):
                try:
                    self.pipeline.vae.enable_slicing()
                    self.pipeline.vae.enable_tiling()  # Additional tiling for large images
                    print("[OK] Enabled VAE slicing and tiling")
                except Exception as e:
                    print(f"[WARN] VAE optimization failed: {e}")
        else:
            self.pipeline.to(self.device)
        
        # Additional optimizations after device placement
        if self.device == "cuda":
            # DISABLE xformers - it causes "CUDA error: invalid configuration argument"
            # on RTX 4080 Laptop with SVD model
            # Use PyTorch native scaled_dot_product_attention instead
            print("[INFO] Skipping xformers (causes CUDA errors with this GPU/model combo)")
            print("[INFO] Using PyTorch native attention mechanism")
            
            # Explicitly disable xformers if it was enabled elsewhere
            try:
                if hasattr(self.pipeline, 'disable_xformers_memory_efficient_attention'):
                    self.pipeline.disable_xformers_memory_efficient_attention()
                    print("[OK] xformers explicitly disabled")
            except:
                pass
            
            # Enable TF32 for Ampere GPUs (RTX 30xx, 40xx) - faster computation
            try:
                if torch.cuda.get_device_capability()[0] >= 8:
                    torch.backends.cuda.matmul.allow_tf32 = True
                    torch.backends.cudnn.allow_tf32 = True
                    print("[OK] Enabled TF32 for faster computation")
            except Exception as e:
                print(f"[WARN] TF32 setup failed: {e}")
            
            print("[OK] All optimizations enabled")
        
        print(f"[OK] Model loaded on {self.device}")
        print(f"     VRAM usage: ~{torch.cuda.memory_allocated() / 1024**3:.2f} GB")
    
    def preprocess_image(self, image_path: Path, target_size: Tuple[int, int]) -> Image.Image:
        """
        Load and preprocess input image to target resolution with quality enhancements.
        
        Args:
            image_path: Path to input image
            target_size: Target (width, height) tuple
            
        Returns:
            Preprocessed PIL Image with enhanced quality
        """
        # Load image
        image = load_image(str(image_path))
        
        # Resize to target resolution maintaining aspect ratio
        image = image.convert("RGB")
        
        # Calculate aspect-preserving resize
        img_width, img_height = image.size
        target_width, target_height = target_size
        
        # Resize and center crop
        aspect_ratio = img_width / img_height
        target_aspect = target_width / target_height
        
        if aspect_ratio > target_aspect:
            # Image is wider - fit to height
            new_height = target_height
            new_width = int(target_height * aspect_ratio)
        else:
            # Image is taller - fit to width
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
        
        # Use LANCZOS for high-quality downsampling
        image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Center crop to exact target size
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        image = image.crop((left, top, right, bottom))
        
        # Enhance image quality before processing
        # Slight sharpening
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        # Slight color enhancement
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.05)
        
        return image
    
    def enhance_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply post-processing enhancements to a single frame.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            Enhanced frame
        """
        # Convert to float for processing
        frame_float = frame.astype(np.float32) / 255.0
        
        # Apply bilateral filter to reduce noise while preserving edges
        frame_filtered = cv2.bilateralFilter(
            (frame_float * 255).astype(np.uint8), 
            d=5, 
            sigmaColor=10, 
            sigmaSpace=10
        )
        
        # Slight sharpening using unsharp mask
        gaussian = cv2.GaussianBlur(frame_filtered, (0, 0), 2.0)
        sharpened = cv2.addWeighted(frame_filtered, 1.5, gaussian, -0.5, 0)
        
        # Ensure values are in valid range
        sharpened = np.clip(sharpened, 0, 255)
        
        return sharpened.astype(np.uint8)
    
    def apply_motion_preset(self, preset: str) -> dict:
        """
        Get motion parameters for a specific preset.
        
        Args:
            preset: Motion preset name
            
        Returns:
            Dictionary with motion parameters
        """
        motion_configs = {
            "micro": {
                "motion_bucket_id": 50,
                "noise_aug_strength": 0.05,
            },
            "pan_l": {
                "motion_bucket_id": 100,
                "noise_aug_strength": 0.1,
            },
            "pan_r": {
                "motion_bucket_id": 100,
                "noise_aug_strength": 0.1,
            },
            "tilt_up": {
                "motion_bucket_id": 100,
                "noise_aug_strength": 0.1,
            },
            "tilt_down": {
                "motion_bucket_id": 100,
                "noise_aug_strength": 0.1,
            },
            "dolly_in": {
                "motion_bucket_id": 127,
                "noise_aug_strength": 0.15,
            },
        }
        
        return motion_configs.get(preset, motion_configs["micro"])
    
    def generate_video(self, params: VideoGenerationParams, progress_callback=None) -> Path:
        """
        Generate video from image using SVD model.
        
        Args:
            params: Video generation parameters
            progress_callback: Optional callback function(step, total_steps) for progress updates
            
        Returns:
            Path to generated video file
        """
        # Ensure model is loaded
        self.load_model()
        
        print(f"[GENERATING] Video: {params.duration}s @ {params.resolution[0]}x{params.resolution[1]}")
        
        # Preprocess input image
        image = self.preprocess_image(params.image_path, params.resolution)
        
        # Apply motion preset
        motion_config = self.apply_motion_preset(params.motion_preset)
        
        # Calculate number of frames
        num_frames = params.duration * params.fps
        
        # Generate video frames using the pipeline
        print(f"[INFERENCE] Running with {params.steps} steps, {num_frames} frames...")
        print(f"            Motion bucket: {motion_config['motion_bucket_id']}, Noise: {motion_config.get('noise_aug_strength', params.noise_aug_strength)}")
        
        # Create callback wrapper for progress
        def step_callback(pipe, step_index, timestep, callback_kwargs):
            if progress_callback:
                progress_callback(step_index + 1, params.steps)
            print(f"   Step {step_index + 1}/{params.steps} completed")
            return callback_kwargs
        
        # Force GPU usage for inference
        import torch
        if torch.cuda.is_available():
            print(f"[GPU] Before generation: {torch.cuda.memory_allocated() / 1024**3:.2f}GB allocated")
            print(f"[GPU] Starting inference - GPU should be at 80-100% now!")
        
        # Validate inputs before pipeline call
        print(f"[VALIDATE] Checking inputs before pipeline call...")
        print(f"   Image type: {type(image)}, Size: {image.size if hasattr(image, 'size') else 'N/A'}")
        print(f"   Num frames: {num_frames}, Steps: {params.steps}, FPS: {params.fps}")
        print(f"   Motion bucket: {motion_config['motion_bucket_id']}, Noise: {motion_config.get('noise_aug_strength', params.noise_aug_strength)}")
        print(f"   Pipeline device: {self.device}, Pipeline type: {type(self.pipeline)}")
        
        if self.pipeline is None:
            raise RuntimeError("Pipeline not loaded! Call load_model() first.")
        
        # Ensure image is PIL Image
        if not isinstance(image, Image.Image):
            print(f"[WARN] Image is not PIL.Image, converting...")
            if isinstance(image, (np.ndarray, torch.Tensor)):
                image = Image.fromarray(np.array(image))
            else:
                raise TypeError(f"Expected PIL.Image, got {type(image)}")
        
        try:
            with torch.inference_mode():
                # NEVER call pipeline.to() when using CPU offload - it causes meta tensor errors
                # Sequential CPU offload handles device placement automatically
                print("[INFO] Using CPU offload - pipeline device placement is automatic")
                print("[INFO] DO NOT manually move pipeline to GPU with CPU offload!")
                
                print(f"[INFERENCE] Calling pipeline.generate()...")
                
                # Call pipeline with error handling
                try:
                    result = self.pipeline(
                        image=image,
                        num_frames=num_frames,
                        num_inference_steps=params.steps,
                        fps=params.fps,
                        motion_bucket_id=motion_config["motion_bucket_id"],
                        noise_aug_strength=motion_config.get("noise_aug_strength", params.noise_aug_strength),
                        decode_chunk_size=4,  # Reduced from 8 to 4 for less memory usage
                        callback_on_step_end=step_callback,
                        callback_on_step_end_tensor_inputs=["latents"],
                    )
                    
                    print(f"[INFERENCE] Pipeline call completed, extracting frames...")
                    frames = result.frames[0]
                    print(f"[INFERENCE] Got {len(frames)} frames")
                    
                except RuntimeError as e:
                    error_msg = str(e)
                    print(f"[ERROR] RuntimeError in pipeline call: {error_msg}")
                    
                    # Check for CUDA/OOM errors
                    if "CUDA" in error_msg or "out of memory" in error_msg.lower():
                        print(f"[ERROR] GPU memory issue detected!")
                        if torch.cuda.is_available():
                            print(f"[ERROR] GPU memory allocated: {torch.cuda.memory_allocated() / 1024**3:.2f}GB")
                            print(f"[ERROR] GPU memory reserved: {torch.cuda.memory_reserved() / 1024**3:.2f}GB")
                        raise RuntimeError(f"GPU memory error: {error_msg}. Try reducing resolution or duration.")
                    
                    # Check for configuration errors
                    if "invalid configuration" in error_msg.lower() or "configuration argument" in error_msg.lower():
                        print(f"[ERROR] CUDA configuration error - this might be xformers issue")
                        print(f"[ERROR] Try disabling xformers or restarting worker")
                        raise RuntimeError(f"CUDA configuration error: {error_msg}")
                    
                    # Re-raise other runtime errors
                    raise
                    
                except Exception as e:
                    error_msg = str(e)
                    error_type = type(e).__name__
                    print(f"[ERROR] Unexpected error in pipeline call: {error_type}: {error_msg}")
                    print(f"[ERROR] Error details: {repr(e)}")
                    raise RuntimeError(f"Pipeline generation failed: {error_type}: {error_msg}") from e
        
        except Exception as pipeline_error:
            # Log full error context
            print(f"[FATAL] Video generation pipeline failed!")
            print(f"[FATAL] Error type: {type(pipeline_error).__name__}")
            print(f"[FATAL] Error message: {str(pipeline_error)}")
            
            # Additional diagnostics
            if torch.cuda.is_available():
                print(f"[DIAG] GPU memory after error:")
                print(f"   Allocated: {torch.cuda.memory_allocated() / 1024**3:.2f}GB")
                print(f"   Reserved: {torch.cuda.memory_reserved() / 1024**3:.2f}GB")
                print(f"   Max allocated: {torch.cuda.max_memory_allocated() / 1024**3:.2f}GB")
            
            # Re-raise with more context
            raise
        
        # Clear GPU cache after generation to prevent memory leak
        if torch.cuda.is_available():
            print(f"[GPU] After generation: {torch.cuda.memory_allocated() / 1024**3:.2f}GB allocated")
            print(f"[GPU] Clearing cache to prevent memory leaks...")
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            print(f"[GPU] After cleanup: {torch.cuda.memory_allocated() / 1024**3:.2f}GB allocated")
        
        # Save video to file using imageio with ffmpeg
        print(f"[SAVING] Video to {params.output_path}")
        
        # Ensure output directory exists
        params.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert frames to numpy arrays and apply enhancements
        frame_array = []
        for idx, frame in enumerate(frames):
            if isinstance(frame, Image.Image):
                frame_np = np.array(frame)
            else:
                frame_np = frame
            
            # Apply post-processing enhancements if enabled
            if params.enhance_output:
                frame_np = self.enhance_frame(frame_np)
            
            frame_array.append(frame_np)
        
        print(f"[ENCODING] Using high-quality H.264 encoding...")
        
        # Save as MP4 using imageio-ffmpeg with maximum quality settings
        imageio.mimsave(
            str(params.output_path),
            frame_array,
            fps=params.fps,
            codec='libx264',
            quality=10,  # Maximum quality (0-10 scale)
            pixelformat='yuv420p',
            macro_block_size=1,
            ffmpeg_params=[
                '-crf', '18',  # Constant Rate Factor (lower = better quality, 18 is visually lossless)
                '-preset', 'slow',  # Slower encoding for better compression
                '-tune', 'film',  # Optimize for film content
                '-movflags', '+faststart',  # Enable fast start for web playback
            ]
        )
        
        print(f"[SUCCESS] Video generated: {params.output_path}")
        print(f"           Frames: {len(frame_array)}, FPS: {params.fps}, Duration: {params.duration}s")
        
        return params.output_path
    
    def cleanup(self):
        """Free up GPU memory by unloading the model."""
        if self.pipeline is not None:
            print("[CLEANUP] Unloading model and clearing memory...")
            
            # Properly unload CPU offload if enabled
            try:
                if hasattr(self.pipeline, 'disable_model_cpu_offload'):
                    self.pipeline.disable_model_cpu_offload()
                    print("[CLEANUP] Disabled CPU offload")
            except:
                pass
            
            # Delete pipeline
            del self.pipeline
            self.pipeline = None
            
            # Clear GPU memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
                print(f"[CLEANUP] GPU memory after cleanup: {torch.cuda.memory_allocated() / 1024**3:.2f}GB")
            
            print("[CLEANUP] Model unloaded and memory cleared")


# Singleton instance for worker usage
_renderer_instance: Optional[SVDRenderer] = None


def get_renderer(model_id: str = "stabilityai/stable-video-diffusion-img2vid-xt",
                 cache_dir: Optional[Path] = None) -> SVDRenderer:
    """
    Get or create singleton renderer instance.
    
    Args:
        model_id: HuggingFace model identifier
        cache_dir: Cache directory for models
        
    Returns:
        SVDRenderer instance
    """
    global _renderer_instance
    
    if _renderer_instance is None:
        print("[RENDERER] Creating new renderer instance...")
        _renderer_instance = SVDRenderer(model_id=model_id, cache_dir=cache_dir)
        _renderer_instance.load_model()
        print("[RENDERER] Renderer instance created and model loaded")
    else:
        print("[RENDERER] Using existing renderer instance")
    
    return _renderer_instance

