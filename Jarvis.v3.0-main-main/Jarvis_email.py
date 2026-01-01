# jarvis_email_module_popup_email.py
import os
import json
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from livekit.agents import function_tool
import platform
import subprocess
import tkinter as tk
from tkinter import simpledialog
import difflib
import datetime
import traceback

# Load .env
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_CONFIGURED = bool(EMAIL_ADDRESS and EMAIL_PASSWORD)
if not EMAIL_CONFIGURED:
    # Do not exit on import; instead make functions return clear errors at runtime.
    print("WARNING: EMAIL_ADDRESS या EMAIL_PASSWORD .env में सेट नहीं है। ईमेल भेजने की कोशिश करने पर error आएगा।")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Contact list
contact_list = {
    "john": "john.doe@example.com",
    "mom": "mom.email@example.com",
    "me": EMAIL_ADDRESS,
    "vikash": "vikashkumar13228@gmail.com",
    "vinod": "guptavinod02210@gmail.com"
}

# quick aliases (common misspellings / variations)
aliases = {
    'vikas': 'vikash',
}

def resolve_recipient(name_or_email: str) -> str:
    """Resolve an identifier to an email address.
    Order: if looks like an email, return it. Else exact key match, aliases, close-match.
    Returns the resolved email string (or the original identifier if nothing found).
    """
    if not name_or_email:
        return None
    candidate = name_or_email.strip().lower()
    # if it looks like an email address, return as-is
    if "@" in candidate and "." in candidate.split('@')[-1]:
        return candidate

    # alias lookup
    if candidate in aliases:
        key = aliases[candidate]
        return contact_list.get(key, candidate)

    # direct contact lookup
    if candidate in contact_list:
        return contact_list[candidate]

    # fuzzy match against keys
    keys = list(contact_list.keys())
    matches = difflib.get_close_matches(candidate, keys, n=1, cutoff=0.7)
    if matches:
        return contact_list.get(matches[0], candidate)

    # no match, return original (may be an email the user said)
    return name_or_email

def speak(text: str):
    """Jarvis बोलेगा text"""
    print(f"Jarvis: {text}")
    try:
        if platform.system() == "Windows":
            cmd = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{text}");'
            subprocess.run(["powershell", "-Command", cmd], check=True, capture_output=True, text=True)
        elif platform.system() == "Darwin":
            subprocess.call(["say", text])
        else:
            subprocess.call(["espeak", text])
    except Exception:
        print("(Unable to speak)")

# --- Tkinter popup only for email ---
def get_email_from_user(prompt="Enter recipient email:"):
    root = tk.Tk()
    root.withdraw()
    user_email = simpledialog.askstring("Email Input", prompt)
    root.destroy()
    return user_email

# --- Send email function ---
@function_tool(name="send_email", description="Send email via Gmail SMTP")
async def send_email_interactive(recipient: str = None, subject: str = None, message: str = None):
    """Interactive send tool. If parameters are provided, use them. Otherwise attempt to collect via Tkinter dialogs.
    Avoid console input so this can run under the agent process."""
    if not EMAIL_CONFIGURED:
        speak("Email configuration missing. कृपया .env में EMAIL_ADDRESS और EMAIL_PASSWORD सेट करें.")
        return {"status": "error", "error": "email_not_configured"}

    try:
        # Determine recipient
        name_or_email = recipient
        if not name_or_email:
            speak("Please enter recipient email:")
            try:
                name_or_email = get_email_from_user("Enter recipient email:")
            except Exception:
                name_or_email = None
        if not name_or_email:
            speak("No email entered. Cancelled.")
            return {"status": "cancelled"}

        receiver = resolve_recipient(name_or_email)

        # Subject and message: try provided params first, then popup dialogs
        subj = subject
        msg_text = message
        if not subj:
            try:
                root = tk.Tk(); root.withdraw()
                subj = simpledialog.askstring("Subject", "Enter subject:")
                root.destroy()
            except Exception:
                subj = ''
        if not msg_text:
            try:
                root = tk.Tk(); root.withdraw()
                msg_text = simpledialog.askstring("Message", "Enter message:")
                root.destroy()
            except Exception:
                msg_text = ''

        speak(f"Sending email to {receiver}...")
        msg = MIMEMultipart()
        msg["From"] = f"Jarvis <{EMAIL_ADDRESS}>"
        msg["To"] = receiver
        msg["Subject"] = subj or ''
        msg.attach(MIMEText(msg_text or '', "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, receiver, msg.as_string())
        server.quit()
        speak("Email submitted successfully!")
        result = {"status": "sent", "receiver": receiver}
    except Exception as e:
        speak("Failed to send email.")
        tb = traceback.format_exc()
        result = {"status": "error", "error": str(e), "receiver": receiver if 'receiver' in locals() else None, "traceback": tb}

    # write result file for agent compatibility
    try:
        data_dir = os.path.join(os.path.dirname(__file__), 'jarvis_data')
        os.makedirs(data_dir, exist_ok=True)
        result_path = os.path.join(data_dir, 'email_result.json')
        with open(result_path, 'w', encoding='utf-8') as rf:
            json.dump(result, rf, ensure_ascii=False)
        # also append to a human-readable log for debugging
        try:
            log_path = os.path.join(data_dir, 'email_ui.log')
            with open(log_path, 'a', encoding='utf-8') as lf:
                lf.write(datetime.datetime.now().isoformat() + ' - ' + json.dumps(result, ensure_ascii=False) + '\n')
        except Exception:
            pass
    except Exception:
        pass

    return result


def send_email_direct(recipient_identifier: str, subject: str, message: str) -> dict:
    """Send email directly (no GUI). recipient_identifier can be a name from contact_list or an email."""
    receiver = None
    try:
        if not EMAIL_CONFIGURED:
            return {"status": "error", "error": "email_not_configured"}
        if not recipient_identifier:
            return {"status": "error", "error": "missing recipient"}
        receiver = resolve_recipient(recipient_identifier)
        msg = MIMEMultipart()
        msg["From"] = f"Jarvis <{EMAIL_ADDRESS}>"
        msg["To"] = receiver
        msg["Subject"] = subject or ''
        msg.attach(MIMEText(message or '', "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, receiver, msg.as_string())
        server.quit()
        result = {"status": "sent", "receiver": receiver}
    except Exception as e:
        tb = traceback.format_exc()
        result = {"status": "error", "error": str(e), "receiver": receiver, "traceback": tb}
    # write result file for agent compatibility
    try:
        data_dir = os.path.join(os.path.dirname(__file__), 'jarvis_data')
        os.makedirs(data_dir, exist_ok=True)
        result_path = os.path.join(data_dir, 'email_result.json')
        with open(result_path, 'w', encoding='utf-8') as rf:
            json.dump(result, rf, ensure_ascii=False)
        try:
            log_path = os.path.join(data_dir, 'email_ui.log')
            with open(log_path, 'a', encoding='utf-8') as lf:
                lf.write(datetime.datetime.now().isoformat() + ' - ' + json.dumps(result, ensure_ascii=False) + '\n')
        except Exception:
            pass
    except Exception:
        pass
    return result

# --- Main loop ---
if __name__ == "__main__":
    speak("Jarvis is ready with email module.")
    running = True
    while running:
        user_input = input("You (type 'send email' or 'exit'): ").lower()
        if "send email" in user_input:
            asyncio.run(send_email_interactive())
        elif "exit" in user_input or "quit" in user_input:
            speak("Goodbye!")
            running = False
        else:
            speak("Command not recognized. Type 'send email' or 'exit'.")
