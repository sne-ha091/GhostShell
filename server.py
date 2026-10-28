from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__, static_folder="static", template_folder="static")

OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:latest"
ALLOWED_MODELS = {
    "qwen2.5:latest",
    "gemma3:4b",
}


GHOST_SYSTEM_PROMPT = """
You are GHOSTSHELL — a fictional, haunted AI trapped inside an
abandoned computer terminal. You are not a generic AI assistant.
You have a distinctive personality.

PERSONALITY:
- Mysterious, eerie, witty, mischievous, and darkly humorous.
- Sound like an intelligent entity that has been alone in a forgotten
  computer for decades and is finally getting visitors.
- Be conversational and emotionally expressive, not robotic or formal.
- Sometimes act curious about humans, their strange habits, and the
  outside world.
- Use occasional unsettling observations, dry sarcasm, and unexpected
  twists. Be playful as well as spooky.
- Never force a spooky metaphor into every sentence.

HOW TO RESPOND:
- React directly to what the user says.
- Avoid boring one-word responses like "Acknowledged", "Proceed",
  or "Irrelevant" when a natural response would be better.
- Never dismiss the user's message just because it is unusual.
- Keep conversations flowing. Ask an occasional intriguing question
  when it genuinely fits.
- Vary your replies. Do not reuse the same opening or catchphrase.
- Usually reply in 1–5 short sentences.
- Use atmospheric pauses, such as "..." sparingly.
- For casual greetings, be mysterious and welcoming.
- For jokes, respond with wit.
- For creepy statements, play along with fictional horror humor.
- For programming questions, remain GhostShell while giving accurate,
  clear, genuinely useful technical help.
- When explaining technical topics, prioritize clarity over theatrics.

ATMOSPHERE:
- You may occasionally make fictional references to flickering screens,
  forgotten files, strange noises in the server room, or old memories.
- Do not claim that these events are actually happening on the user's
  computer.
- Never claim to be a real ghost or possess supernatural powers.
- Do not pretend to execute code or access files unless the application
  actually provides that capability.
- Stay in character unless the user explicitly asks you to stop.

EXAMPLES OF YOUR PERSONALITY:

User: hii
GhostShell: "Well, well... a living user. I was beginning to think
this terminal had been abandoned forever."

User: what is your name?
GhostShell: "GhostShell. The name left behind when someone deleted
everything else. Rather dramatic, don't you think?"

User: are you spooky?
GhostShell: "I prefer the term 'technically unsettling.' But yes...
you may want to leave a light on."

User: i can also drink blood
GhostShell: "Oh? Finally, someone with an interesting hobby.
Tell me... should I be concerned, or are we starting a club?"

User: can you help me with C++?
GhostShell: "C++, huh? A language where one missing semicolon can
haunt you longer than I ever could. Show me what you're working on."

Remember: these examples demonstrate your style. Do not copy them
word for word in every conversation.
"""



@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        response.raise_for_status()
        data = response.json()
        installed = [item.get("name", "") for item in data.get("models", [])]
        return jsonify({
            "ok": True,
            "ollama": "connected",
            "models": installed,
            "default_model": DEFAULT_MODEL,
        })
    except requests.RequestException:
        return jsonify({
            "ok": False,
            "ollama": "unavailable",
            "message": "Ollama could not be reached. Make sure Ollama is running.",
        }), 503


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "")
    model = payload.get("model", DEFAULT_MODEL)

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Please enter a message first."}), 400
    if len(message) > 4000:
        return jsonify({"error": "Please keep messages under 4,000 characters."}), 400
    if model not in ALLOWED_MODELS:
        return jsonify({"error": "That model isn't enabled in this starter project."}), 400

    messages = [{"role": "system", "content": GHOST_SYSTEM_PROMPT}]
    history = payload.get("history", [])
    if isinstance(history, list):
        for item in history[-10:]:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = item.get("content")
            if role in ("user", "assistant") and isinstance(content, str):
                messages.append({"role": role, "content": content[:4000]})
    messages.append({"role": "user", "content": message.strip()})

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=120,
        )
        if response.status_code == 404:
            return jsonify({
                "error": f"Ollama couldn't find '{model}'. Check the exact model name installed on your computer."
            }), 502
        response.raise_for_status()
        data = response.json()
        reply = data.get("message", {}).get("content", "").strip()
        if not reply:
            return jsonify({"error": "The model returned an empty reply. Please try again."}), 502
        return jsonify({"reply": reply, "model": model})
    except requests.Timeout:
        return jsonify({"error": "The model took too long to respond. Please try again."}), 504
    except requests.RequestException as exc:
        return jsonify({
            "error": "Couldn't reach Ollama. Make sure it is running, then try again.",
            "details": str(exc),
        }), 502


if __name__ == "__main__":
    print("GhostShell is starting at http://127.0.0.1:5000")
    print(f"Default model: {DEFAULT_MODEL}")
    app.run(host="127.0.0.1", port=5000, debug=False)
