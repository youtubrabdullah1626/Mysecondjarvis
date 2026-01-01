import tkinter as tk
import pyperclip
import asyncio
from livekit.agents import function_tool

def show_code_popup(code: str, title: str = "Jarvis Code Output"):
    root = tk.Tk()
    root.title(title)
    root.geometry("800x600")
    frame = tk.Frame(root)
    frame.pack(expand=True, fill=tk.BOTH)
    text = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 12))
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
    text.configure(yscrollcommand=scrollbar.set)
    text.insert(tk.END, code)
    text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    def copy_to_clipboard():
        pyperclip.copy(code)
    copy_btn = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
    copy_btn.pack(pady=10)
    root.mainloop()

# --- LLM API Placeholder Functions ---



@function_tool
async def generate_code(prompt: str) -> str:
    try:
        await asyncio.sleep(0)  # Simulate async
        code = "def is_prime(n):\n    if n < 2: return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0: return False\n    return True"
        try:
            show_code_popup(code, title="Generated Code")
        except Exception as e:
            print(f"Popup दिखाने में दिक्कत: {e}")
            return f"Code generated, but popup failed: {e}\n{code}"
        return code
    except Exception as e:
        print(f"Code generation failed: {e}")
        return f"Code generation failed: {e}"



@function_tool
async def explain_code(code: str) -> str:
    try:
        await asyncio.sleep(0)
        explanation = "This function checks if a number is prime by testing divisibility from 2 up to sqrt(n). Returns True if prime, else False."
        try:
            show_code_popup(explanation, title="Code Explanation")
        except Exception as e:
            print(f"Popup दिखाने में दिक्कत: {e}")
            return f"Explanation generated, but popup failed: {e}\n{explanation}"
        return explanation
    except Exception as e:
        print(f"Code explanation failed: {e}")
        return f"Code explanation failed: {e}"



@function_tool
async def debug_code(code: str) -> str:
    try:
        await asyncio.sleep(0)
        debug = "No syntax errors detected. Logic appears correct for prime checking."
        try:
            show_code_popup(debug, title="Debugging Output")
        except Exception as e:
            print(f"Popup दिखाने में दिक्कत: {e}")
            return f"Debug info generated, but popup failed: {e}\n{debug}"
        return debug
    except Exception as e:
        print(f"Debugging failed: {e}")
        return f"Debugging failed: {e}"

# --- Example Usage ---
if __name__ == "__main__":
    # Simulate code generation
    prompt = "Write a Python function to check if a number is prime."
    code = generate_code(prompt)
    show_code_popup(code, title="Generated Code")
    # Simulate explanation
    explanation = explain_code(code)
    show_code_popup(explanation, title="Code Explanation")
    # Simulate debugging
    debug = debug_code(code)
    show_code_popup(debug, title="Debugging Output")
