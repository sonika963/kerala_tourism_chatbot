/**
 * Kerala Tourism - Frontend Logic
 * * Note: fetchDestinations() was removed because we are now 
 * using Python/Jinja2 to render cards directly from the database.
 */

// 1. CHATBOT VISIBILITY TOGGLE
function toggleChat() {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.classList.toggle('hidden');
}

// 2. CHATBOT COMMUNICATION
async function sendMessage() {
    const input = document.getElementById('user-input');
    const msg = input.value.trim();
    
    // Don't send empty messages
    if (!msg) return;

    const chatMessages = document.getElementById('chat-messages');
    
    // Append User Message to UI
    chatMessages.innerHTML += `
        <div class="user-msg">
            <span class="sender">You:</span> ${msg}
        </div>`;
    
    // Clear input immediately for better UX
    input.value = '';

    try {
        // Send message to Flask API
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });

        if (!res.ok) throw new Error("Server error");

        const data = await res.json();
        
        // Append Bot Response to UI
        chatMessages.innerHTML += `
            <div class="bot-msg">
                <span class="sender">Assistant:</span> ${data.reply}
            </div>`;

    } catch (error) {
        console.error("Chat Error:", error);
        chatMessages.innerHTML += `<div class="bot-msg" style="color: red;">Sorry, I'm having trouble connecting right now.</div>`;
    }
    
    // Auto-scroll to the bottom of the chat
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 3. EVENT LISTENERS
document.addEventListener('DOMContentLoaded', () => {
    // Listen for "Enter" key in the chat input box
    const userInput = document.getElementById('user-input');
    if (userInput) {
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    console.log(">>> JS Loaded: Chatbot ready. Destination cards handled by Python.");
});

// 4. OPTIONAL: SHOW DETAILS FUNCTION
// This can be triggered if you added onclick="showDetails('{{ name }}')" in your HTML
function showDetails(placeName) {
    alert("You clicked on: " + placeName + "\nMore details coming soon!");
}