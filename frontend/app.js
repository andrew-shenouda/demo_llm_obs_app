const input = document.getElementById("input");
const messages = document.getElementById("messages");

async function sendMessage() {
  const userMessage = input.value;
  if (!userMessage) return;

  appendMessage("You", userMessage, "user");
  input.value = "";

  try {
    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage })
    });
    const data = await res.json();
    if (data.reply) {
      appendMessage("Bot", data.reply, "bot");
    } else {
      appendMessage("Bot", "Error: " + (data.error || "Unknown"), "bot");
    }
  } catch (e) {
    appendMessage("Bot", "Error: " + e.message, "bot");
  }
}

function appendMessage(sender, text, className) {
  const div = document.createElement("div");
  div.className = `message ${className}`;
  div.innerHTML = `<strong>${sender}:</strong> ${text}`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}
