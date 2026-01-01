import pyautogui
import asyncio
import time
import os
import builtins
from datetime import datetime
from typing import List
from livekit.agents import function_tool

try:
    import pyperclip
except Exception:
    pyperclip = None

# ---------------------
# SafeController Class
# ---------------------
class SafeController:
    def __init__(self):
        self.active = False
        self.activation_time = None
        pyautogui.FAILSAFE = False  # Move mouse to top-left corner to stop script

    def log(self, action: str):
        # write into centralized jarvis_data if possible
        try:
            data_dir = os.path.join(os.getcwd(), 'jarvis_data')
            os.makedirs(data_dir, exist_ok=True)
            path = os.path.join(data_dir, 'control_log.txt')
            with builtins.open(path, 'a', encoding='utf-8', errors='replace') as f:
                f.write(f"{datetime.now()}: {action}\n")
        except Exception:
            try:
                with builtins.open('control_log.txt', 'a', encoding='utf-8', errors='replace') as f:
                    f.write(f"{datetime.now()}: {action}\n")
            except Exception:
                pass

    def activate(self, token=None):
        if token != "my_secret_token":
            self.log("Activation attempt failed.")
            return
        self.active = True
        self.activation_time = time.time()
        self.log("Controller activated.")

    def deactivate(self):
        self.active = False
        self.log("Controller deactivated.")

    def is_active(self):
        return self.active

    # -----------------------------
    # Mouse & Cursor Controls
    # -----------------------------
    async def move_cursor(self, direction: str, distance: int = 100):
        if not self.is_active():
            return "🛑 Controller inactive."
        try:
            x, y = pyautogui.position()
            if direction == "left": x -= distance
            elif direction == "right": x += distance
            elif direction == "up": y -= distance
            elif direction == "down": y += distance
            pyautogui.moveTo(x, y, duration=0.2)
            self.log(f"Mouse moved {direction}")
            return f"🖱️ Mouse moved {direction}."
        except Exception as e:
            self.log(f"move_cursor error: {e}")
            return f"❌ move_cursor failed: {e}"

    async def mouse_click(self, button: str = "left"):
        if not self.is_active():
            return "🛑 Controller inactive."
        try:
            if button == "left": pyautogui.click()
            elif button == "right": pyautogui.rightClick()
            elif button == "double": pyautogui.doubleClick()
            await asyncio.sleep(0.2)
            self.log(f"Mouse clicked {button}")
            return f"🖱️ {button.capitalize()} click."
        except Exception as e:
            self.log(f"mouse_click error: {e}")
            return f"❌ mouse_click failed: {e}"

    async def scroll_cursor(self, direction: str, amount: int = 10):
        if not self.is_active():
            return "🛑 Controller inactive."
        try:
            if direction == "up": pyautogui.scroll(amount * 100)
            elif direction == "down": pyautogui.scroll(-amount * 100)
            await asyncio.sleep(0.2)
            self.log(f"Mouse scrolled {direction}")
            return f"🖱️ Scrolled {direction}."
        except Exception as e:
            self.log(f"scroll_cursor error: {e}")
            return f"❌ scroll_cursor failed: {e}"

    async def swipe_gesture(self, direction: str):
        if not self.is_active():
            return "🛑 Controller inactive."
        try:
            screen_width, screen_height = pyautogui.size()
            x, y = screen_width // 2, screen_height // 2
            if direction == "up": pyautogui.moveTo(x, y + 200); pyautogui.dragTo(x, y - 200, duration=0.5)
            elif direction == "down": pyautogui.moveTo(x, y - 200); pyautogui.dragTo(x, y + 200, duration=0.5)
            elif direction == "left": pyautogui.moveTo(x + 200, y); pyautogui.dragTo(x - 200, y, duration=0.5)
            elif direction == "right": pyautogui.moveTo(x - 200, y); pyautogui.dragTo(x + 200, y, duration=0.5)
            await asyncio.sleep(0.5)
            self.log(f"Swipe gesture: {direction}")
            return f"🖱️ Swipe {direction} done."
        except Exception as e:
            self.log(f"swipe_gesture error: {e}")
            return f"❌ swipe_gesture failed: {e}"

    # -----------------------------
    # Keyboard Controls
    # -----------------------------
    async def type_text(self, text: str):
        if not self.is_active():
            return "🛑 Controller inactive."
        try:
            pyautogui.typewrite(text, interval=0.05)
            self.log(f"Typed text: {text}")
            return f"⌨️ Typed: {text}"
        except Exception as e:
            self.log(f"type_text error: {e}")
            return f"❌ type_text failed: {e}"

    async def press_key(self, key: str):
        if not self.is_active():
            return "🛑 Controller inactive."
        try:
            pyautogui.press(key)
            await asyncio.sleep(0.2)
            self.log(f"Pressed key: {key}")
            return f"⌨️ Key '{key}' pressed."
        except Exception as e:
            self.log(f"press_key error: {e}")
            return f"❌ Failed key: {key} — {e}"

    async def press_hotkey(self, keys: List[str]):
        if not self.is_active():
            return "🛑 Controller inactive."
        try:
            pyautogui.hotkey(*keys)
            await asyncio.sleep(0.2)
            self.log(f"Pressed hotkey: {' + '.join(keys)}")
            return f"⌨️ Hotkey {' + '.join(keys)} pressed."
        except Exception as e:
            self.log(f"press_hotkey error: {e}")
            return f"❌ Failed hotkey: {' + '.join(keys)} — {e}"

    async def control_volume(self, action: str):
        if not self.is_active():
            return "🛑 Controller inactive."
        try:
            if action == "up": pyautogui.press("volumeup")
            elif action == "down": pyautogui.press("volumedown")
            elif action == "mute": pyautogui.press("volumemute")
            await asyncio.sleep(0.2)
            self.log(f"Volume control: {action}")
            return f"🔊 Volume {action}."
        except Exception as e:
            self.log(f"control_volume error: {e}")
            return f"❌ control_volume failed: {e}"

    async def paste_and_send_text(self, text: str):
        if not self.is_active():
            return "🛑 Controller inactive."
        try:
            if pyperclip:
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            else:
                pyautogui.typewrite(text, interval=0.02)
            await asyncio.sleep(0.05)
            pyautogui.press('enter')
            self.log(f"Pasted and sent text: {text}")
            return f"✅ Pasted and sent text."
        except Exception as e:
            self.log(f"paste_and_send_text error: {e}")
            return f"❌ paste_and_send_text failed: {e}"

