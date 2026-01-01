"""Simple visibility/permission manager for Jarvis features.

This module stores a small JSON at the repo root `.permissions.json` with keys like
`camera` and `screen_capture`, and provides helpers to check and change permissions.
"""
import json
import os
from datetime import datetime

PERM_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '.permissions.json')

DEFAULTS = {
    'camera': True,
    'screen_capture': False,
    'face_registry': False,
}

def _read_perms():
    try:
        if os.path.exists(PERM_FILE):
            with open(PERM_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return DEFAULTS.copy()

def _write_perms(p):
    try:
        with open(PERM_FILE, 'w', encoding='utf-8') as f:
            json.dump(p, f, indent=2)
        return True
    except Exception as e:
        print(f"[visibility] write error: {e}")
        return False

def is_allowed(feature: str) -> bool:
    p = _read_perms()
    return bool(p.get(feature, False))

def grant(feature: str) -> bool:
    p = _read_perms()
    p[feature] = True
    p['last_changed'] = datetime.utcnow().isoformat()
    return _write_perms(p)

def revoke(feature: str) -> bool:
    p = _read_perms()
    p[feature] = False
    p['last_changed'] = datetime.utcnow().isoformat()
    return _write_perms(p)

def status():
    return _read_perms()
