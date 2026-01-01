import subprocess
import psutil
import platform
import time
# pyautogui को अभी इस्तेमाल नहीं किया जा रहा है, पर रख सकते हैं
# from livekit.agents import function_tool # अभी इस्तेमाल नहीं हो रहा

# speedtest-cli को सुरक्षित रूप से इम्पोर्ट करें
try:
    import speedtest
except ImportError:
    speedtest = None


def speak(text):
    """सिस्टम की आवाज में टेक्स्ट बोलता है।"""
    print(f"Jarvis: {text}")
    # विंडोज के लिए PowerShell का उपयोग करके बोलना
    if platform.system() == "Windows":
        try:
            # PowerShell कमांड में डबल कोट्स को एस्केप करना महत्वपूर्ण है
            escaped_text = text.replace('"', '`"')
            powershell_command = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{escaped_text}");'
            subprocess.run(["powershell.exe", "-Command", powershell_command], check=True, capture_output=True, text=True)
        except Exception as e:
            print(f"(बोलने में असमर्थ: {e})")
    # यहां macOS और Linux के लिए कोड जोड़ा जा सकता है
    # ...

async def get_system_performance():
    """CPU, RAM, डिस्क उपयोगिता की जानकारी देता है।"""
    speak("सिस्टम के प्रदर्शन की जांच कर रहा हूँ।")
    await asyncio.sleep(0)  # allow async context
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        performance = (
            f"CPU उपयोग: {cpu_percent}%\n"
            f"RAM उपयोग: {ram.percent}%\n"
            f"डिस्क उपयोग: {disk.percent}%"
        )
        return performance
    except Exception as e:
        print(f"Error checking system performance: {e}")
        return "माफ़ कीजिए, मैं सिस्टम प्रदर्शन की जानकारी प्राप्त नहीं कर सका।"

import asyncio
async def get_battery_status():
    """बैटरी की स्थिति की जांच करता है और एक स्ट्रिंग लौटाता है।"""
    speak("बैटरी की स्थिति की जांच कर रहा हूँ।")
    await asyncio.sleep(0)  # allow async context
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return "माफ़ कीजिए, इस डिवाइस पर बैटरी की जानकारी नहीं मिल सकती। यह शायद एक डेस्कटॉप कंप्यूटर है।"

        percent = battery.percent
        is_charging = battery.power_plugged
        
        status_message = f"बैटरी {percent}% पर है"
        if is_charging:
            status_message += " और डिवाइस चार्ज हो रहा है।"
        else:
            status_message += " और डिवाइस चार्जिंग पर नहीं है।"
            
        if percent < 20 and not is_charging:
            status_message += "\nचेतावनी! बैटरी बहुत कम है। कृपया चार्जर कनेक्ट करें।"
            
        return status_message
    except Exception as e:
        print(f"Error checking battery: {e}")
        return "माफ़ कीजिए, मैं बैटरी की स्थिति की जानकारी प्राप्त नहीं कर सका।"

def get_internet_speed():
    """इंटरनेट की गति की जांच करता है और एक स्ट्रिंग लौटाता है।"""
    if not speedtest:
        return "Speedtest मॉड्यूल इंस्टॉल नहीं है। कृपया 'pip install speedtest-cli' चलाएँ।"
        
    speak("ठीक है सर, मैं इंटरनेट की गति की जांच कर रहा हूँ। इसमें थोड़ा समय लग सकता है, कृपया धैर्य रखें।")
    try:
        st = speedtest.Speedtest()
        
        speak("सबसे अच्छे सर्वर को ढूंढा जा रहा है...")
        st.get_best_server()
        
        speak("डाउनलोड स्पीड की गणना कर रहा हूँ...")
        download_speed_bps = st.download()
        download_speed_mbps = round(download_speed_bps / (10**6), 2)
        
        speak("अपलोड स्पीड की गणना कर रहा हूँ...")
        upload_speed_bps = st.upload()
        upload_speed_mbps = round(upload_speed_bps / (10**6), 2)
        
        return f"जांच पूरी हुई। आपकी डाउनलोड स्पीड {download_speed_mbps} Mbps और अपलोड स्पीड {upload_speed_mbps} Mbps है।"
    except speedtest.ConfigRetrievalError:
        return "माफ़ कीजिए, मैं इंटरनेट स्पीड की जांच नहीं कर सका। कृपया अपने इंटरनेट कनेक्शन की जांच करें।"
    except Exception as e:
        print(f"Error checking internet speed: {e}")
        return "इंटरनेट स्पीड की जांच के दौरान एक अनपेक्षित त्रुटि हुई।"

def process_command(command):
    """यूजर के कमांड को प्रोसेस करता है।"""
    command = command.lower()
    
    if "performance" in command or "cpu" in command or "ram" in command:
        result = get_system_performance()
        speak(result)
    elif "battery" in command:
        result = get_battery_status()
        speak(result)
    elif "internet speed" in command or "speed test" in command:
        result = get_internet_speed()
        speak(result)
    elif "exit" in command or "quit" in command or "band karo" in command:
        speak("ठीक है सर, अलविदा!")
        return False # लूप को रोकने के लिए False लौटाएँ
    else:
        speak("माफ़ कीजिए, मैं यह कमांड समझ नहीं पाया।")
        
    return True # लूप जारी रखने के लिए True लौटाएँ

if __name__ == "__main__":
    speak("सिस्टम मॉनिटरिंग मॉड्यूल के साथ Jarvis ऑनलाइन है।")
    running = True
    while running:
        try:
            user_input = input("आप: ")
            if user_input:
                running = process_command(user_input)
        except KeyboardInterrupt:
            speak("सिस्टम बंद हो रहा है।")
            running = False