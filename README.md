# Pulse AI - ScaleDown Ecosystem

**Pulse AI** is a high-performance, voice-enabled AI assistant built as part of the ScaleDown ecosystem. It leverages the **OpenRouter API** (specifically the **Trinity** model with reasoning capabilities) to provide intelligent, context-aware responses.

## 🚀 Features

*   **Advanced AI Model**: Powered by `arcee-ai/trinity-large-preview:free` via OpenRouter, supporting chain-of-thought reasoning.
*   **Voice Interaction**:
    *   **Wake Word Detection**: Low-latency detection using Google Speech Recognition (supports "Pulse", "Hello", "Hi").
    *   **Text-to-Speech (TTS)**: Robust, thread-safe output using Windows System Speech (PowerShell) to avoid COM threading issues.
    *   **Continuous Conversation**: Intelligent listening loop that remains active for 20 seconds after a response, allowing for natural back-and-forth dialogue.
*   **Live UI Sync**: The Streamlit-based web interface automatically updates in real-time to display voice transcriptions and AI responses.
*   **Memory & Context**:
    *   Local SQLite database for persistent chat history.
    *   Context optimization strategy (mocked/integrated via ScaleDown concepts).
*   **Training Data Export**: Built-in tool to export conversation history to JSONL format for future LLM fine-tuning.

## 🛠️ Installation

### Prerequisites
*   Python 3.8+
*   Windows OS (for PowerShell TTS support)
*   Microphone and Speakers

### Setup
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Abhijit1018/scaledown.git
    cd scaledown
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: You may need to install `pyaudio` separately if the direct install fails.*

3.  **Environment Configuration**:
    *   The application uses `pulse/config.py` for configuration.
    *   Ensure your `OPENROUTER_API_KEY` is set in your environment variables or updated in `config.py`.

## 🖥️ Usage

### Running the Application
Launch the Pulse AI interface:
```bash
python -m streamlit run pulse/app.py
```
The application will open in your default browser at `http://localhost:8501`.

### Voice Commands
1.  **Start Voice**: Click the **Start Voice** button in the sidebar.
2.  **Wake Up**: Say **"Pulse"** or **"Hello"**.
3.  **Command**: Wait for the "Yes?" prompt, then speak your request.
    *   *Example: "What time is it?"*
    *   *Example: "Tell me a joke."*
4.  **Continuous Mode**: After the AI responds, it will keep listening for 20 seconds. You can continue the conversation without saying the wake word again.
5.  **Stop**: Say **"Stop"**, **"Exit"**, or **"Goodbye"** to end the voice session visually, or click **Stop Voice** in the UI.

### Training Data Export
To export your chat history for training:
```bash
python pulse/tools/export_memory.py
```
This generates a `training_data/chat_history_export.jsonl` file.

## 📂 Project Structure

*   `pulse/app.py`: Main Streamlit web application.
*   `pulse/core/`: Core logic (Brain, Memory, LLM Clients).
*   `pulse/voice/`: Voice processing (STT, TTS, Voice Loop).
*   `pulse/config.py`: Configuration settings.
*   `pulse/tools/`: Utility scripts (e.g., memory export).

## 📝 Specifications

*   **LLM Provider**: OpenRouter
*   **Default Model**: `arcee-ai/trinity-large-preview:free`
*   **Database**: SQLite (`pulse_memory.db`)
*   **Voice Stack**:
    *   STT: `SpeechRecognition` (Google Web API for Wake Word, Whisper for dictation typically, but currently optimized to Google for speed).
    *   TTS: PowerShell `System.Speech`.

---
*Built by Pulse AI Team*
