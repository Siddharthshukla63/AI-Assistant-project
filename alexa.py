import speech_recognition as sr
import pyttsx3
import pywhatkit

# Initialize the listener and the "voice" of the assistant
listener = sr.Recognizer()
engine = pyttsx3.init()

def talk(text):
    """Makes the assistant speak."""
    engine.say(text)
    engine.runAndWait()

def take_command():
    """Listens to the microphone and returns the recognized text."""
    try:
        with sr.Microphone() as source:
            print("Listening...")
            # Adjust for background noise
            listener.adjust_for_ambient_noise(source, duration=1)
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'assistant' in command:
                command = command.replace('assistant', '')
            print(f"You said: {command}")
            return command
    except Exception as e:
        print("Could not understand audio.")
        return ""

def run_assistant():
    """Main logic to process commands."""
    command = take_command()
    
    if 'play' in command:
        song = command.replace('play', '').strip()
        talk(f"Playing {song}")
        # This will open YouTube and play the most relevant video
        pywhatkit.playonyt(song)
    elif 'open youtube' in command:
        talk("Opening YouTube")
        pywhatkit.playonyt("https://www.youtube.com")
    else:
        talk("I didn't quite catch that. Please say play followed by the song name.")

# Start the assistant
if __name__ == "__main__":
    talk("I am ready. How can I help you?")
    run_assistant()