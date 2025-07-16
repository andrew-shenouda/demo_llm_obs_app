// DOM Elements
const input = document.getElementById("input");
const messages = document.getElementById("messages");
const sendButton = document.querySelector("button");

// Chat API Configuration
const API_CONFIG = {
  url: "http://localhost:8000/agents/chat",
  headers: {
    "Content-Type": "application/json"
  }
};

// Typing Indicator Management
class TypingIndicator {
  constructor() {
    this.currentIndicator = null;
  }

  show() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "message bot typing-indicator";
    typingDiv.innerHTML = `
      <strong>AI Assistant</strong>
      <div class="typing-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    `;
    typingDiv.style.display = "block";
    messages.appendChild(typingDiv);
    messages.scrollTop = messages.scrollHeight;
    this.currentIndicator = typingDiv;
  }

  hide() {
    if (this.currentIndicator && this.currentIndicator.parentNode) {
      this.currentIndicator.parentNode.removeChild(this.currentIndicator);
      this.currentIndicator = null;
    }
  }
}

// Message Management
class MessageManager {
  static formatMessage(text) {
    // Convert markdown-style formatting to HTML
    let formattedText = text;
    
    // Handle line breaks first to avoid breaking inline formatting
    // Replace double line breaks with paragraph breaks
    formattedText = formattedText.replace(/\n\n/g, '</p><p>');
    // Replace single line breaks with <br> tags
    formattedText = formattedText.replace(/\n/g, '<br>');
    
    // Bold text: **text** or __text__ (non-greedy to avoid breaking across lines)
    formattedText = formattedText.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>');
    formattedText = formattedText.replace(/__([^_]+?)__/g, '<strong>$1</strong>');
    
    // Italic text: *text* or _text_ (non-greedy)
    formattedText = formattedText.replace(/\*([^*]+?)\*/g, '<em>$1</em>');
    formattedText = formattedText.replace(/_([^_]+?)_/g, '<em>$1</em>');
    
    // Code inline: `code`
    formattedText = formattedText.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Code blocks: ```code```
    formattedText = formattedText.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    // Headers: # Header, ## Header, ### Header
    formattedText = formattedText.replace(/^### (.*$)/gm, '<h3>$1</h3>');
    formattedText = formattedText.replace(/^## (.*$)/gm, '<h2>$1</h2>');
    formattedText = formattedText.replace(/^# (.*$)/gm, '<h1>$1</h1>');
    
    // Lists: - item or * item or 1. item
    formattedText = formattedText.replace(/^[-*] (.*$)/gm, '<li>$1</li>');
    formattedText = formattedText.replace(/^\d+\. (.*$)/gm, '<li>$1</li>');
    
    // Wrap consecutive list items in <ul> tags
    formattedText = formattedText.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
    
    // Links: [text](url)
    formattedText = formattedText.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    
    // Clean up any empty paragraphs or excessive breaks
    formattedText = formattedText.replace(/<p><\/p>/g, '');
    formattedText = formattedText.replace(/<br><br>/g, '<br>');
    
    // Wrap in paragraph tags if not already wrapped
    if (!formattedText.startsWith('<')) {
      formattedText = '<p>' + formattedText + '</p>';
    }
    
    return formattedText;
  }

  static appendMessage(sender, text, className) {
    const div = document.createElement("div");
    div.className = `message ${className}`;
    
    // Format the text if it's from the AI assistant
    const formattedText = className === 'bot' ? this.formatMessage(text) : text;
    
    div.innerHTML = `<strong>${sender}</strong> ${formattedText}`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  static appendError(errorMessage) {
    this.appendMessage("AI Assistant", `Error: ${errorMessage}`, "bot");
  }
}

// Input Management
class InputManager {
  static disable() {
    input.disabled = true;
    input.style.opacity = "0.6";
  }

  static enable() {
    input.disabled = false;
    input.style.opacity = "1";
    input.focus();
  }

  static clear() {
    input.value = "";
  }

  static getValue() {
    return input.value.trim();
  }
}

// API Communication
class ChatAPI {
  static async sendMessage(message, conversationHistory) {
    try {
      const response = await fetch(API_CONFIG.url, {
        method: "POST",
        headers: API_CONFIG.headers,
        body: JSON.stringify({ 
          newest_message: message,
          conversation_history: conversationHistory
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      throw new Error(`Network error: ${error.message}`);
    }
  }
}

// Main Chat Controller
class ChatController {
  constructor() {
    this.typingIndicator = new TypingIndicator();
    this.conversationHistory = [];
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Enter key support
    input.addEventListener("keypress", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        this.handleSendMessage();
      }
    });

    // Button hover effects
    sendButton.addEventListener("mouseenter", () => {
      sendButton.style.transform = "translateY(-2px)";
    });

    sendButton.addEventListener("mouseleave", () => {
      sendButton.style.transform = "translateY(0)";
    });

    // Focus input on page load
    window.addEventListener("load", () => {
      input.focus();
    });
  }

  async handleSendMessage() {
    const userMessage = InputManager.getValue();
    if (!userMessage) return;

    // Disable input and show user message
    InputManager.disable();
    MessageManager.appendMessage("You", userMessage, "user");
    InputManager.clear();

    // Add user message to conversation history
    this.conversationHistory.push(userMessage);

    // Show typing indicator
    this.typingIndicator.show();

    try {
      const data = await ChatAPI.sendMessage(userMessage, this.conversationHistory);
      
      // Hide typing indicator
      this.typingIndicator.hide();
      
      if (data.reply) {
        MessageManager.appendMessage("AI Assistant", data.reply, "bot");
        // Add AI response to conversation history
        this.conversationHistory.push(data.reply);
      } else {
        MessageManager.appendError(data.error || "Unknown error occurred");
      }
    } catch (error) {
      this.typingIndicator.hide();
      MessageManager.appendError(error.message);
    } finally {
      InputManager.enable();
    }
  }
}

// Global function for onclick handler
function sendMessage() {
  chatController.handleSendMessage();
}

// Initialize the chat controller
const chatController = new ChatController();
