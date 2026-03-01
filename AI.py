import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import random
import pyautogui
import pywhatkit # New library for playing songs

# --- CONFIGURATION ---
USER_NAME = "Siddharth"
ASSISTANT_NAME = "alexa"

engine = pyttsx3.init()

def speak(text):
    print(f"{ASSISTANT_NAME}: {text}")
    engine.say(text)
    engine.runAndWait()

def process_command(command):
    command = command.lower()

    # 1. PERSONALIZED HELP & IDENTITY
    if "how can you help" in command:
        speak(f"Hello {USER_NAME}! I can control your laptop, play songs on YouTube, update VS Code, or open Chrome.")

    elif "what are you doing" in command:
        speak(f"I'm keeping an eye on your system and waiting for your commands, {USER_NAME}.")

    # 2. NEW FEATURE: YOUTUBE & MUSIC
    elif "play" in command:
        # Extract song name (e.g., "play isk risk" -> "isk risk")
        song = command.replace("play", "").strip()
        speak(f"Sure {USER_NAME}, playing {song} on YouTube.")
        pywhatkit.playonyt(song)

    elif "open youtube" in command:
        speak(f"Opening YouTube, {USER_NAME}.")
        webbrowser.open("https://www.youtube.com")

    # 3. SOFTWARE UPDATES
    elif "update vs code" in command:
        speak(f"Checking for updates for Visual Studio Code, {USER_NAME}...")
        os.system("winget upgrade --id Microsoft.VisualStudioCode --silent")
        speak("The update is running in the background.")

    # 4. CHROME & SYSTEM CONTROL
    elif "open chrome" in command:
        speak("Opening Chrome.")
        webbrowser.open("https://www.google.com")

    elif "minimize" in command:
        speak("Minimizing windows.")
        pyautogui.hotkey('win', 'd')

    elif "exit" in command:
        speak(f"Goodbye, {USER_NAME}!")
        return False
    
    return True

def start_assistant():
    recognizer = sr.Recognizer()
    speak(f"Ready for you, {USER_NAME}.")
    
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=5)
                user_text = recognizer.recognize_google(audio)
                print(f"{USER_NAME}: {user_text}")
                if not process_command(user_text):
                    break
            except:
                pass

if __name__ == "__main__":
    start_assistant()