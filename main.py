import re
from agent.graph import agent, ask_with_pruning
from tools.transcribe_speech import transcribe_speech
from tools.speak import speak

def ask_streaming(question: str):
    full_response = ""
    buffer = ""
    for chunk in agent.stream({"messages": [{"role": "user", "content": question}]}, stream_mode="messages"):
        token = chunk[0].content if chunk[0].content else ""
        buffer += token
        full_response += token

        if re.search(r'[.!?]\s', buffer):
            sentence, _, buffer = buffer.rpartition('. ')
            if sentence:
                try:
                    speak(sentence)
                except Exception as e:
                    print(f"[speak error, skipping sentence] {e}")

    if buffer.strip():
        try:
            speak(buffer)
        except Exception as e:
            print(f"[speak error, skipping final buffer] {e}")

    return full_response

if __name__ == "__main__":
    print("Verora Voice Interface Started. Speak into your microphone!")
    
    # Initialize the empty history list before the loop starts
    chat_history = []
    
    while True:
        # 1. Listen for the user's voice
        question = transcribe_speech(duration=5)
        
        # Only process if they actually said something
        if question.strip():
            print(f"You said: {question}")
            
            # 2. Pass the question AND the history to the agent.
            # It will return the updated history and the final answer.
            chat_history, answer = ask_with_pruning(question, chat_history, max_history=10)
            
            print(f"Verora: {answer}")
            
            # 3. Speak the answer out loud
            speak(answer)
