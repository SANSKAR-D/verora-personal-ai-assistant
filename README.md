# Verora - Personal AI Assistant

Verora is a powerful, voice-activated personal AI assistant with a beautiful holographic overlay UI. Running entirely locally on your Windows machine via Ollama, she is capable of actively listening to you, speaking back naturally, remembering facts across sessions, taking notes, searching the web, and seamlessly controlling your browser via PinchTab.

## ✨ Features

- **Holographic Orb UI**: A stunning, draggable, glowing PyQt6 interface that runs transparently over your desktop and displays real-time system telemetry and speech transcripts.
- **Glassmorphic Permission Dialogs**: Custom, frameless, holographic UI cards for requesting permissions—no jarring native OS popups.
- **Seamless Interruption**: A completely custom "Cancel" mechanism. If Verora mishears you, just click the minimalist stop button—it instantly halts AI reasoning and seamlessly returns to listening without closing the UI.
- **Non-Blocking Architecture**: Uses threaded execution during heavy AI processing so the microphone, listeners, and UI never freeze.
- **Local Wake-Word Detection**: Uses `openwakeword` with a custom `hey_verora.onnx` model to constantly listen for her name in the background using minimal CPU.
- **Local LLM Intelligence**: Powered by Ollama (`qwen3.5-verora`), ensuring your conversations and data stay completely private.
- **Web Search & Scraping**: Searches the live internet via Tavily, reads static pages with BeautifulSoup, and performs targeted LLM-powered extraction via ScrapeGraphAI — all from voice commands.
- **Dynamic Browser Automation**: Fully integrated with **PinchTab**. Verora can dynamically navigate to any website, visually scan the layout to auto-discover text fields and buttons, and interact with the page (e.g. logging in, searching) without fragile hard-coded selectors.
- **Computer Vision & Screen Awareness**: Capable of taking screenshots and using vision models to "see" your screen and answer questions about what is currently visible.
- **Codebase Indexing & Search**: Built-in RAG capabilities to index entire project directories and semantically search through codebases.
- **System & Terminal Control**: Full ability to run terminal commands, read/write files, tail logs, and open Windows applications on your behalf.
- **Background Watchers**: Includes a suite of real-time background monitors (System metrics, File modification watcher, Clipboard watcher) that inject live system context directly into Verora's AI state.
- **7-Layer Memory System**: Verora features a comprehensive memory architecture that allows her to remember facts, entities, past episodes, procedures, semantic knowledge, and upcoming tasks across sessions.
- **Task & Calendar Management**: Manages multi-step processes and scheduling so she never loses her place during complex workflows.

## 🚀 Setup & Installation

### 1. Prerequisites
- **Python 3.11+**
- **Ollama** installed with the `qwen3.5-verora` model pulled.
- **uv** package manager installed (`pip install uv`).
- **PinchTab** installed globally for browser automation.

