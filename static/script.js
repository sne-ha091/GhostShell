const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const conversation = document.querySelector("#conversation");
const statusBox = document.querySelector("#connection-status");
const statusLabel = document.querySelector("#status-label");
const modelSelect = document.querySelector("#model-select");
const modelLabel = document.querySelector("#model-label");
const clearButton = document.querySelector("#clear-button");
const toast = document.querySelector("#toast");

let history = [];
let toastTimer;

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.classList.toggle("error-toast", isError);
  toast.classList.add("show");
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => toast.classList.remove("show"), 3600);
}

function setConnection(ok, message) {
  statusBox.classList.toggle("connected", ok);
  statusBox.classList.toggle("error", !ok);
  statusLabel.textContent = message;
}

function updateModelLabel() {
  modelLabel.textContent = `MODEL: ${modelSelect.value.startsWith("qwen") ? "QWEN 2.5" : "GEMMA 3"}`;
}
modelSelect.addEventListener("change", updateModelLabel);
updateModelLabel();

function addMessage(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role === "user" ? "user-message" : "ghost-message"}`;

  const label = document.createElement("div");
  label.className = "message-label";
  const icon = document.createElement("span");
  icon.className = "ghost-icon";
  icon.textContent = role === "user" ? "⌁" : "◉";
  const name = document.createElement("span");
  name.textContent = role === "user" ? "YOU" : "THE GHOST";
  const time = document.createElement("span");
  time.className = "message-time";
  time.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  label.append(icon, name, time);

  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  article.append(label, paragraph);
  conversation.append(article);
  conversation.scrollTop = conversation.scrollHeight;
  return article;
}

function addTypingIndicator() {
  const article = addMessage("assistant", "Listening through the static...");
  article.classList.add("typing-message");
  return article;
}

async function checkHealth() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(data.message || "Ollama unavailable");
    setConnection(true, "LOCAL SYSTEM CONNECTED");
    const modelNames = data.models || [];
    if (!modelNames.includes(modelSelect.value)) {
      const matching = modelNames.find(name => name.toLowerCase().startsWith("qwen2.5"));
      if (matching) modelSelect.value = matching;
      updateModelLabel();
    }
  } catch {
    setConnection(false, "LOCAL SYSTEM OFFLINE");
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || sendButton.disabled) return;

  addMessage("user", message);
  const priorHistory = history.slice(-10);
  history.push({ role: "user", content: message });
  input.value = "";
  input.style.height = "auto";
  sendButton.disabled = true;
  sendButton.querySelector("span").textContent = "WAIT";
  const typing = addTypingIndicator();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        model: modelSelect.value,
        history: priorHistory
      })
    });
    const data = await response.json();
    typing.remove();
    if (!response.ok) throw new Error(data.error || "Something went wrong.");
    addMessage("assistant", data.reply);
    history.push({ role: "assistant", content: data.reply });
    setConnection(true, "LOCAL SYSTEM CONNECTED");
  } catch (error) {
    typing.remove();
    addMessage("assistant", `The signal broke: ${error.message}`);
    setConnection(false, "CONNECTION INTERRUPTED");
  } finally {
    sendButton.disabled = false;
    sendButton.querySelector("span").textContent = "SEND";
    input.focus();
  }
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
});

clearButton.addEventListener("click", () => {
  history = [];
  conversation.replaceChildren();
  const line = document.createElement("div");
  line.className = "system-line";
  line.textContent = "[!] CONVERSATION PURGED";
  const greeting = document.createElement("article");
  greeting.className = "message ghost-message";
  const label = document.createElement("div");
  label.className = "message-label";
  label.textContent = "◉ THE GHOST";
  const paragraph = document.createElement("p");
  paragraph.textContent = "...a clean slate. What do you want to know, traveler?";
  greeting.append(label, paragraph);
  conversation.append(line, greeting);
  showToast("Conversation cleared from this page.");
});

checkHealth();