# ------------------------------
# LiveKit Tool Wrappers Section
# ------------------------------
controller = SafeController()

async def with_temp_activation(fn, *args, **kwargs):
    controller.activate("my_secret_token")
    result = await fn(*args, **kwargs)
    await asyncio.sleep(0.5)
    controller.deactivate()
    return result

@function_tool
async def move_cursor_tool(direction: str, distance: int = 100):
    return await with_temp_activation(controller.move_cursor, direction, distance)

@function_tool
async def mouse_click_tool(button: str = "left"):
    return await with_temp_activation(controller.mouse_click, button)

@function_tool
async def scroll_cursor_tool(direction: str, amount: int = 10):
    return await with_temp_activation(controller.scroll_cursor, direction, amount)

@function_tool
async def type_text_tool(text: str):
    return await with_temp_activation(controller.type_text, text)

@function_tool
async def press_key_tool(key: str):
    return await with_temp_activation(controller.press_key, key)

@function_tool
async def press_hotkey_tool(keys: List[str]):
    return await with_temp_activation(controller.press_hotkey, keys)

@function_tool
async def control_volume_tool(action: str):
    return await with_temp_activation(controller.control_volume, action)

@function_tool
async def swipe_gesture_tool(direction: str):
    return await with_temp_activation(controller.swipe_gesture, direction)

@function_tool
async def paste_and_send_text_tool(text: str):
    return await with_temp_activation(controller.paste_and_send_text, text)

# ------------------------------
# Quick test when running standalone
# ------------------------------
if __name__ == "__main__":
    async def main():
        print(await move_cursor_tool("right", 100))
        print(await mouse_click_tool("left"))
       
        print(await press_hotkey_tool(["ctrl", "a"]))
       

    asyncio.run(main())
