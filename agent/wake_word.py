from openwakeword.model import Model
import sounddevice as sd
import numpy as np
import threading
from agent.overlay import signals
from state_store.state import store

from tools.transcribe_speech import transcribe_speech
from tools.speak import speak
from agent.graph import ask_with_pruning
from tools.chat_history import load_chat_history, save_chat_history

oww_model = Model(
    # wakeword_models=["hey_jarvis"],
    wakeword_models=["./models/hey_verora.onnx"],
    inference_framework="onnx"
) 

chat_history = load_chat_history()
is_busy = False

def on_wake_word_detected():
    global chat_history, is_busy
    
    try:
        signals.show_signal.emit()
        store.update("overlay_open", True)
        
        signals.update_signal.emit("Listening...")
        question = transcribe_speech(duration=5)
        
        if not question.strip():
            # If no question was asked, tell the user and go back to sleep
            signals.update_signal.emit("I didn't catch that...")
            import time
            time.sleep(1.5)
            return
            
        print(f"\n{'='*50}")
        print(f"[Verora] USER SAID: \"{question}\"")
        print(f"{'='*50}\n")
        
        signals.update_signal.emit(f"You said: {question}")
        # Keep only the last 4 messages (2 full exchanges) to prevent the AI from drowning in past context
        chat_history, answer = ask_with_pruning(question, chat_history, max_history=4)
        save_chat_history(chat_history)
        
        # Guard against None or empty answers
        if not answer:
            answer = "I processed your request but didn't generate a response."
        
        # Strip any leftover XML thinking tags from Qwen3
        import re
        # Remove <think> reasoning (internal thought, not for user)
        answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL)
        answer = re.sub(r'<think>.*', '', answer, flags=re.DOTALL)
        
        answer = re.sub(r'<\|.*?\|>', '', answer)
        answer = answer.strip()
        
        if not answer:
            answer = "Done. I completed your request."
        
        print(f"[Verora] Clean answer ({len(answer)} chars): {answer[:200]}...")
        
        # Parse spoken vs displayed text
        import re
        speak_match = re.search(r'<speak>(.*?)</speak>', answer, re.DOTALL)
        if speak_match:
            spoken_text = speak_match.group(1).strip()
            display_text = answer.replace(speak_match.group(0), '').strip()
            if not display_text:
                display_text = spoken_text
        else:
            # Fallback if AI forgot tags but generated a huge response
            if len(answer) > 200:
                spoken_text = "Here is the detailed information you requested."
                display_text = answer
            else:
                spoken_text = answer
                display_text = answer
        # Strip HTML block tags that disable Markdown parsing
        display_text = re.sub(r'</?(details|summary)>', '', display_text)
        
        # Always pop up the big translucent black screen
        signals.large_text_signal.emit(display_text)
        
        signals.update_signal.emit("Speaking...")
        speak(spoken_text)
        
        signals.update_signal.emit("")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[Error] Something crashed while processing voice: {e}")
        signals.update_signal.emit(f"Error: {e}")
        import time
        time.sleep(3)  # Give user time to read the error
        
    finally:
        print("[WakeWord] Task complete. Returning to sleep...")
        signals.hide_signal.emit()
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
