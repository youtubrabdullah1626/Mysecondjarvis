import csv
import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'mood_log.csv')

def log_mood(description: str):
    """Append a mood entry to mood_log.csv. If description contains 'Mood:', extract it."""
    mood = None
    if 'Mood:' in description:
        try:
            mood = description.split('Mood:')[-1].split()[0].strip().lower()
        except Exception:
            mood = None
    row = {
        'timestamp': datetime.utcnow().isoformat(),
        'mood': mood if mood else '',
        'description': description
    }
    write_header = not os.path.exists(LOG_FILE)
    try:
        with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp','mood','description'])
            if write_header:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        # Non-fatal: print error for visibility
        print(f"[mood_logger] Failed to write log: {e}")

def read_logs(limit: int = 50):
    """Read last `limit` logs from the CSV."""
    if not os.path.exists(LOG_FILE):
        return []
    rows = []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception as e:
        print(f"[mood_logger] Failed to read logs: {e}")
        return []
    return rows[-limit:]
