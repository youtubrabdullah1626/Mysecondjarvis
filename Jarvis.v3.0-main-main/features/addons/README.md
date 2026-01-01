Addons feature folder

This folder contains small optional features you can enable individually:

- face_registry.py — simple face registry and identification (uses `face_recognition` if installed)
- ambient_sound_detector.py — placeholder for sound detection (requires `pyaudio` + `numpy`)
- auto_notes.py — append/read short notes per day
- screen_logger.py — screenshot capture using PIL
- reminder_service.py — schedule/list reminders (file-based)

How to use
Import them directly, for example:

from features.addons import auto_notes
auto_notes.append_note('Test')

They are intentionally lightweight and safe: missing optional libraries will cause functions to return fallbacks rather than crash.
