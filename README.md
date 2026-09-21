# Verora - Personal AI Assistant

Verora is a powerful, voice-activated personal AI assistant with a beautiful holographic overlay UI. Running entirely locally on your Windows machine via Ollama, she is capable of actively listening to you, speaking back naturally, remembering facts across sessions, taking notes, and seamlessly controlling your browser via PinchTab.

## ✨ Features

- **Holographic Orb UI**: A stunning, draggable, glowing PyQt6 interface that runs transparently over your desktop and displays real-time system telemetry and speech transcripts.
- **Local Wake-Word Detection**: Uses `openwakeword` with a custom `hey_verora.onnx` model to constantly listen for her name in the background using minimal CPU.
- **Local LLM Intelligence**: Powered by Ollama (`qwen3.5-verora`), ensuring your conversations and data stay completely private.
- **Dynamic Browser Automation**: Fully integrated with **PinchTab**. Verora can dynamically navigate to any website, visually scan the layout to auto-discover text fields and buttons, and interact with the page (e.g. logging in, searching) without fragile hard-coded selectors.
- **Background Watchers**: Includes a suite of real-time background monitors (System metrics, File modification watcher, Clipboard watcher) that inject live system context directly into Verora's AI state.
- **Permanent Memory**: Maintains a `long_term_memory.txt` that she updates to remember important facts about you forever.
- **Task Management**: Uses a `scratchpad.txt` to keep track of multi-step processes so she never loses her place during complex workflows.

## 🚀 Setup & Installation

### 1. Prerequisites
- **Python 3.11+**
- **Ollama** installed with the `qwen3.5-verora` model pulled.
- **uv** package manager installed (`pip install uv`).
- **PinchTab** installed globally for browser automation.

### 2. Environment Variables
Create a `.env` file in the root directory. You can add site credentials here for Verora's auto-login feature:
```env
PINCHTAB_TOKEN=your_pinchtab_token_here
GITHUB_USERNAME=your_username
GITHUB_PASSWORD=your_password
```

### 3. Installation
Install the project dependencies using `uv`:
```powershell
uv sync
```

## 🎮 Usage

### Start the PinchTab Server
Before Verora can control your browser, she needs the PinchTab server running in the background. Open a PowerShell terminal and run:
```powershell
pinchtab server
```

### Start Verora
In a new terminal, launch the Verora agent:
```powershell
uv run start_verora.py
```
*Note: This will launch all background watchers, initialize the holographic UI, and begin listening for the wake word.*

### Talk to Verora
1. Say **"Hey Verora"**.
2. The Holographic Orb will light up and say *Listening...*
3. Ask her to do something! Try:
   - *"Hey Verora, search Wikipedia for Dragon."*
   - *"Hey Verora, open Amazon and search for a laptop."*
   - *"Hey Verora, remember that my favorite color is blue."*
   - *"Hey Verora, open Notepad."*

## 📁 Architecture
- `start_verora.py`: Main entry point. Starts the UI, watchers, and wake word listener.
- `agent/`: Contains the core AI logic.
  - `graph.py`: LangChain setup, system prompts, and tool bindings.
  - `wake_word.py`: Microphone stream processing using `openwakeword`.
  - `overlay.py`: The beautiful PyQt6 holographic UI implementation.
- `tools/`: The capabilities Verora has access to (PinchTab navigation, memory updating, app opening).
- `watchers/`: Background threads that monitor your PC's CPU/RAM, file changes, and clipboard.
- `state_store/`: A thread-safe global dictionary that bridges data between the background watchers and the UI.
