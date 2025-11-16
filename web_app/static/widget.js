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

// Export chat to PDF using jsPDF (client-side)
window.exportChatPDF = function() {
    try {
        const messages = document.querySelectorAll('#chat-messages .message');

        if (messages.length === 0) {
            alert('No chat messages to export yet. Start a conversation first!');
            return;
        }

        // Check if jsPDF is loaded
        if (typeof window.jspdf === 'undefined') {
            alert('PDF library not loaded. Please refresh the page and try again.');
            return;
        }

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        // Set up the document
        const pageWidth = doc.internal.pageSize.width;
        const margin = 15;
        const maxLineWidth = pageWidth - (margin * 2);
        let yPosition = 20;

        // Title
        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.text('NvidiAdvisor Chat Transcript', pageWidth / 2, yPosition, { align: 'center' });
        yPosition += 10;

        // Timestamp
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(128, 128, 128);
        const timestamp = new Date().toLocaleString();
        doc.text(`Exported on ${timestamp}`, pageWidth / 2, yPosition, { align: 'center' });
        yPosition += 15;
        doc.setTextColor(0, 0, 0);

        // Extract and add messages
        messages.forEach(msgEl => {
            const isUser = msgEl.classList.contains('user-message');
            const sender = isUser ? 'You' : 'NvidiAdvisor';

            // Get text content
            const textEl = msgEl.querySelector('.message-text') || msgEl;
            let text = textEl.innerText || textEl.textContent || '';
            text = text.trim();

            if (!text) return;

            // Check if we need a new page
            if (yPosition > 270) {
                doc.addPage();
                yPosition = 20;
            }

            // Sender name (bold)
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text(sender, margin, yPosition);
            yPosition += 6;

            // Message text (wrapped)
            doc.setFontSize(10);
            doc.setFont('helvetica', 'normal');
            const lines = doc.splitTextToSize(text, maxLineWidth);

            lines.forEach(line => {
                if (yPosition > 270) {
                    doc.addPage();
                    yPosition = 20;
                }
                doc.text(line, margin, yPosition);
                yPosition += 5;
            });

            yPosition += 5; // Space between messages
        });

        // Save the PDF
        const filename = `nvidiAdvisor-chat-${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.pdf`;
        doc.save(filename);

    } catch (error) {
        console.error('Export error:', error);
        alert('Failed to export chat. Please try again.');
    }
};

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
