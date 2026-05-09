/**
 * Kerala Tourism - Chatbot Logic
 */

// 1. Toggle Chat Window
function toggleChat() {
    const chatWindow = document.getElementById('chat-window');
    if (chatWindow) {
        chatWindow.classList.toggle('hidden');
    }
}

// 2. Send Message to Flask
async function sendMessage() {
    const input = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const msg = input.value.trim();
    
    if (!msg) return;

    // Display User Message
    chatMessages.innerHTML += `
        <div class="user-msg" style="margin-bottom: 10px; text-align: right;">
            <span style="background: #e1ffc7; padding: 8px; border-radius: 10px; display: inline-block;">
                <strong>You:</strong> ${msg}
            </span>
        </div>`;
    
    input.value = ''; // Clear input field

    try {
        // Fetch from the API route in app.py
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg }) // Key "message" must match Python
        });

        if (!response.ok) throw new Error("Server error");

        const data = await response.json();
        
        // Display Assistant Response
        chatMessages.innerHTML += `
            <div class="bot-msg" style="margin-bottom: 10px; text-align: left;">
                <span style="background: #f0f0f0; padding: 8px; border-radius: 10px; display: inline-block;">
                    <strong>Assistant:</strong> ${data.reply}
                </span>
            </div>`;

    } catch (error) {
        console.error("Chat Error:", error);
        chatMessages.innerHTML += `
            <div class="bot-msg" style="color: red; text-align: left; margin-bottom: 10px;">
                ⚠️ Connection Error. Please ensure the server is running on Port 5001.
            </div>`;
    }
    
    // Auto-scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    const chatBox = document.getElementById("chat-messages");
    chatBox.scrollTop = chatBox.scrollHeight;

}
// Function for suggestion buttons
function sendSuggestion(text) {
    const input = document.getElementById('user-input');
    if (input) {
        input.value = text;
        input.focus();
        // Optional: Automatically send the message
    }
}
// 3. Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    
    // Listen for Enter Key
    if (userInput) {
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});
function toggleDescription(card) {
    if(event.target.closest('.description-content')){
        return;
    }
    // Close any other open cards first (optional)
    document.querySelectorAll('.dest-card').forEach(c => {
        if (c !== card) c.classList.remove('active');
    });
    
    // Toggle the clicked card
    card.classList.toggle('active');
}