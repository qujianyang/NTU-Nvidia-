/**
 * Simple Chat Interface for NVIDIA Course Advisor
 * KISS Principle: Just enough JavaScript to make it work
 */

// Send message when Enter is pressed
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Main function to send messages
function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();

    if (!message) return;

    // Display user message
    addMessage(message, 'user');

    // Clear input and disable while processing
    input.value = '';
    input.disabled = true;
    document.getElementById('send-btn').disabled = true;

    // Show thinking indicator
    const thinkingId = addThinkingMessage();

    // Send to backend
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: message })
    })
    .then(response => response.json())
    .then(data => {
        // Remove thinking indicator
        removeThinkingMessage(thinkingId);

        // Show bot response
        if (data.error) {
            addMessage(data.error, 'bot error');
        } else {
            addMessage(data.answer, 'bot');
        }
    })
    .catch(error => {
        removeThinkingMessage(thinkingId);
        addMessage('Sorry, I encountered a connection error. Please try again.', 'bot error');
        console.error('Error:', error);
    })
    .finally(() => {
        // Re-enable input
        input.disabled = false;
        document.getElementById('send-btn').disabled = false;
        input.focus();
    });
}

// Add message to chat
function addMessage(text, sender) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    // Add sender label
    const label = document.createElement('strong');
    label.textContent = sender === 'user' ? 'You:' : 'Advisor:';
    messageDiv.appendChild(label);

    // Add message text (handle markdown-style formatting)
    const content = document.createElement('div');
    content.innerHTML = formatMessage(text);
    messageDiv.appendChild(content);

    messagesDiv.appendChild(messageDiv);

    // Scroll to bottom
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Add thinking indicator
function addThinkingMessage() {
    const messagesDiv = document.getElementById('chat-messages');
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'message bot thinking';
    thinkingDiv.id = `thinking-${Date.now()}`;
    thinkingDiv.innerHTML = '<strong>Advisor:</strong><div class="thinking-dots"><span>.</span><span>.</span><span>.</span></div>';
    messagesDiv.appendChild(thinkingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return thinkingDiv.id;
}

// Remove thinking indicator
function removeThinkingMessage(thinkingId) {
    const thinkingDiv = document.getElementById(thinkingId);
    if (thinkingDiv) {
        thinkingDiv.remove();
    }
}

// Basic message formatting (convert line breaks and basic markdown)
function formatMessage(text) {
    // Escape HTML to prevent XSS (but preserve URLs we'll convert)
    text = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // Convert NVIDIA Learn URLs to clickable links
    text = text.replace(
        /(https:\/\/learn\.nvidia\.com\/courses\/[^\s]+)/g,
        '<a href="$1" target="_blank" class="course-link">🔗 View on NVIDIA Learn</a>'
    );

    // Convert any other URLs to clickable links
    text = text.replace(
        /(https?:\/\/[^\s]+)/g,
        function(url) {
            // Skip if already converted (has HTML tags)
            if (url.includes('</a>')) return url;
            return `<a href="${url}" target="_blank" class="external-link">${url}</a>`;
        }
    );

    // Convert line breaks
    text = text.replace(/\n/g, '<br>');

    // Convert **bold** to <strong>
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Convert `code` to <code>
    text = text.replace(/`(.*?)`/g, '<code>$1</code>');

    // Convert lists (simple version)
    text = text.replace(/^- (.+)$/gm, '• $1');

    // Special formatting for course IDs (make them stand out)
    text = text.replace(/\b(isaac-\w+-\d{3}|jetson-\d{3}|cosmos-\d{3})\b/g, '<span class="course-id">$1</span>');

    return text;
}

// Save user preferences
function savePreferences() {
    const level = document.getElementById('user-level').value;

    fetch('/api/preferences', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            level: level
        })
    })
    .then(response => response.json())
    .then(data => {
        // Show brief confirmation
        const btn = document.querySelector('.save-btn');
        const originalText = btn.textContent;
        btn.textContent = '✓ Saved!';
        btn.classList.add('saved');

        setTimeout(() => {
            btn.textContent = originalText;
            btn.classList.remove('saved');
        }, 2000);
    })
    .catch(error => {
        console.error('Error saving preferences:', error);
    });
}