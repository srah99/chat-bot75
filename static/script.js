document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    // Initialize conversation history
    let conversationHistory = [];
    
    // Load conversation history from localStorage if available
    try {
        const savedHistory = localStorage.getItem('chatHistory');
        if (savedHistory) {
            conversationHistory = JSON.parse(savedHistory);
            // Display previous messages
            conversationHistory.forEach(item => {
                addMessage(item.message, item.isUser);
            });
        }
    } catch (e) {
        console.error('Error loading chat history:', e);
    }
    
    function saveHistory() {
        try {
            localStorage.setItem('chatHistory', JSON.stringify(conversationHistory));
        } catch (e) {
            console.error('Error saving chat history:', e);
        }
    }
    
    function addMessage(message, isUser = false) {
        const messageElement = document.createElement('div');
        messageElement.className = isUser ? 'user-message' : 'bot-message';
        
        const textElement = document.createElement('p');
        textElement.textContent = message;
        messageElement.appendChild(textElement);
        
        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Add to history
        if (conversationHistory.length >= 50) {
            // Limit history to last 50 messages
            conversationHistory.shift();
        }
        conversationHistory.push({ message, isUser });
        saveHistory();
    }
    
    function setLoading(isLoading) {
        if (loadingIndicator) {
            loadingIndicator.style.display = isLoading ? 'block' : 'none';
        }
        sendButton.disabled = isLoading;
        userInput.disabled = isLoading;
    }
    
    function clearInput() {
        userInput.value = '';
    }
    
    function clearHistory() {
        chatContainer.innerHTML = '';
        conversationHistory = [];
        saveHistory();
    }
    
    // Add clear history button functionality
    const clearButton = document.getElementById('clear-button');
    if (clearButton) {
        clearButton.addEventListener('click', clearHistory);
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        addMessage(message, true);
        clearInput();
        setLoading(true);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: message }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error:', errorData.error);
                addMessage(`Error: ${errorData.error || 'Unknown error occurred'}`);
            } else {
                const data = await response.json();
                addMessage(data.response);
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, there was an error connecting to the server. Please try again later.');
        } finally {
            setLoading(false);
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Focus input field on page load
    userInput.focus();
});