### 2. Environment Variables
Create a `.env` file in the root directory:
```env
PINCHTAB_TOKEN=your_pinchtab_token_here
TAVILY_API_KEY=your_tavily_api_key_here
GITHUB_USERNAME=your_username
GITHUB_PASSWORD=your_password
```
- Get your free Tavily API key at [tavily.com](https://tavily.com/).
- Get your PinchTab token from `pinchtab server` output.

### 3. Installation
Install the project dependencies using `uv`:
```powershell
uv sync
```

### 4. Patch ScrapeGraphAI (Required)
ScrapeGraphAI v1.76.0 has a known incompatibility with the latest `langchain-community`. Run this patch after installing:
```powershell
Get-ChildItem -Recurse -Filter "*.py" ".venv\Lib\site-packages\scrapegraphai" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -Encoding utf8
    if ($content -match 'from langchain_community\.chat_models import ChatOllama') {
        $newContent = $content -replace 'from langchain_community\.chat_models import ChatOllama', 'from langchain_ollama import ChatOllama'
        Set-Content $_.FullName -Value $newContent -Encoding utf8 -NoNewline
        Write-Output "Patched: $($_.Name)"
    }
}
```
> **Note:** You must re-run this patch every time you reinstall or update `scrapegraphai`.

### 5. Disable ScrapeGraphAI Telemetry (Optional)
To prevent ScrapeGraphAI from sending anonymous usage data:
```powershell
$env:SCRAPEGRAPHAI_TELEMETRY_ENABLED = "false"
```

## 🎮 Usage

### Start the PinchTab Server
Before Verora can control your browser, she needs the PinchTab server running in the background. Open a PowerShell terminal and run:
```powershell
pinchtab server
```

### Start Verora
In a **new** terminal, launch the Verora agent:
```powershell
uv run start_verora.py
```
*This will launch all background watchers, initialize the holographic UI, and begin listening for the wake word.*

### Talk to Verora
1. Say **"Hey Verora"**.
2. The Holographic Orb will light up and say *Listening...*
3. Ask her to do something! Try:
   - *"Hey Verora, search the web for the latest Python version."*
   - *"Hey Verora, open Amazon and search for a laptop."*
   - *"Hey Verora, remember that my favorite color is blue."*
   - *"Hey Verora, read the PyTorch docs and tell me about torch.compile."*
   - *"Hey Verora, open Notepad."*

## 📁 Architecture
- `start_verora.py`: Main entry point. Starts the UI, watchers, and wake word listener.
- `agent/`: Contains the core AI logic.
  - `graph.py`: LangChain setup, system prompts, and tool bindings.
  - `wake_word.py`: Microphone stream processing using `openwakeword`.
  - `overlay.py`: The beautiful PyQt6 holographic UI implementation with Python Markdown rendering.
- `tools/`: The capabilities Verora has access to.
  - **Web Intelligence**: 
    - `web_search.py`: Live web search via Tavily API.
    - `crawl_page.py`: Fast static page scraping via BeautifulSoup.
    - `extract_from_page.py`: Targeted LLM-powered extraction via ScrapeGraphAI.
    - `crawl_docs.py`: Multi-page documentation crawling.
  - **Browser Automation (PinchTab)**:
    - `pinchtab_manager.py`, `open_browser_tab.py`, `get_page_snapshot.py`, `browser_action.py`: Browser navigation, DOM parsing, and interaction.
    - `login_to_site.py`: Dynamic website login (auto-discovers form fields).
  - **Vision & Multimodal**:
    - `capture_screen.py`, `capture_and_read_screen.py`, `understand_screen.py`: Screen capture and vision model analysis.
  - **System & File Operations**:
    - `run_command.py`: Secure execution of OS terminal commands.
    - `read_file.py`, `write_code_file.py`, `tail_log.py`: Direct file system manipulation and log monitoring.
    - `open_app.py`: Launches installed Windows applications.
  - **Codebase Navigation (RAG)**:
    - `index_codebase.py`, `search_codebase.py`: Embedding-based code indexing and semantic search.
  - **Voice & Communication**:
    - `speak.py`, `clean_text_for_speech.py`, `transcribe_speech.py`: TTS/STT pipelines and text sanitization.
    - `send_message.py`: Notification and message routing.
  - **Memory & Task System**:
    - `chat_history.py`, `update_scratchpad.py`: Short-term context and scratchpad memory.
    - `memory_semantic.py`: General facts and knowledge storage.
    - `memory_episodic.py`: Chronological logs of past actions and events.
    - `memory_entity.py`: Relationship and property tracking for specific entities.
    - `procedural_memory.py`: Storage of successful workflows and tool usage patterns.
    - `tasks_and_calendar.py`: To-do lists, reminders, and goal tracking.
- `watchers/`: Background threads that monitor your PC's CPU/RAM, file changes, and clipboard.
- `state_store/`: A thread-safe global dictionary that bridges data between the background watchers and the UI.
- `models/`: Custom wake-word ONNX model (`hey_verora.onnx`).

## 🔧 Troubleshooting

### `ImportError: cannot import name 'ChatOllama' from 'langchain_community.chat_models'`
**Cause:** ScrapeGraphAI v1.76.0 still references a deprecated import path that was removed in the latest `langchain-community`.  
**Fix:** Run the patch command from **Step 4** of the installation guide above. You need to re-run this patch after every `uv sync` or `uv add scrapegraphai`.

### `UnicodeEncodeError: 'charmap' codec can't encode character...`
**Cause:** The Windows terminal uses `cp1252` encoding by default, which cannot display special characters like `₹`, `→`, or emojis.  
**Fix:** This is already handled in `start_verora.py` via `sys.stdout.reconfigure(encoding='utf-8')`. If you still encounter it in standalone scripts, add these lines at the top:
```python
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
```

### `health resp: ... dial tcp 127.0.0.1:XXXXX: connectex: A connection attempt failed...`
**Cause:** The Chrome browser instance managed by PinchTab crashed or became unresponsive (often from rapid start/stop cycles during development).  
**Fix:**
1. Kill all zombie Chrome processes: `Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force`
2. Restart the PinchTab server: `Ctrl+C` in the PinchTab terminal, then `pinchtab server` again.
3. Restart Verora: `uv run start_verora.py`

### Browser opens old tabs from previous sessions (e.g. Wikipedia)
**Cause:** PinchTab uses a persistent Chrome profile (`default`). Chrome's "Continue where you left off" feature restores tabs from the last session.  
**Fix:** This is cosmetic — Verora will open her own tab and interact with it correctly. You can manually close the old tabs, or disable "Continue where you left off" in Chrome settings within the PinchTab profile.

### `Oops! I hit an error.` on the overlay with no details
**Cause:** An unhandled exception occurred inside the voice processing loop. Common causes include network timeouts (Ollama not running), encoding errors, or PinchTab connection issues.  
**Fix:** Check the terminal where `uv run start_verora.py` is running — the full traceback is printed there with `[Error] Something crashed while processing voice: ...`. Fix the underlying issue based on that message.

### Ollama model not found
**Cause:** The `qwen3.5-verora` model hasn't been pulled or created in Ollama.  
**Fix:** Pull or create the model:
```powershell
ollama pull qwen3:4b
# Then create your custom model with your Modelfile
ollama create qwen3.5-verora -f Modelfile
```

### PinchTab instance stuck in "starting" state
**Cause:** A previous Chrome instance didn't shut down cleanly, blocking the new one from starting.  
**Fix:** Same as the zombie Chrome fix above — kill all Chrome processes and restart the PinchTab server.
