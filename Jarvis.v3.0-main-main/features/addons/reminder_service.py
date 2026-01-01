"""Reminder service stub

Functions:
- schedule_reminder(text: str, when: str) -> bool
- list_reminders() -> list

This is a simple file-based scheduler (no background runner). For now it stores reminders and
returns them; you can add a separate runner to check and fire reminders later.
"""
import os
import json
from datetime import datetime

DB = os.path.join(os.path.dirname(__file__), 'reminders.json')

def schedule_reminder(text: str, when: str) -> bool:
    try:
        reminders = []
        if os.path.exists(DB):
            with open(DB, 'r', encoding='utf-8') as f:
                reminders = json.load(f)
        reminders.append({'text': text, 'when': when, 'created': datetime.utcnow().isoformat()})
        with open(DB, 'w', encoding='utf-8') as f:
            json.dump(reminders, f, indent=2)
        return True
    except Exception as e:
        print(f"[reminder_service] schedule error: {e}")
        return False

def list_reminders():
    try:
        if not os.path.exists(DB):
            return []
        with open(DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[reminder_service] list error: {e}")
        return []
