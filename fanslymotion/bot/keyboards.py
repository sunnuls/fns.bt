"""
Keyboard builders for Telegram bot interaction.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import VideoConfig

# Import new configurations
if not hasattr(VideoConfig, 'VISUAL_STYLES'):
    VideoConfig.VISUAL_STYLES = {
        "none": {"description": "No style (realistic)", "prompt_suffix": ""}
    }
if not hasattr(VideoConfig, 'QUALITY_MODES'):
    VideoConfig.QUALITY_MODES = {
        "standard": {"steps": 40, "fps": 24, "description": "Standard quality"}
    }


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get the main menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📸 photo→video 🎦", callback_data="start_generation")
    builder.button(text="ℹ️ Info", callback_data="info")
    builder.adjust(1)
    return builder.as_markup()


def get_duration_keyboard() -> InlineKeyboardMarkup:
    """Get duration selection keyboard."""
    builder = InlineKeyboardBuilder()
    for duration in VideoConfig.DURATIONS:
        builder.button(text=f"{duration}s", callback_data=f"duration_{duration}")
    builder.button(text="◀️ Back", callback_data="back_to_menu")
    builder.adjust(3, 2, 1)
    return builder.as_markup()


def get_resolution_keyboard() -> InlineKeyboardMarkup:
    """Get resolution selection keyboard."""
    builder = InlineKeyboardBuilder()
    for res_name in VideoConfig.RESOLUTIONS.keys():
        width, height = VideoConfig.RESOLUTIONS[res_name]
        builder.button(text=f"{res_name} ({width}×{height})", callback_data=f"resolution_{res_name}")
    builder.button(text="◀️ Back", callback_data="back_to_duration")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def get_style_keyboard() -> InlineKeyboardMarkup:
    """Get visual style selection keyboard (like LitVideo)."""
    builder = InlineKeyboardBuilder()
    
    style_emojis = {
        "none": "⚪",
        "anime": "🎌",
        "comic": "📕",
        "3d": "🎮",
        "clay": "🪨",
        "cyberpunk": "🌃",
        "cinematic": "🎬",
        "fantasy": "✨"
    }
    
    for style_name, config in VideoConfig.VISUAL_STYLES.items():
        emoji = style_emojis.get(style_name, "🎨")
        label = f"{emoji} {config['description']}"
        builder.button(text=label, callback_data=f"style_{style_name}")
    
    builder.button(text="◀️ Back", callback_data="back_to_resolution")
    builder.adjust(2, 2, 2, 2, 1)
    return builder.as_markup()


def get_quality_mode_keyboard() -> InlineKeyboardMarkup:
    """Get quality mode selection keyboard."""
    builder = InlineKeyboardBuilder()
    
    mode_emojis = {
        "fast": "⚡",
        "standard": "⭐",
        "smooth": "💎"
    }
    
    for mode_name, config in VideoConfig.QUALITY_MODES.items():
        emoji = mode_emojis.get(mode_name, "🎯")
        label = f"{emoji} {config['description']}"
        builder.button(text=label, callback_data=f"quality_{mode_name}")
    
    builder.button(text="◀️ Back", callback_data="back_to_style")
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()


def get_motion_keyboard() -> InlineKeyboardMarkup:
    """Get motion preset selection keyboard."""
    builder = InlineKeyboardBuilder()
    
    motion_labels = {
        "micro": "🔍 Micro",
        "smooth": "🌊 Smooth",
        "pan_l": "⬅️ Pan Left",
        "pan_r": "➡️ Pan Right",
        "tilt_up": "⬆️ Tilt Up",
        "tilt_down": "⬇️ Tilt Down",
        "dolly_in": "🔎 Dolly In",
        "dynamic": "⚡ Dynamic"
    }
    
    for preset_name, config in VideoConfig.MOTION_PRESETS.items():
        label = motion_labels.get(preset_name, preset_name)
        builder.button(text=label, callback_data=f"motion_{preset_name}")
    
    builder.button(text="◀️ Back", callback_data="back_to_quality")
    builder.adjust(2, 2, 2, 2, 1)
    return builder.as_markup()


def get_prompt_keyboard() -> InlineKeyboardMarkup:
    """Get prompt input keyboard with skip option."""
    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ Skip (use auto prompt)", callback_data="prompt_skip")
    builder.button(text="◀️ Back", callback_data="back_to_motion")
    builder.adjust(1, 1)
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get cancel keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Cancel", callback_data="cancel_generation")
    return builder.as_markup()


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Get back to menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Back to Menu", callback_data="back_to_menu")
    return builder.as_markup()

