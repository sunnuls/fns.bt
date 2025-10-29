"""
Stable Video Diffusion (SVD) rendering module.
Handles video generation from static images using the SVD-XT model.
"""
from .renderer import SVDRenderer, VideoGenerationParams

__all__ = ["SVDRenderer", "VideoGenerationParams"]

