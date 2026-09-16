import re
from agent.graph import agent
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
    question = transcribe_speech(duration=5)
    print(f"You said: {question}")

    answer = ask_streaming(question)
    print(f"Verora: {answer}")