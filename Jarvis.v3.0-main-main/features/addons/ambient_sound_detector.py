"""Ambient sound detector stub

Functions:
- detect_loud_sound(threshold_db: int = 70) -> bool

This file includes a simple placeholder. For a real implementation it would read from the microphone
and perform RMS/decibel analysis. Here it returns False (no loud sound) unless `pyaudio` and
`numpy` are present and user invokes the function.
"""

def detect_loud_sound(threshold_db: int = 70) -> bool:
    try:
        import numpy as np
        import pyaudio
    except Exception:
        print("[ambient_sound_detector] libs missing; returning False")
        return False
    # Placeholder: real-time microphone code omitted for safety and simplicity
    return False
