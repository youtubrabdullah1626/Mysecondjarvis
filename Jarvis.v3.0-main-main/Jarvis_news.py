import platform
import requests
from livekit.agents import function_tool
import os
from dotenv import load_dotenv
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
if NEWS_API_KEY == 'c82a4c86db17447daa7c1b7c25f094d3':
    NEWS_API_KEY = NEWS_API_KEY.strip("'\"")
import pyautogui
import pytesseract

def speak(text):
    print(text)
@function_tool
async def get_news():
    """
    Fetches top 5 news headlines from NewsAPI for India and speaks them in English.
    """
    if not NEWS_API_KEY or NEWS_API_KEY == "YOUR_NEWS_API_KEY_HERE":
        speak("To use the news feature, please configure your News API Key first.")
        return None
    speak("Sure sir, I am fetching today's top news headlines.")
    main_url = f"https://newsapi.org/v2/everything?q=india&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(main_url)
        news_data = response.json()
        if news_data["status"] != "ok":
            speak("Sorry, I am unable to fetch news at the moment.")
            return None
        articles = news_data["articles"]
        headlines = []
        for article in articles[:5]:
            headlines.append(article['title'])
        if not headlines:
            speak("No major headlines found for today.")
            print("No headlines found. Full NewsAPI response:")
            print(news_data)
            return None
        speak("Today's top headlines are:")
        for i, headline in enumerate(headlines):
            speak(f"Headline number {i + 1}: {headline}")
        print("\nToday's top headlines:")
        for i, headline in enumerate(headlines):
            print(f"{i + 1}. {headline}")
        speak("These were today's latest headlines.")
        return headlines
    except requests.exceptions.RequestException:
        speak("There is a problem with the internet connection. Please check your connection.")
        return None
    except Exception as e:
        print(f"Error while fetching news: {e}")
        speak("Sorry, there was an unexpected problem fetching the news.")
        return None


def read_screen():
    # यह फंक्शन जैसा था वैसा ही रहेगा...
    speak("Okay sir, I am reading your screen.")
    try:
        screenshot = pyautogui.screenshot()
        text_on_screen = pytesseract.image_to_string(screenshot)
        if text_on_screen.strip():
            print("\n--- Text found on screen ---\n" + text_on_screen + "\n--------------------------\n")
            speak("I found this text on your screen.")
            speak(text_on_screen[:200]) # Shorten long text for reading
        else:
            speak("Sorry, I did not find any text on your screen.")
    except Exception as e:
        speak(f"An error occurred while reading the screen: {e}")


def process_command(command):
    """
    # Processes user commands.
    """
    command = command.lower()

    if "hello jarvis" in command or "hey jarvis" in command:
        speak("Hello sir, how can I help you?")
    elif "read my screen" in command:
        read_screen()
    # ===== नया कमांड यहाँ जोड़ा गया है =====
    elif (
        "latest news" in command
        or "samachar" in command
        or "khabar" in command
        or "news" in command
        or "aaj ka news" in command
        or "aaj ki khabar" in command
        or "aaj ki news" in command
        or "आज का समाचार" in command
        or "आज की खबर" in command
        or "आज की न्यूज़" in command
    ):
        import asyncio
        asyncio.run(get_news())
    # ======================================
    elif "what's your name" in command:
        speak("My name is Jarvis.")
    elif "exit" in command or "quit" in command:
        speak("Okay sir, goodbye!")
        return False
    else:
        speak("Sorry, I did not understand that command.")
    return True


if __name__ == "__main__":
    speak("Jarvis Assistant has started.")
    running = True
    while running:
        try:
            user_input = input("You: ")
            if user_input:
                running = process_command(user_input)
        except KeyboardInterrupt:
            speak("System is shutting down.")
            running = False