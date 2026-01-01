import tkinter as tk
import os
import time
import pyautogui
from livekit.agents import function_tool

def speak(text):
    print(f"Jarvis: {text}")

@function_tool
async def take_screenshot():
    try:
        # 1. Check/create screenshots folder
        folder = "screenshots"
        if not os.path.exists(folder):
            os.makedirs(folder)
        # 2. Unique filename
        filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".png"
        full_path = os.path.join(folder, filename)
        # 3. Take screenshot and save
        screenshot = pyautogui.screenshot()
        screenshot.save(full_path)
        # 4. Confirmation
        speak(f"स्क्रीनशॉट ले लिया गया है: {full_path}")
        def show_popup():
            try:
                from PIL import Image, ImageTk
                import tkinter.filedialog as filedialog
                root = tk.Tk()
                root.title("Screenshot Saved")
                root.geometry("600x400")
                label = tk.Label(root, text=f"Screenshot saved:\n{full_path}", font=("Arial", 12))
                label.pack(pady=10)
                img = Image.open(full_path)
                img.thumbnail((500, 300))
                img_tk = ImageTk.PhotoImage(img)
                img_label = tk.Label(root, image=img_tk)
                img_label.image = img_tk
                img_label.pack(pady=10)
                def save_as():
                    save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
                    if save_path:
                        img.save(save_path)
                        label.config(text=f"Screenshot saved as:\n{save_path}")
                btn_save = tk.Button(root, text="Save As", command=save_as)
                btn_save.pack(pady=5)
                btn_ok = tk.Button(root, text="OK", command=root.destroy)
                btn_ok.pack(pady=5)
                root.mainloop()
            except Exception as e:
                speak(f"स्क्रीनशॉट तो ले लिया, लेकिन popup दिखाने में दिक्कत आई: {e}")
        import threading
        threading.Thread(target=show_popup).start()
        return f"Screenshot saved: {full_path}"
    except Exception as e:
        speak(f"स्क्रीनशॉट लेने में असमर्थ: {e}")
        return f"Error taking screenshot: {e}"

if __name__ == "__main__":
    import asyncio
    asyncio.run(take_screenshot())
