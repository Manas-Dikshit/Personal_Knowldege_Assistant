# MRD AI Desktop Assistant (Offline Edition)

![CI](https://github.com/Manas-Dikshit/MRD_AI_Desktop_Assistant/actions/workflows/ci.yml/badge.svg)

A fully offline, advanced desktop AI assistant for Windows. It runs in the background, listens for a global hotkey, and uses a local Ollama model for intelligence.

## Features

- **Offline & Private**: Uses local Ollama models (Llama 3, Mistral, etc.) and offline speech recognition (Vosk).
- **System Tray Control**: Runs silently in the background with a tray icon to pause/resume/quit.
- **Global Hotkey**: Press `Ctrl+Shift+M` to wake the assistant.
- **System Control**: Open apps, websites, and get system info.
- **Auto-Startup**: Automatically runs when Windows starts.

## Prerequisites

1.  **Python 3.11+**
2.  **Ollama**: Download and install from [ollama.com](https://ollama.com/).
    -   Pull a model: `ollama pull llama3` (or your preferred model).
3.  **Vosk Model**:
    -   Download a small English model from [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models).
    -   Recommended: `vosk-model-small-en-us-0.15`.
    -   Extract the folder and rename it to `model`.
    -   Place the `model` folder in the root of this project.

## Languages

-   **English**: Default. Uses `model` folder.
-   **Hindi**: Run `python setup/download_hindi_model.py`. Change `model_path` in `config.json` to `"model_hi"`.
-   **Odia**: Currently **not supported** for offline recognition by Vosk.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd MRD_AI_Desktop_Assistant
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If `pyaudio` fails, download the `.whl` file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install manually.*

3.  **Configuration**:
    -   Edit `config/config.json` to customize:
        -   `ai.model`: The Ollama model name (e.g., "llama3").
        -   `voice.model_path`: Path to your Vosk model folder (default: "model").
        -   `hotkey`: Activation shortcut.
        -   `paths`: Application paths.

## Usage

1.  **Run the Assistant**:
    ```bash
    python main.py
    ```
    The assistant will start and minimize to the system tray.

2.  **Interact**:
    -   Press **Ctrl+Shift+M**.
    -   Wait for "Yes, I'm listening...".
    -   Speak your command (e.g., "Open Chrome", "What is the capital of France?").

3.  **Tray Menu**:
    -   Right-click the tray icon (blue/white square) to Pause, Resume, or Quit.

## Troubleshooting

-   **"Vosk model not found"**: Ensure the `model` folder exists in the project root and contains the model files.
-   **"Could not connect to Ollama"**: Ensure Ollama is running (`ollama serve` or via desktop app).
-   **Microphone issues**: Check Windows sound settings.

## License

MIT
#
