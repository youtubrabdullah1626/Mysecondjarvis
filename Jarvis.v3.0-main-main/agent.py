from dotenv import load_dotenv
import asyncio
import datetime
import traceback
import os
import builtins
import subprocess
import sys



from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    google,
    noise_cancellation,
)
from Jarvis_prompts import behavior_prompts, Reply_prompts
from Jarvis_google_search import google_search, get_current_datetime
from jarvis_get_whether import get_weather
from Jarvis_window_CTRL import open, close, folder_file
from Jarvis_file_opner import Play_file
from keyboard_mouse_CTRL import move_cursor_tool, mouse_click_tool, scroll_cursor_tool, type_text_tool, press_key_tool, swipe_gesture_tool, press_hotkey_tool, control_volume_tool
load_dotenv()

# Memory persistence (best-effort)
try:
    from Jarvis_memory import save_conversation, recall_last, summarize_recent
except Exception:
    def save_conversation(u, a):
        return None
    def recall_last(n=10):
        return []
    def summarize_recent(n=10):
        return ""


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=behavior_prompts,
                         tools=[
                            google_search,
                            get_current_datetime,
                            get_weather,
                            open, #ये apps ओपन करने के लिए हैं
                            close, 
                            folder_file, #ये folder ओपन करने के लिए है
                            Play_file,  #ये file रन करने के लिए है जैसे कि MP4, MP3, PDF, PPT, img, png etc.
                            move_cursor_tool, #ये cursor move करने के लिए है
                            mouse_click_tool, #ये mouse click करने के लिए है
                            scroll_cursor_tool, #ये cursor scroll करने के लिए है
                            type_text_tool, #ये text type करने के लिए है
                            press_key_tool, #ये key press करने के लिए है
                            press_hotkey_tool, #ये hotkey press करने के लिए है
                            control_volume_tool, #ये volume control करने के लिए है
                            swipe_gesture_tool #ये gesture wipe करने के लिए है 
                         ]
                         )

    async def on_tool_result(self, tool_name, user_input, result):
        try:
            # save as a small conversation pair: user input -> tool result
            await asyncio.to_thread(save_conversation, str(user_input), str(result))
        except Exception:
            pass

    async def on_reply(self, user_input, jarvis_reply):
        try:
            await asyncio.to_thread(save_conversation, str(user_input), str(jarvis_reply))
        except Exception:
            pass


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            voice="Charon"
        )
    )
    
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
            video_enabled=True 
        ),
    )

    await ctx.connect()

    async def safe_generate_reply(sess, instructions, retries: int = 3, base_wait: float = 1.0) -> bool:
        """Try to call sess.generate_reply with retries and log failures to jarvis_data/realtime_errors.log.

        Returns True on success, False if all retries failed.
        """
        logdir = os.path.join(os.getcwd(), 'jarvis_data')
        os.makedirs(logdir, exist_ok=True)
        logpath = os.path.join(logdir, 'realtime_errors.log')

        for attempt in range(1, retries + 1):
            try:
                await sess.generate_reply(instructions=instructions)
                return True
            except Exception as e:
                tb = traceback.format_exc()
                ts = datetime.datetime.now().isoformat()
                entry = f"[{ts}] generate_reply attempt={attempt} error={e}\n{tb}\n"
                try:
                    with builtins.open(logpath, 'a', encoding='utf-8') as lf:
                        lf.write(entry)
                except Exception:
                    # best-effort write
                    pass
                print(f"[agent] generate_reply attempt {attempt} failed: {e}")
                if attempt < retries:
                    await asyncio.sleep(base_wait * attempt)
        return False

    ok = await safe_generate_reply(session, Reply_prompts)
    if not ok:
        print("Failed to generate initial reply after retries. See jarvis_data/realtime_errors.log for details.")

get_current_datetime




if __name__ == "__main__":
    # Best-effort: start the GUI when the agent is launched so the user sees the interface.
    def start_gui_if_needed():
        try:
            data_dir = os.path.join(os.getcwd(), 'jarvis_data')
            os.makedirs(data_dir, exist_ok=True)
            lock_path = os.path.join(data_dir, 'gui_running.lock')
            log_path = os.path.join(data_dir, 'gui_launch.log')

            # If a lock exists, assume GUI already running
            if os.path.exists(lock_path):
                return

            # Prefer pythonw from venv, then system pythonw, else fallback to sys.executable
            pythonw = None
            venv_pythonw = os.path.join(os.getcwd(), 'venv', 'Scripts', 'pythonw.exe')
            if os.path.exists(venv_pythonw):
                pythonw = venv_pythonw
            else:
                sibling_pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
                if os.path.exists(sibling_pythonw):
                    pythonw = sibling_pythonw
                else:
                    pythonw = sys.executable

            gui_script = os.path.join(os.getcwd(), 'jarvis_gui.py')
            env = os.environ.copy()

            try:
                lf = builtins.open(log_path, 'a', encoding='utf-8', errors='replace')
            except Exception:
                lf = None

            creation_flags = 0
            try:
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            except Exception:
                creation_flags = 0

            try:
                if lf:
                    subprocess.Popen([pythonw, gui_script], cwd=os.getcwd(), env=env,
                                     stdout=lf, stderr=lf, close_fds=True, creationflags=creation_flags)
                else:
                    subprocess.Popen([pythonw, gui_script], cwd=os.getcwd(), env=env,
                                     close_fds=True, creationflags=creation_flags)
                # write a lock file so we don't spawn duplicates
                try:
                    with builtins.open(lock_path, 'w', encoding='utf-8') as lk:
                        lk.write(str(os.getpid()))
                except Exception:
                    pass
            except Exception as e:
                try:
                    if lf:
                        lf.write(f"Failed to spawn GUI: {e}\n")
                except Exception:
                    pass
        except Exception:
            pass

    try:
        start_gui_if_needed()
    except Exception:
        pass

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))

