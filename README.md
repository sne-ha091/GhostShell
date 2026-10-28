# GhostShell 👻

A haunted-terminal web app powered by a locally running Ollama model. The ghost is fictional; the model runs on your computer.

## Features

- Retro green-on-black terminal interface
- AI-generated ghost programmer replies
- Local inference through Ollama
- Switch between Qwen 2.5 and Gemma 3
- Conversation history for the current page session
- Clear-conversation control and connection status
- No API key or hosted AI account required

## Requirements

- Python 3.10 or newer
- Ollama installed and running
- At least one supported model installed locally

This starter is configured for these Ollama model tags:
- `qwen2.5:latest`
- `gemma3:4b`

If your installed Gemma tag is different, update `ALLOWED_MODELS` in `server.py` and the corresponding option in `static/index.html` to match the exact name shown by Ollama.

## Run locally (Windows PowerShell)

1. Open this folder in VS Code.
2. Open a terminal in VS Code.
3. Create and activate a virtual environment (optional but recommended).
4. Install dependencies from `requirements.txt`.
5. Make sure Ollama is running and that your chosen model is installed.
6. Start the Flask server by running `server.py`.
7. Open `http://127.0.0.1:5000` in your browser.

### First-time setup notes

- Python packages need an internet connection to install unless already cached.
- Ollama needs to be running locally.
- The first response from a model can take longer while the model loads into memory.
- If the app says a model cannot be found, check the exact model tag installed in Ollama. The app's dropdown uses `qwen2.5:latest` and `gemma3:4b` by default.

## How it works

1. The browser sends a message to the Flask backend.
2. Flask sends the message to Ollama's local chat API.
3. Ollama runs the selected model on your machine.
4. Flask returns the response to the browser.

The app binds to `127.0.0.1`, so it is intended for local use by default.

## Open innovation

GhostShell demonstrates how open-weight models and local inference can make an AI experience usable without sending each conversation to a hosted AI provider. Once dependencies and the model are installed, the core chat can run without an internet connection. Users can inspect and modify the application and choose which supported local model to run.

Model availability, performance, and license terms depend on the model and the user's hardware. Review the model license before redistributing model files or packaging them with this project.

## Project structure

```text
GhostShell/
├── server.py
├── requirements.txt
├── README.md
├── .gitignore
└── static/
    ├── index.html
    ├── style.css
    └── script.js
```

## Troubleshooting

- **Local system offline:** Open Ollama and try again.
- **Model not found:** Check the exact installed model tag.
- **Python import error:** Confirm dependencies were installed in the active Python environment.
- **Port 5000 already in use:** Stop the other local server using that port before starting GhostShell.
