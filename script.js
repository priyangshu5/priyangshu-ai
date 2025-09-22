class PriyangshuAIClient {
    constructor() {
        this.apiBaseUrl = window.location.hostname === 'localhost' ? 
            'http://localhost:5000' : 
            'https://your-backend-url.herokuapp.com'; // Replace with your actual backend URL
        
        this.chatHistory = [];
        this.isImageMode = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadChatHistory();
    }

    bindEvents() {
        // Send message on button click
        document.getElementById('sendButton').addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter key (with Shift for new line)
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Clear chat
        document.getElementById('clearChat').addEventListener('click', () => this.clearChat());
        
        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => this.toggleTheme());
        
        // Mode buttons
        document.getElementById('textMode').addEventListener('click', () => this.setMode('text'));
        document.getElementById('imageMode').addEventListener('click', () => this.setMode('image'));
    }

    setMode(mode) {
        this.isImageMode = mode === 'image';
        
        // Update button states
        document.getElementById('textMode').classList.toggle('active', mode === 'text');
        document.getElementById('imageMode').classList.toggle('active', mode === 'image');
        
        // Update placeholder
        const input = document.getElementById('messageInput');
        input.placeholder = this.isImageMode ? 
            "Describe the image you want to generate..." : 
            "Type your message here... (For images, start with 'generate image' or 'create image')";
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        input.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            let response;
            if (this.isImageMode || message.toLowerCase().startsWith('generate image') || message.toLowerCase().startsWith('create image')) {
                // Extract prompt for image generation
                let prompt = message;
                if (message.toLowerCase().startsWith('generate image')) {
                    prompt = message.substring('generate image'.length).trim();
                } else if (message.toLowerCase().startsWith('create image')) {
                    prompt = message.substring('create image'.length).trim();
                }
                response = await this.generateImage(prompt);
            } else {
                response = await this.chat(message);
            }
            
            this.removeTypingIndicator();
            this.addMessage(response, 'bot');
            
        } catch (error) {
            this.removeTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            console.error('Error:', error);
        }
        
        this.saveChatHistory();
    }

    async chat(message) {
        const response = await fetch(`${this.apiBaseUrl}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        return data.response;
    }

    async generateImage(prompt) {
        const response = await fetch(`${this.apiBaseUrl}/api/generate-image`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        return data.response;
    }

    addMessage(content, sender) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (sender === 'bot' && content.includes('http')) {
            // If it's an image URL, create an image element
            const urlMatch = content.match(/https?:\/\/[^\s]+/);
            if (urlMatch) {
                const imageUrl = urlMatch[0];
                const img = document.createElement('img');
                img.src = imageUrl;
                img.style.maxWidth = '100%';
                img.style.borderRadius = '10px';
                img.style.marginTop = '10px';
                messageContent.innerHTML = content.replace(urlMatch[0], '');
                messageContent.appendChild(img);
            } else {
                messageContent.innerHTML = content;
            }
        } else {
            messageContent.innerHTML = sender === 'bot' ? `<strong>Priyangshu AI:</strong> ${content}` : content;
        }
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Save to history
        this.chatHistory.push({ sender, content, timestamp: new Date().toISOString() });
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.className = 'message bot-message';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'typing-indicator';
        typingContent.innerHTML = `
            <strong>Priyangshu AI:</strong> 
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        typingDiv.appendChild(typingContent);
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = `
            <div class="message bot-message">
                <div class="message-content">
                    <strong>Priyangshu AI:</strong> Hello! I'm Priyangshu AI, your advanced AI assistant. I can help you with text conversations and generate images. How can I assist you today?
                </div>
            </div>
        `;
        this.chatHistory = [];
        localStorage.removeItem('priyangshuAI_chatHistory');
    }

    saveChatHistory() {
        localStorage.setItem('priyangshuAI_chatHistory', JSON.stringify(this.chatHistory));
    }

    loadChatHistory() {
        const saved = localStorage.getItem('priyangshuAI_chatHistory');
        if (saved) {
            this.chatHistory = JSON.parse(saved);
            // Replay chat history (optional - you might want to limit this)
            this.chatHistory.forEach(msg => {
                this.addMessage(msg.content, msg.sender);
            });
        }
    }

    toggleTheme() {
        document.body.classList.toggle('dark-mode');
        const themeBtn = document.getElementById('themeToggle');
        themeBtn.textContent = document.body.classList.contains('dark-mode') ? '☀️ Light Mode' : '🌙 Dark Mode';
    }
}

// Initialize the AI client when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new PriyangshuAIClient();
});