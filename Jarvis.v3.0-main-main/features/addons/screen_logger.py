"""Screen logger stub

Functions:
- capture_screenshot(name: str = None) -> str (path)

This uses PIL if available. Saves screenshots in features/addons/screenshots.
"""
import os
from datetime import datetime

def capture_screenshot(name: str = None) -> str:
    try:
        from PIL import ImageGrab
    except Exception:
        print('[screen_logger] PIL not available')
        return ''
    folder = os.path.join(os.path.dirname(__file__), 'screenshots')
    os.makedirs(folder, exist_ok=True)
    if not name:
        name = datetime.now().strftime('%Y%m%d_%H%M%S') + '.png'
    path = os.path.join(folder, name)
    try:
        img = ImageGrab.grab()
        img.save(path)
        return path
    except Exception as e:
        print(f"[screen_logger] capture error: {e}")
        return ''
