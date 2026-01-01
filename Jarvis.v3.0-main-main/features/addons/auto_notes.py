"""Auto-notes: simple helper to append short transcriptions or notes to a daily file."""
import os
from datetime import datetime

def append_note(text: str):
    d = datetime.now().strftime('%Y-%m-%d')
    folder = os.path.join(os.path.dirname(__file__), '..', '..', 'notes')
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f'{d}.md')
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f"- [{datetime.now().strftime('%H:%M:%S')}] {text}\n")
        return True
    except Exception as e:
        print(f"[auto_notes] append_note error: {e}")
        return False

def read_notes(days: int = 7):
    # Return recent notes concatenated
    folder = os.path.join(os.path.dirname(__file__), '..', '..', 'notes')
    if not os.path.exists(folder):
        return ''
    files = sorted([f for f in os.listdir(folder) if f.endswith('.md')], reverse=True)
    out = ''
    for f in files[:days]:
        try:
            with open(os.path.join(folder, f), 'r', encoding='utf-8') as fh:
                out += f"\n## {f}\n" + fh.read()
        except Exception:
            pass
    return out
