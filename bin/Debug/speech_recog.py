import speech_recognition as sr
import sys

def recognize_speech():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("LISTENING...", flush=True)
        recognizer.adjust_for_ambient_noise(source, duration=2)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            
            try:
                text = recognizer.recognize_google(audio)
                print(f"RESULT:{text}", flush=True)
                return text
            except sr.UnknownValueError:
                print("ERROR: Could not understand audio", flush=True)
                return None
            except sr.RequestError as e:
                print(f"ERROR: Service error - {e}", flush=True)
                return None
                
        except sr.WaitTimeoutError:
            print("ERROR: No speech detected", flush=True)
            return None

if __name__ == "__main__":
    result = recognize_speech()
    if result is None:
        sys.exit(1)