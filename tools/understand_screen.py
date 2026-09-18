import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ollama
from tools.capture_screen import capture_active_window 


def understand_screen(image_path: str, question: str = "What does this show? Describe any text, code, or data visible.") -> str:
    """Passes a screenshot to the multimodal LLM and returns its description/reading of the content."""
    
    response = ollama.chat(
        model="qwen3.5-verora", 
        messages=[{
            "role": "user",
            "content": question,
            "images": [image_path],
        }],
    )
    return response["message"]["content"]

if __name__ == "__main__":
    path = capture_active_window()
    print(f"Captured: {path}")
    print("Asking LLM to describe it (this might take a few seconds)...")
    result = understand_screen(path)
    print(result)
