from openwakeword.model import Model
import sounddevice as sd
import numpy as np
import threading
from agent.overlay import signals
from state_store.state import store

from tools.transcribe_speech import transcribe_speech
from tools.speak import speak
from agent.graph import ask_with_pruning

oww_model = Model(
    # wakeword_models=["hey_jarvis"],
    wakeword_models=["./models/hey_verora.onnx"],
    inference_framework="onnx"
) 

chat_history = []
is_busy = False

def on_wake_word_detected():
    global chat_history, is_busy
    
    try:
        signals.show_signal.emit()
        
        # Turn the switch ON
        store.update("overlay_open", True)
        
        # Keep having a conversation until the switch is flipped OFF
        while store.get("overlay_open"):
            signals.update_signal.emit("Listening...")

            question = transcribe_speech(duration=5)
            
            # If you didn't say anything, just loop back and listen again!
            if not question.strip():
                continue
                
            signals.update_signal.emit(f"You said: {question}")
            chat_history, answer = ask_with_pruning(question, chat_history, max_history=10)
            
            # If she closed the overlay during that answer, the loop will break on the NEXT pass
            signals.update_signal.emit("Speaking...")
            speak(answer)
            
            # Clear the text after speaking
            signals.update_signal.emit("")
            
    except Exception as e:
        print(f"\n[Error] Something crashed while processing voice: {e}")
        signals.update_signal.emit("Oops! I hit an error.")
        
    finally:
        print("[WakeWord] Resetting listener...")
        is_busy = False
        store.update("overlay_open", False)

def listen_for_wake_word():
    
    def callback(indata, frames, time_info, status):
        global is_busy  # <--- MUST BE INSIDE THE CALLBACK
        
        # If Verora is already talking or listening, ignore new audio
        if is_busy:
            return
            
        audio = np.frombuffer(indata, dtype=np.int16)
        prediction = oww_model.predict(audio)
        for wakeword, score in prediction.items():
            if score > 0.03:
                oww_model.reset()
                is_busy = True # Lock it so it doesn't double-trigger
                
                # --- NEW: Run the heavy AI stuff in a separate thread so the mic doesn't freeze! ---
                threading.Thread(target=on_wake_word_detected, daemon=True).start()

    with sd.InputStream(callback=callback, channels=1, samplerate=16000, dtype='int16'):
        while True:
            sd.sleep(100)


def start_wake_word_listener():
    thread = threading.Thread(target=listen_for_wake_word, daemon=True)
    thread.start()
