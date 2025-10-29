"""
FSM states for bot conversation flow.
"""
from aiogram.fsm.state import State, StatesGroup


class VideoGenerationStates(StatesGroup):
    """States for video generation flow."""
    waiting_for_duration = State()
    waiting_for_resolution = State()
    waiting_for_style = State()
    waiting_for_quality_mode = State()
    waiting_for_motion = State()
    waiting_for_prompt = State()
    waiting_for_photo = State()
    processing = State()

