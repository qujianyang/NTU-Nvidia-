/**
 * Floating Chat Widget Controller
 * Handles widget open/close animations and state
 */

// Widget state
let isWidgetOpen = false;

// Toggle widget visibility
function toggleChatWidget() {
    if (isWidgetOpen) {
        closeChatWidget();
    } else {
        openChatWidget();
    }
}

// Open the chat widget
function openChatWidget() {
    const widget = document.getElementById('chat-widget-container');
    const toggleBtn = document.getElementById('chat-widget-toggle');
    const badge = document.getElementById('widget-badge');

    // Show widget with animation
    widget.style.display = 'flex';

    // Hide toggle button (optional - or you can keep it visible)
    // toggleBtn.style.transform = 'scale(0)';

    // Hide notification badge
    if (badge) {
        badge.style.display = 'none';
    }

    // Focus on input
    setTimeout(() => {
        const input = document.getElementById('user-input');
        if (input) {
            input.focus();
        }
    }, 300);

    isWidgetOpen = true;
}

// Close the chat widget
function closeChatWidget() {
    const widget = document.getElementById('chat-widget-container');
    const toggleBtn = document.getElementById('chat-widget-toggle');

    // Add fade out animation
    widget.style.animation = 'slideDown 0.3s ease-out';

    setTimeout(() => {
        widget.style.display = 'none';
        widget.style.animation = 'slideUp 0.3s ease-out';
    }, 250);

    // Show toggle button again
    // toggleBtn.style.transform = 'scale(1)';

    isWidgetOpen = false;
}

// Close widget when clicking outside (optional)
document.addEventListener('click', function(event) {
    const widget = document.getElementById('chat-widget-container');
    const toggleBtn = document.getElementById('chat-widget-toggle');

    if (isWidgetOpen &&
        !widget.contains(event.target) &&
        !toggleBtn.contains(event.target)) {
        // Uncomment to enable click-outside-to-close
        // closeChatWidget();
    }
});

// Close widget with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && isWidgetOpen) {
        closeChatWidget();
    }
});

// Add slide down animation keyframe
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
        to {
            opacity: 0;
            transform: translateY(20px) scale(0.95);
        }
    }
`;
document.head.appendChild(style);

// Resize functionality
document.addEventListener('DOMContentLoaded', function() {
    const widget = document.getElementById('chat-widget-container');
    const handle = document.getElementById('widget-resize-handle');

    if (widget) {
        widget.style.display = 'none';
    }

    if (handle && widget) {
        let isResizing = false;
        let startX, startY, startWidth, startHeight;

        handle.addEventListener('mousedown', function(e) {
            isResizing = true;
            startX = e.clientX;
            startY = e.clientY;
            startWidth = widget.offsetWidth;
            startHeight = widget.offsetHeight;
            e.preventDefault();
        });

        document.addEventListener('mousemove', function(e) {
            if (!isResizing) return;

            const width = startWidth + (startX - e.clientX);
            const height = startHeight + (startY - e.clientY);

            widget.style.width = Math.max(350, Math.min(800, width)) + 'px';
            widget.style.height = Math.max(400, Math.min(900, height)) + 'px';
        });

        document.addEventListener('mouseup', function() {
            isResizing = false;
        });
    }
});
