import speech_recognition as sr
import pywhatkit
import pyautogui
import time
import pygetwindow as gw
import sys
import webbrowser
import urllib.parse
import os
import re
import requests
from features.storage import data_path


# from livekit.plugins import  # Removed incomplete import statement

async def play_youtube_song(song_name: str):
    """Play a song on YouTube using pywhatkit with a webbrowser fallback.

    This async function performs the same action as the sync helper below
    but keeps the async signature in case other code awaits it.
    """
    try:
        pywhatkit.playonyt(song_name)
        return f"Playing '{song_name}' on YouTube."
    except Exception as e:
        # Log the failure and try a webbrowser fallback
        try:
            logp = data_path('youtube_error.log')
            with open(logp, 'a', encoding='utf-8') as lf:
                lf.write(f"[{time.time()}] pywhatkit.playonyt failed: {e}\n")
        except Exception:
            pass
        try:
            q = urllib.parse.quote_plus(song_name)
            url = f"https://www.youtube.com/results?search_query={q}"
            webbrowser.open_new_tab(url)
            return f"Opened browser search for '{song_name}' as fallback."
        except Exception as e2:
            return f"Error playing song (fallback failed): {e2}"


def play_youtube_song_sync(song_name: str) -> str:
    """Synchronous helper that attempts to play via pywhatkit then falls back to the browser."""
    try:
        pywhatkit.playonyt(song_name)
        return f"Playing '{song_name}' on YouTube."
    except Exception as e:
        try:
            logp = data_path('youtube_error.log')
            with open(logp, 'a', encoding='utf-8') as lf:
                lf.write(f"[{time.time()}] pywhatkit.playonyt failed: {e}\n")
        except Exception:
            pass
        try:
            # Try to resolve a direct video link from the search results and open it
            vid = None
            try:
                q = urllib.parse.quote_plus(song_name)
                search_url = f"https://www.youtube.com/results?search_query={q}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
                }
                r = requests.get(search_url, headers=headers, timeout=8)
                if r.status_code == 200 and r.text:
                    # First try to find videoId fields which appear in JSON snippets
                    m = re.search(r'"videoId"\s*:\s*"([A-Za-z0-9_\-]{11})"', r.text)
                    if m:
                        vid = m.group(1)
                    else:
                        # Fallback: look for watch?v= links in the HTML
                        m2 = re.search(r"watch\?v=([A-Za-z0-9_\-]{11})", r.text)
                        if m2:
                            vid = m2.group(1)
            except Exception as exc:
                try:
                    with open(data_path('youtube_error.log'), 'a', encoding='utf-8') as lf:
                        lf.write(f"[{time.time()}] error resolving direct video for '{song_name}': {exc}\n")
                except Exception:
                    pass
                vid = None

            if vid:
                video_url = f"https://www.youtube.com/watch?v={vid}"
                try:
                    webbrowser.open_new_tab(video_url)
                    try:
                        with open(data_path('youtube_error.log'), 'a', encoding='utf-8') as lf:
                            lf.write(f"[{time.time()}] opened direct video {video_url} for '{song_name}'\n")
                    except Exception:
                        pass
                    return f"Opened video {video_url} for '{song_name}' as fallback."
                except Exception as exc:
                    try:
                        with open(data_path('youtube_error.log'), 'a', encoding='utf-8') as lf:
                            lf.write(f"[{time.time()}] failed to open direct video URL {video_url}: {exc}\n")
                    except Exception:
                        pass
                    # Fall through to open search page below

            # If we couldn't resolve a video id or opening failed, open the search page
            q = urllib.parse.quote_plus(song_name)
            url = f"https://www.youtube.com/results?search_query={q}"
            try:
                webbrowser.open_new_tab(url)
                return f"Opened browser search for '{song_name}' as fallback."
            except Exception as e_open:
                try:
                    with open(data_path('youtube_error.log'), 'a', encoding='utf-8') as lf:
                        lf.write(f"[{time.time()}] fallback webbrowser failed: {e_open}\n")
                except Exception:
                    pass
                return f"Error opening browser search for '{song_name}': {e_open}"
        except Exception as e2:
            try:
                with open(data_path('youtube_error.log'), 'a', encoding='utf-8') as lf:
                    lf.write(f"[{time.time()}] fallback webbrowser failed: {e2}\n")
            except Exception:
                pass
            return f"Error playing song (fallback failed): {e2}"

