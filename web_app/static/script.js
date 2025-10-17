/**
 * Enhanced Chat Interface for NVIDIA Course Advisor
 * Phase 1: Professional UI with character counter and thought process
 */

// Character Counter
const userInput = document.getElementById('user-input');
const charCounter = document.getElementById('char-counter');

userInput.addEventListener('input', function() {
    const length = this.value.length;
    charCounter.textContent = `${length}/500`;

    // Warn when approaching limit
    if (length > 450) {
        charCounter.classList.add('warning');
    } else {
        charCounter.classList.remove('warning');
    }
});

// Send message when Enter is pressed
userInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Thought process messages
const thoughtMessages = [
    "Searching course catalog...",
    "Analyzing prerequisites...",
    "Matching your level...",
    "Preparing recommendations..."
];

let thoughtInterval = null;

// Main function to send messages
function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();

    if (!message) return;

    // Display user message
    addMessage(message, 'user');

    // Clear input and disable while processing
    input.value = '';
    charCounter.textContent = '0/500';  // Reset character counter
    charCounter.classList.remove('warning');
    input.disabled = true;
    document.getElementById('send-btn').disabled = true;

    // Show enhanced thought process
    startThoughtProcess();

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
        // Stop thought process
        stopThoughtProcess();

        // Show bot response
        if (data.error) {
            addMessage(data.error, 'bot error');
        } else {
            addMessage(data.answer, 'bot');
        }
    })
    .catch(error => {
        stopThoughtProcess();
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

    // Add sender label with icon
    const label = document.createElement('strong');
    if (sender === 'user') {
        label.innerHTML = '<i class="fas fa-user"></i> You:';
    } else if (sender.includes('error')) {
        label.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error:';
    } else {
        label.innerHTML = '<i class="fas fa-robot"></i> NvidiAdvisor:';
    }
    messageDiv.appendChild(label);

    // Add message text (handle markdown-style formatting)
    const content = document.createElement('div');
    content.innerHTML = formatMessage(text);
    messageDiv.appendChild(content);

    messagesDiv.appendChild(messageDiv);

    // Scroll to bottom
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Enhanced Thought Process Indicator
function startThoughtProcess() {
    const thoughtContainer = document.getElementById('thought-process-container');
    const thoughtText = document.getElementById('thought-process-text');
    const dots = [
        document.getElementById('dot-1'),
        document.getElementById('dot-2'),
        document.getElementById('dot-3'),
        document.getElementById('dot-4')
    ];

    // Show the container
    thoughtContainer.style.display = 'block';

    // Start cycling through messages and dots
    let messageIndex = 0;
    let dotIndex = 0;

    // Update first message immediately
    thoughtText.textContent = thoughtMessages[0];
    dots[0].classList.add('active');

    thoughtInterval = setInterval(() => {
        // Update message
        messageIndex = (messageIndex + 1) % thoughtMessages.length;
        thoughtText.textContent = thoughtMessages[messageIndex];

        // Update dots
        dots.forEach(dot => dot.classList.remove('active'));
        dotIndex = (dotIndex + 1) % dots.length;
        dots[dotIndex].classList.add('active');
    }, 2000);
}

function stopThoughtProcess() {
    const thoughtContainer = document.getElementById('thought-process-container');
    const dots = [
        document.getElementById('dot-1'),
        document.getElementById('dot-2'),
        document.getElementById('dot-3'),
        document.getElementById('dot-4')
    ];

    // Clear interval
    if (thoughtInterval) {
        clearInterval(thoughtInterval);
        thoughtInterval = null;
    }

    // Hide container
    thoughtContainer.style.display = 'none';

    // Reset dots
    dots.forEach(dot => dot.classList.remove('active'));
}

// Basic message formatting (convert line breaks and basic markdown)
function formatMessage(text) {
    // KISS APPROACH: Simple and working

    // 1. First escape HTML to prevent XSS
    text = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // 2. Handle markdown links: [text](url) -> clickable link with text
    text = text.replace(
        /\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g,
        '<a href="$2" target="_blank" class="course-link">$1</a>'
    );

    // 3. Convert any remaining plain URLs to clickable links
    // Only match URLs that aren't already in anchor tags
    text = text.replace(
        /(^|[^">])(https?:\/\/[^\s<]+)/g,
        function(match, prefix, url) {
            // Clean any trailing punctuation from URL
            url = url.replace(/[.,;:!?\)]$/, '');
            if (url.includes('learn.nvidia.com')) {
                return prefix + '<a href="' + url + '" target="_blank" class="course-link">🔗 View on NVIDIA Learn</a>';
            }
            return prefix + '<a href="' + url + '" target="_blank" class="external-link">' + url + '</a>';
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
    text = text.replace(/\b(isaac-\w+-\d{3}|jetson-\d{3}|cosmos-\d{3}|robotics-\w+-\d{3})\b/g, '<span class="course-id">$1</span>');

    return text;
}