"""
Bot message and callback handlers.
"""
import base64
import asyncio
import logging
from io import BytesIO
from typing import Optional

import httpx

logger = logging.getLogger(__name__)
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from config import settings, VideoConfig
from bot.states import VideoGenerationStates
from bot.keyboards import (
    get_main_menu_keyboard, get_duration_keyboard, get_resolution_keyboard,
    get_style_keyboard, get_quality_mode_keyboard, get_motion_keyboard, 
    get_prompt_keyboard, get_cancel_keyboard, get_back_to_menu_keyboard
)

# Create router
router = Router()

# HTTP client for API requests
http_client = httpx.AsyncClient(timeout=30.0)


async def poll_job_status(job_id: str, message: Message) -> Optional[dict]:
    """
    Poll job status and update user with progress.
    
    Args:
        job_id: Job identifier
        message: Message to edit with progress updates
        
    Returns:
        Job result dictionary or None on failure
    """
    progress_msg = None
    last_progress = -1
    retry_count = 0
    max_retries = VideoConfig.RETRY_COUNT
    max_poll_time = VideoConfig.TIMEOUT  # Maximum time to poll (10 minutes)
    start_time = asyncio.get_event_loop().time()
    
    while retry_count < max_retries:
        # Check if we've exceeded maximum polling time
        elapsed_time = asyncio.get_event_loop().time() - start_time
        if elapsed_time > max_poll_time:
            await message.answer(f"⏱️ Processing took longer than {max_poll_time // 60} minutes. Please try again with lower settings.")
            return None
        try:
            # Get job status
            response = await http_client.get(f"{settings.backend_url}/job/status/{job_id}")
            response.raise_for_status()
            status_data = response.json()
            
            status = status_data.get("status")
            progress = status_data.get("progress") or 0
            queue_position = status_data.get("queue_position")
            
            # Update progress if changed - only update if content actually changed
            current_text_hash = None
            if progress != last_progress or queue_position:
                # Ensure progress is a number
                progress_int = int(progress) if progress is not None else 0
                progress_bar = "█" * int(progress_int / 10) + "░" * (10 - int(progress_int / 10))
                
                # Get status message and truncate to prevent Telegram errors (max 4096 chars)
                status_msg = status_data.get('message') or ''  # Ensure it's a string, not None
                if not isinstance(status_msg, str):
                    status_msg = str(status_msg) if status_msg else ''
                if len(status_msg) > 150:  # Limit status message
                    status_msg = status_msg[:147] + "..."
                
                if queue_position:
                    new_text = f"⏳ Queue: {queue_position}\n[{progress_bar}] {progress:.0f}%"
                else:
                    # Keep text short - Telegram has 4096 char limit
                    new_text = f"🎬 {progress:.0f}%\n[{progress_bar}]"
                    if status_msg and isinstance(status_msg, str) and len(status_msg) > 0:
                        # Add status message if there's room
                        temp_text = new_text + f"\n{status_msg}"
                        if len(temp_text) <= 4090:  # Safety margin
                            new_text = temp_text
                
                # Final safety check - ensure text doesn't exceed Telegram limit
                if isinstance(new_text, str) and len(new_text) > 4090:
                    new_text = new_text[:4087] + "..."
                
                # Only update if text actually changed (to avoid "message is not modified" error)
                current_text_hash = hash(new_text)
                if not hasattr(poll_job_status, 'last_text_hash') or poll_job_status.last_text_hash != current_text_hash:
                    try:
                        if progress_msg:
                            await progress_msg.edit_text(new_text)
                        else:
                            progress_msg = await message.answer(new_text)
                        poll_job_status.last_text_hash = current_text_hash
                    except Exception as e:
                        error_str = str(e)
                        # Ignore "message is not modified" error - it's harmless
                        if "message is not modified" not in error_str.lower():
                            logger.warning(f"Failed to update progress: {error_str}")
                            try:
                                # Fallback to minimal message only if different
                                short_text = f"🎬 {progress:.0f}%"
                                if not hasattr(poll_job_status, 'last_short_hash') or poll_job_status.last_short_hash != hash(short_text):
                                    if progress_msg:
                                        await progress_msg.edit_text(short_text)
                                    else:
                                        progress_msg = await message.answer(short_text)
                                    poll_job_status.last_short_hash = hash(short_text)
                            except:
                                pass
                
                last_progress = progress
            
            # Check if completed
            if status == "completed":
                return status_data
            elif status == "failed":
                error = status_data.get("error") or "Unknown error"
                # Ensure error is a string
                if not isinstance(error, str):
                    error = str(error) if error else "Unknown error"
                # Truncate error message to avoid "message too long" error
                if len(error) > 1000:
                    error = error[:997] + "..."
                error_text = f"❌ Technical error. Credits refunded.\n\nError: {error}"
                # Final safety check
                if len(error_text) > 4090:
                    error_text = error_text[:4087] + "..."
                await message.answer(error_text)
                return None
            
            # Wait before next poll
            await asyncio.sleep(3)
            
        except Exception as e:
            error_msg = str(e) if e else "Unknown error"
            logger.error(f"Error polling job status: {error_msg}")
            print(f"Error polling job status: {error_msg}")
            retry_count += 1
            
            if retry_count >= max_retries:
                logger.error(f"Max retries ({max_retries}) exceeded for job {job_id}")
                await message.answer("❌ Превышено максимальное количество попыток. Попробуйте позже.")
                return None
            
            await asyncio.sleep(VideoConfig.RETRY_DELAY * retry_count)  # Exponential backoff
    
    await message.answer("⏱️ Job timed out. Credits refunded.")
    return None


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    import logging
    logger = logging.getLogger(__name__)
    
    user = message.from_user
    logger.info(f"📥 /start command from user @{user.username} (ID: {user.id})")
    print(f"[HANDLER] /start from @{user.username or user.id}")
    
    try:
        await state.clear()
        
        welcome_text = (
            "🎬 <b>Welcome to FanslyMotion v2.0!</b>\n\n"
            "Transform your photos into <b>stunning AI videos</b> with professional quality!\n\n"
            "✨ <b>New Features:</b>\n"
            "• 🎨 <b>8 Visual Styles</b> (Anime, Comic, 3D, Cinematic, etc)\n"
            "• 💎 <b>3 Quality Modes</b> (Fast, Standard, Smooth)\n"
            "• 🎬 <b>8 Motion Presets</b> (Pan, Tilt, Dolly, Dynamic)\n"
            "• 💬 <b>Custom Prompts</b> to describe your vision\n"
            "• ⚡ <b>2x Faster</b> with xformers optimization\n"
            "• 📺 <b>Multiple Resolutions</b> (360p - 1080p)\n\n"
            "<b>Quality:</b> 11/10 ⭐⭐⭐ | <b>Speed:</b> +150% 🚀\n\n"
            "Select an option below to get started:"
        )
        
        sent = await message.answer(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        logger.info(f"✅ Welcome message sent to @{user.username}")
        print(f"[HANDLER] ✅ Welcome sent to @{user.username or user.id}")
    except Exception as e:
        logger.error(f"❌ Error in /start handler: {e}")
        print(f"[HANDLER] ❌ ERROR in /start: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.callback_query(F.data == "start_generation")
async def start_generation(callback: CallbackQuery, state: FSMContext):
    """Start video generation flow."""
    await callback.answer()
    
    text = (
        "🎬 <b>Create Video from Photo</b>\n\n"
        "Step 1 of 4: Select video duration\n\n"
        "Choose how long you want your video to be:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_duration_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(VideoGenerationStates.waiting_for_duration)


@router.callback_query(VideoGenerationStates.waiting_for_duration, F.data.startswith("duration_"))
async def select_duration(callback: CallbackQuery, state: FSMContext):
    """Handle duration selection."""
    await callback.answer()
    
    duration = int(callback.data.split("_")[1])
    await state.update_data(duration=duration)
    
    text = (
        f"✅ Duration: <b>{duration} seconds</b>\n\n"
        "Step 2 of 4: Select video resolution\n\n"
        "Choose the output quality:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_resolution_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(VideoGenerationStates.waiting_for_resolution)


@router.callback_query(VideoGenerationStates.waiting_for_resolution, F.data.startswith("resolution_"))
async def select_resolution(callback: CallbackQuery, state: FSMContext):
    """Handle resolution selection."""
    await callback.answer()
    
    resolution = callback.data.split("_")[1]
    await state.update_data(resolution=resolution)
    
    data = await state.get_data()
    
    text = (
        f"✅ Duration: <b>{data['duration']}s</b>\n"
        f"✅ Resolution: <b>{resolution}</b>\n\n"
        "Step 3 of 7: Select Visual Style 🎨\n\n"
        "Choose the artistic style for your video:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_style_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(VideoGenerationStates.waiting_for_style)


@router.callback_query(VideoGenerationStates.waiting_for_style, F.data.startswith("style_"))
async def select_style(callback: CallbackQuery, state: FSMContext):
    """Handle visual style selection."""
    await callback.answer()
    
    style = callback.data.split("_")[1]
    await state.update_data(visual_style=style)
    
    data = await state.get_data()
    style_desc = VideoConfig.VISUAL_STYLES.get(style, {}).get("description", style)
    
    text = (
        f"✅ Duration: <b>{data['duration']}s</b>\n"
        f"✅ Resolution: <b>{data['resolution']}</b>\n"
        f"✅ Style: <b>{style_desc}</b>\n\n"
        "Step 4 of 7: Select Quality Mode 💎\n\n"
        "Choose generation speed and quality:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_quality_mode_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(VideoGenerationStates.waiting_for_quality_mode)


@router.callback_query(VideoGenerationStates.waiting_for_quality_mode, F.data.startswith("quality_"))
async def select_quality_mode(callback: CallbackQuery, state: FSMContext):
    """Handle quality mode selection."""
    await callback.answer()
    
    quality_mode = callback.data.split("_")[1]
    await state.update_data(quality_mode=quality_mode)
    
    data = await state.get_data()
    style_desc = VideoConfig.VISUAL_STYLES.get(data.get('visual_style'), {}).get("description", "Realistic")
    mode_desc = VideoConfig.QUALITY_MODES.get(quality_mode, {}).get("description", quality_mode)
    
    text = (
        f"✅ Duration: <b>{data['duration']}s</b>\n"
        f"✅ Resolution: <b>{data['resolution']}</b>\n"
        f"✅ Style: <b>{style_desc}</b>\n"
        f"✅ Quality: <b>{mode_desc}</b>\n\n"
        "Step 5 of 7: Select Motion Preset 🎬\n\n"
        "Choose how your video should move:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_motion_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(VideoGenerationStates.waiting_for_motion)


@router.callback_query(VideoGenerationStates.waiting_for_motion, F.data.startswith("motion_"))
async def select_motion(callback: CallbackQuery, state: FSMContext):
    """Handle motion preset selection."""
    await callback.answer()
    
    motion_preset = callback.data.split("_", 1)[1]
    await state.update_data(motion_preset=motion_preset)
    
    data = await state.get_data()
    
    motion_desc = VideoConfig.MOTION_PRESETS[motion_preset]["description"]
    style_desc = VideoConfig.VISUAL_STYLES.get(data.get('visual_style'), {}).get("description", "Realistic")
    mode_desc = VideoConfig.QUALITY_MODES.get(data.get('quality_mode'), {}).get("description", "Standard")
    
    text = (
        f"✅ Duration: <b>{data['duration']}s</b>\n"
        f"✅ Resolution: <b>{data['resolution']}</b>\n"
        f"✅ Style: <b>{style_desc}</b>\n"
        f"✅ Quality: <b>{mode_desc}</b>\n"
        f"✅ Motion: <b>{motion_preset}</b> ({motion_desc})\n\n"
        "Step 6 of 7: Add Description (Prompt) 💬\n\n"
        "Describe how you want your video to look and move.\n"
        "Example: <i>\"a cinematic scene with dramatic lighting\"</i>\n\n"
        "Or skip to use automatic prompt based on your image:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_prompt_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(VideoGenerationStates.waiting_for_prompt)


@router.callback_query(VideoGenerationStates.waiting_for_prompt, F.data == "prompt_skip")
async def skip_prompt(callback: CallbackQuery, state: FSMContext):
    """Skip prompt and use automatic."""
    await callback.answer()
    
    await state.update_data(user_prompt="")
    
    data = await state.get_data()
    style_desc = VideoConfig.VISUAL_STYLES.get(data.get('visual_style'), {}).get("description", "Realistic")
    mode_desc = VideoConfig.QUALITY_MODES.get(data.get('quality_mode'), {}).get("description", "Standard")
    motion_desc = VideoConfig.MOTION_PRESETS[data.get('motion_preset', 'micro')]["description"]
    
    text = (
        f"✅ Duration: <b>{data['duration']}s</b>\n"
        f"✅ Resolution: <b>{data['resolution']}</b>\n"
        f"✅ Style: <b>{style_desc}</b>\n"
        f"✅ Quality: <b>{mode_desc}</b>\n"
        f"✅ Motion: <b>{data.get('motion_preset')}</b> ({motion_desc})\n"
        f"✅ Prompt: <b>Automatic</b>\n\n"
        "Step 7 of 7: Upload your photo 📸\n\n"
        "Please send a high-quality photo to create your video:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(VideoGenerationStates.waiting_for_photo)


@router.message(VideoGenerationStates.waiting_for_prompt, F.text)
async def process_prompt(message: Message, state: FSMContext):
    """Handle user prompt text."""
    user_prompt = message.text.strip()
    
    if len(user_prompt) > 500:
        await message.answer("⚠️ Prompt too long! Please keep it under 500 characters.")
        return
    
    await state.update_data(user_prompt=user_prompt)
    
    data = await state.get_data()
    style_desc = VideoConfig.VISUAL_STYLES.get(data.get('visual_style'), {}).get("description", "Realistic")
    mode_desc = VideoConfig.QUALITY_MODES.get(data.get('quality_mode'), {}).get("description", "Standard")
    motion_desc = VideoConfig.MOTION_PRESETS[data.get('motion_preset', 'micro')]["description"]
    
    text = (
        f"✅ Duration: <b>{data['duration']}s</b>\n"
        f"✅ Resolution: <b>{data['resolution']}</b>\n"
        f"✅ Style: <b>{style_desc}</b>\n"
        f"✅ Quality: <b>{mode_desc}</b>\n"
        f"✅ Motion: <b>{data.get('motion_preset')}</b> ({motion_desc})\n"
        f"✅ Prompt: <i>\"{user_prompt[:50]}...\"</i>\n\n"
        "Step 7 of 7: Upload your photo 📸\n\n"
        "Please send a high-quality photo to create your video:"
    )
    
    await message.answer(
        text,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(VideoGenerationStates.waiting_for_photo)


@router.message(VideoGenerationStates.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Handle photo upload and start video generation."""
    data = await state.get_data()
    
    # Get largest photo size
    photo = message.photo[-1]
    
    # Download photo
    processing_msg = await message.answer("⏳ Downloading photo...")
    
    try:
        # Download photo bytes
        file = await message.bot.get_file(photo.file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        
        # Read bytes
        image_bytes = file_bytes.read()
        
        # Encode to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        await processing_msg.edit_text("📤 Submitting job to server...")
        
        # Prepare prompt with style suffix
        user_prompt = data.get("user_prompt", "")
        visual_style = data.get("visual_style", "none")
        style_suffix = VideoConfig.VISUAL_STYLES.get(visual_style, {}).get("prompt_suffix", "")
        
        # Combine user prompt with style
        final_prompt = user_prompt + style_suffix if user_prompt else style_suffix
        
        # Get quality mode settings
        quality_mode = data.get("quality_mode", "standard")
        quality_settings = VideoConfig.QUALITY_MODES.get(quality_mode, {})
        
        # Create job via API
        job_data = {
            "user_id": message.from_user.id,
            "image_data": image_base64,
            "duration": data["duration"],
            "resolution": data["resolution"],
            "motion_preset": data["motion_preset"],
            "visual_style": visual_style,
            "quality_mode": quality_mode,
            "user_prompt": final_prompt,
            "custom_fps": quality_settings.get("fps", VideoConfig.FPS),
            "custom_steps": quality_settings.get("steps", VideoConfig.STEPS)
        }
        
        response = await http_client.post(
            f"{settings.backend_url}/job/create",
            json=job_data
        )
        response.raise_for_status()
        result = response.json()
        
        job_id = result["job_id"]
        queue_position = result["queue_position"]
        
        await processing_msg.edit_text(
            f"✅ Job created!\n\n"
            f"🆔 Job ID: <code>{job_id}</code>\n"
            f"📊 Queue position: {queue_position}\n\n"
            f"⏳ Starting processing...",
            parse_mode="HTML"
        )
        
        await state.set_state(VideoGenerationStates.processing)
        await state.update_data(job_id=job_id)
        
        # Poll for job completion
        job_result = await poll_job_status(job_id, message)
        
        if job_result:
            # Download and send video
            await processing_msg.edit_text("📥 Downloading video...")
            
            video_response = await http_client.get(
                f"{settings.backend_url}/job/download/{job_id}"
            )
            video_response.raise_for_status()
            
            # Save to temporary file
            video_path = settings.storage_hot_path / f"temp_{job_id}.mp4"
            with open(video_path, "wb") as f:
                f.write(video_response.content)
            
            # Prepare caption with all settings
            style_desc = VideoConfig.VISUAL_STYLES.get(data.get('visual_style', 'none'), {}).get("description", "Realistic")
            mode_desc = VideoConfig.QUALITY_MODES.get(data.get('quality_mode', 'standard'), {}).get("description", "Standard")
            
            # Build caption - keep it concise to avoid Telegram limits
            caption_parts = [
                "✅ <b>Your video is ready!</b>",
                f"⏱️ {data['duration']}s | 📺 {data['resolution']}",
                f"🎨 {style_desc} | 💎 {mode_desc}",
                f"🎬 {data['motion_preset']}"
            ]
            
            if data.get('user_prompt'):
                prompt_preview = data['user_prompt'][:40] + ("..." if len(data['user_prompt']) > 40 else "")
                caption_parts.append(f"💬 \"{prompt_preview}\"")
            
            caption_parts.append("FanslyMotion v2.0 🎥")
            
            caption = "\n".join(caption_parts)
            
            # Safety check - Telegram caption limit is 1024 chars
            if len(caption) > 1020:
                caption = "\n".join(caption_parts[:3]) + "\n..." + "\n" + caption_parts[-1]
                if len(caption) > 1020:
                    caption = "✅ Video ready! 🎥"
            
            # Send video
            await message.answer_video(
                video=FSInputFile(video_path),
                caption=caption,
                parse_mode="HTML",
                reply_markup=get_back_to_menu_keyboard()
            )
            
            # Cleanup
            await processing_msg.delete()
            if video_path.exists():
                video_path.unlink()
        
        await state.clear()
        
    except Exception as e:
        error_text = f"❌ Technical error. Credits refunded.\n\nError: {str(e)}"
        await message.answer(error_text, reply_markup=get_back_to_menu_keyboard())
        await state.clear()


@router.message(VideoGenerationStates.waiting_for_photo)
async def invalid_photo(message: Message):
    """Handle invalid photo input."""
    await message.answer(
        "⚠️ Please send a photo, not text or other file types.",
        reply_markup=get_cancel_keyboard()
    )


@router.callback_query(F.data == "cancel_generation")
async def cancel_generation(callback: CallbackQuery, state: FSMContext):
    """Cancel current generation."""
    await callback.answer("Generation cancelled")
    await state.clear()
    
    await callback.message.edit_text(
        "❌ Generation cancelled.",
        reply_markup=get_back_to_menu_keyboard()
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Return to main menu."""
    await callback.answer()
    await state.clear()
    
    await callback.message.edit_text(
        "🎬 <b>FanslyMotion</b>\n\nSelect an option:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_duration")
async def back_to_duration(callback: CallbackQuery, state: FSMContext):
    """Go back to duration selection."""
    await callback.answer()
    await state.set_state(VideoGenerationStates.waiting_for_duration)
    
    await callback.message.edit_text(
        "Step 1 of 4: Select video duration",
        reply_markup=get_duration_keyboard()
    )


@router.callback_query(F.data == "back_to_resolution")
async def back_to_resolution(callback: CallbackQuery, state: FSMContext):
    """Go back to resolution selection."""
    await callback.answer()
    await state.set_state(VideoGenerationStates.waiting_for_resolution)
    
    data = await state.get_data()
    
    await callback.message.edit_text(
        f"✅ Duration: <b>{data['duration']}s</b>\n\n"
        "Step 2 of 7: Select video resolution",
        reply_markup=get_resolution_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_style")
async def back_to_style(callback: CallbackQuery, state: FSMContext):
    """Go back to style selection."""
    await callback.answer()
    await state.set_state(VideoGenerationStates.waiting_for_style)
    
    data = await state.get_data()
    
    await callback.message.edit_text(
        f"✅ Duration: <b>{data['duration']}s</b>\n"
        f"✅ Resolution: <b>{data['resolution']}</b>\n\n"
        "Step 3 of 7: Select Visual Style 🎨",
        reply_markup=get_style_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_quality")
async def back_to_quality(callback: CallbackQuery, state: FSMContext):
    """Go back to quality mode selection."""
    await callback.answer()
    await state.set_state(VideoGenerationStates.waiting_for_quality_mode)
    
    data = await state.get_data()
    style_desc = VideoConfig.VISUAL_STYLES.get(data.get('visual_style'), {}).get("description", "Realistic")
    
    await callback.message.edit_text(
        f"✅ Duration: <b>{data['duration']}s</b>\n"
        f"✅ Resolution: <b>{data['resolution']}</b>\n"
        f"✅ Style: <b>{style_desc}</b>\n\n"
        "Step 4 of 7: Select Quality Mode 💎",
        reply_markup=get_quality_mode_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_motion")
async def back_to_motion(callback: CallbackQuery, state: FSMContext):
    """Go back to motion selection."""
    await callback.answer()
    await state.set_state(VideoGenerationStates.waiting_for_motion)
    
    data = await state.get_data()
    style_desc = VideoConfig.VISUAL_STYLES.get(data.get('visual_style'), {}).get("description", "Realistic")
    mode_desc = VideoConfig.QUALITY_MODES.get(data.get('quality_mode'), {}).get("description", "Standard")
    
    await callback.message.edit_text(
        f"✅ Duration: <b>{data['duration']}s</b>\n"
        f"✅ Resolution: <b>{data['resolution']}</b>\n"
        f"✅ Style: <b>{style_desc}</b>\n"
        f"✅ Quality: <b>{mode_desc}</b>\n\n"
        "Step 5 of 7: Select Motion Preset 🎬",
        reply_markup=get_motion_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "info")
async def show_info(callback: CallbackQuery):
    """Show bot information."""
    await callback.answer()
    
    info_text = (
        "ℹ️ <b>FanslyMotion Info</b>\n\n"
        "<b>Supported Resolutions:</b>\n"
        "• 360p (480×360) - Fast\n"
        "• 480p (640×480) - Balanced\n"
        "• 720p (1280×720) - Recommended ⭐\n"
        "• 1080p (1920×1080) - Maximum quality\n\n"
        "<b>Durations:</b>\n"
        "• 3, 6, 8, 10, 12 seconds\n\n"
        "<b>Visual Styles:</b>\n"
        "• 🎨 Realistic, Anime, Comic, 3D\n"
        "• 🎬 Cinematic, Cyberpunk, Clay, Fantasy\n\n"
        "<b>Quality Modes:</b>\n"
        "• ⚡ Fast (30 steps, 18 FPS)\n"
        "• ⭐ Standard (40 steps, 24 FPS)\n"
        "• 💎 Smooth (50 steps, 30 FPS)\n\n"
        "<b>Motion Presets:</b>\n"
        "• 🔍 Micro, 🌊 Smooth\n"
        "• ⬅️➡️ Pan, ⬆️⬇️ Tilt\n"
        "• 🔎 Dolly, ⚡ Dynamic\n\n"
        "<b>Technical Details:</b>\n"
        "• Model: Stable Video Diffusion XT\n"
        "• Enhanced with xformers optimization\n"
        "• Post-processing for maximum quality\n"
        "• Format: MP4 (H.264)\n\n"
        "FanslyMotion v2.0 - Professional AI Video 🎥"
    )
    
    await callback.message.edit_text(
        info_text,
        reply_markup=get_back_to_menu_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    help_text = (
        "📚 <b>Help - How to Use FanslyMotion</b>\n\n"
        "1️⃣ Use /start to open the main menu\n"
        "2️⃣ Click '📸 photo→video 🎦' to start\n"
        "3️⃣ Select duration (3-12 seconds)\n"
        "4️⃣ Choose resolution (360p-1080p)\n"
        "5️⃣ Pick a motion preset\n"
        "6️⃣ Upload your photo\n"
        "7️⃣ Wait for processing\n"
        "8️⃣ Receive your video!\n\n"
        "<b>Tips:</b>\n"
        "• Use clear, well-lit photos\n"
        "• Higher resolutions take longer\n"
        "• Motion presets affect the video style\n\n"
        "Need more help? Contact support."
    )
    
    await message.answer(help_text, parse_mode="HTML")