class VoiceYouTubeController:
    """A class to control YouTube via voice commands without a GUI."""

    def __init__(self):
        """Initializes the recognizer and microphone."""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.youtube_window = None
        print("Adjusting for ambient noise, please wait...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Ready to receive commands. Say 'Jarvis' followed by your command.")

    def _find_and_focus_youtube(self):
        """Finds and activates any window with 'YouTube' in its title."""
        self.youtube_window = None
        for window in gw.getAllWindows():
            if window.title and 'youtube' in window.title.lower():
                self.youtube_window = window
                break
        
        if self.youtube_window:
            try:
                if self.youtube_window.isMinimized:
                    self.youtube_window.restore()
                self.youtube_window.activate()
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"Warning: Could not activate window, but proceeding. Error: {e}")
                return True
        print("Error: YouTube window not found.")
        return False

    def play_song(self, song_name: str):
        """Plays a song on YouTube."""
        if not song_name:
            print("Jarvis: Please specify a song to play.")
            return

        print(f"Jarvis: Playing '{song_name}' on YouTube.")
        try:
            pywhatkit.playonyt(song_name)
            print("Waiting for 10 seconds for the video to load...")
            time.sleep(10)
            if self._find_and_focus_youtube():
                pyautogui.press('f') # Try to enter fullscreen
                print("Jarvis: Playback started. Ready for next command.")
            else:
                print("Jarvis: Could not focus the YouTube window for further control.")
        except Exception as e:
            print(f"Jarvis: An error occurred while trying to play the song: {e}")
            try:
                with open(data_path('youtube_error.log'), 'a', encoding='utf-8') as lf:
                    lf.write(f"[{time.time()}] play_song exception: {str(e)}\n")
            except Exception:
                pass

    def _execute_action(self, key_or_hotkey, response_text):
        """A helper function to focus window and press keys."""
        if self._find_and_focus_youtube():
            if isinstance(key_or_hotkey, list):
                pyautogui.hotkey(*key_or_hotkey)
            else:
                pyautogui.press(key_or_hotkey)
            print(f"Jarvis: {response_text}")
        else:
            print("Jarvis: Action failed. Could not find the YouTube window.")
    
    def handle_music_command(self, command: str):
        """Handles all music-related control commands."""
        actions = {
            ("pause", "play", "resume"): ('space', "Toggled play/pause."),
            ("mute", "unmute"): ('m', "Toggled mute."),
            ("volume up", "increase volume"): ('up', "Increased volume."),
            ("volume down", "decrease volume"): ('down', "Decreased volume."),
            ("next song", "next video", "change song"): (['shift', 'n'], "Playing next video."),
            ("close tab", "close youtube"): (['ctrl', 'w'], "Closed YouTube tab.")
        }
        
        normalized_command = command.lower().strip()
        for keys, (action, response) in actions.items():
            if normalized_command in keys:
                self._execute_action(action, response)
                return

    def listen(self):
        """Continuously listens for voice commands."""
        while True:
            try:
                with self.microphone as source:
                    print("\nListening for activation word 'Jarvis'...")
                    audio = self.recognizer.listen(source)
                
                print("Recognizing...")
                text = self.recognizer.recognize_google(audio, language='en-in').lower()

                if "jarvis" in text:
                    command = text.split("jarvis", 1)[1].strip()
                    print(f"User command: '{command}'")
                    
                    if command.startswith("play "):
                        song_name = command.replace("play", "", 1).strip()
                        self.play_song(song_name)
                    elif command in ["exit", "shutdown", "stop listening"]:
                        print("Jarvis: Deactivating. Goodbye!")
                        sys.exit()
                    else:
                        self.handle_music_command(command)
                        
            except sr.UnknownValueError:
                # This is common when there is silence or noise
                pass
            except sr.RequestError as e:
                print(f"Could not request results from Google; {e}")
            except KeyboardInterrupt:
                print("\nJarvis: Shutting down on user request.")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

def youtube_control(command: str):
    """Control YouTube playback (pause, resume, next, etc.) via pyautogui."""
    import pyautogui
    actions = {
        "pause": "space",
        "play": "space",
        "resume": "space",
        "next": ["shift", "n"],
        "mute": "m",
        "unmute": "m",
        "fullscreen": "f",
        "exit fullscreen": "f",
    }
    key = actions.get(command.lower())
    if key:
        if isinstance(key, list):
            pyautogui.hotkey(*key)
        else:
            pyautogui.press(key)
        return f"YouTube action '{command}' executed."
    return f"Unknown YouTube command: {command}"

if __name__ == "__main__":
    controller = VoiceYouTubeController()
    controller.listen()