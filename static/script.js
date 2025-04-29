document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    function addMessage(message, isUser = false) {
        const messageElement = document.createElement('p');
        messageElement.textContent = message;
        messageElement.style.textAlign = isUser ? 'right' : 'left';
        messageElement.style.backgroundColor = isUser ? '#e6f2ff' : '#f0f0f0';
        messageElement.style.padding = '10px';
        messageElement.style.borderRadius = '5px';
        messageElement.style.marginBottom = '10px';
        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            userInput.value = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ input: message }),
                });

                if (!response.ok) {
                    response.json().then(data => {
                      console.error('Error:', data.error);
                      addMessage(`Error: ${data.error}`);
                    });
                  } else {
                    const data = await response.json();
                    addMessage(data.response);
                  }


            } catch (error) {
                console.error('Error:', error);
                addMessage('Sorry, there was an error processing your request.');
            }
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
