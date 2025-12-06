/**
 * NVIDIA Competency Hub - JavaScript
 * Handles AI Learning Stream and Roadmap Interactions
 */

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
});

// Main function to load all dashboard data
async function loadDashboard() {
    try {
        // Load default role (or previously selected if we had local storage, but keeping it simple)
        await Promise.all([
            loadCompetencyHub('robotics'), // Default role
            loadLearningStream()
        ]);
        console.log('AI Competency Hub loaded successfully.');
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Handle Role Switching
async function changeRole(role) {
    // Show loading state logic if needed, but it's fast enough
    await loadCompetencyHub(role);
}

// Load Competency Data (Roadmap, Readiness, Next Move)
async function loadCompetencyHub(role) {
    try {
        const response = await fetch(`/api/competency-hub?role=${role}`);
        const data = await response.json();

        if (data.error) {
            console.error('Competency API Error:', data.error);
            return;
        }

        // 1. Update Readiness Score
        updateReadiness(data.readiness_percent);

        // 2. Update Roadmap
        renderRoadmap(data.roadmap_nodes);

        // 3. Update Next Best Move
        updateNextMove(data.next_move);
        
        // 4. Update Role Icon (Visual flair)
        updateRoleIcon(data.role_key);

    } catch (error) {
        console.error('Error loading competency data:', error);
    }
}

function updateRoleIcon(roleKey) {
    const icon = document.querySelector('.career-goal-icon i');
    if (icon) {
        if (roleKey === 'ai-engineer') {
            icon.className = 'fas fa-brain';
        } else {
            icon.className = 'fas fa-robot';
        }
    }
}

// Update Readiness UI
function updateReadiness(percent) {
    const bar = document.querySelector('.readiness-bar-fill');
    const score = document.querySelector('.readiness-score');
    
    if (bar && score) {
        // Animate width
        setTimeout(() => {
            bar.style.width = `${percent}%`;
        }, 100); 
        
        // Animate number
        animateValue(score, 0, percent, 1000, '%');
    }
}

// Render Visual Roadmap
function renderRoadmap(nodes) {
    const container = document.querySelector('.roadmap-placeholder');
    if (!container) return;

    container.innerHTML = ''; // Clear placeholder

    if (!nodes || nodes.length === 0) return;

    const totalNodes = nodes.length;
    const spacing = 85 / (totalNodes - 1); // Distribute across 85% width

    nodes.forEach((node, index) => {
        // Create Node
        const nodeDiv = document.createElement('div');
        nodeDiv.className = `roadmap-node ${node.status}`;
        nodeDiv.textContent = node.title.replace('Fundamentals', '').replace('Basics', ''); // Shorten titles
        nodeDiv.style.top = '50%';
        nodeDiv.style.left = `${10 + (index * spacing)}%`;
        nodeDiv.title = node.title;

        container.appendChild(nodeDiv);

        // Create Connecting Line
        if (index < totalNodes - 1) {
            const lineDiv = document.createElement('div');
            lineDiv.className = `roadmap-line ${node.status}`; 
            lineDiv.style.top = '50%';
            lineDiv.style.left = `${10 + (index * spacing)}%`;
            lineDiv.style.width = `${spacing}%`;
            container.appendChild(lineDiv);
        }
    });
}

// Update Next Best Move Card
function updateNextMove(nextMove) {
    const card = document.querySelector('.next-move-card');
    if (!card) return;

    if (nextMove) {
        const icon = card.querySelector('.next-move-icon i');
        const title = card.querySelector('.next-move-content h3');
        const desc = card.querySelector('.next-move-content p');
        
        if (icon) icon.className = nextMove.icon || 'fas fa-play-circle';
        if (title) title.textContent = nextMove.title;
        if (desc) desc.textContent = `Recommended step to master ${nextMove.title} based on your role targets.`;
    } else {
        // All completed state
        const contentDiv = card.querySelector('.next-move-content');
        if (contentDiv) {
             contentDiv.innerHTML = `
                <h3>All Milestones Completed!</h3>
                <p>You have mastered the core path for this role. Check the AI Stream for advanced topics.</p>
            `;
        }
    }
}

// Load AI Learning Stream (Chat History)
async function loadLearningStream() {
    const loadingEl = document.getElementById('history-loading');
    const emptyEl = document.getElementById('history-empty');
    const listEl = document.getElementById('history-list');

    try {
        const response = await fetch('/api/user/chat-history?limit=20');
        const history = await response.json();

        loadingEl.style.display = 'none';

        if (history.length === 0) {
            emptyEl.style.display = 'block';
            listEl.style.display = 'none';
        } else {
            emptyEl.style.display = 'none';
            listEl.style.display = 'block';
            listEl.innerHTML = history.map(item => createStreamItem(item)).join('');
        }
    } catch (error) {
        console.error('Error loading learning stream:', error);
        loadingEl.innerHTML = '<p style="color: #d32f2f;">Error syncing neural stream.</p>';
    }
}

// Create stream item HTML
function createStreamItem(item) {
    const time = formatDate(item.created_at);

    return `
        <div class="history-item">
            <div class="history-item-question">
                <i class="fas fa-user-astronaut"></i>
                <span>${escapeHtml(item.question)}</span>
            </div>
            <div class="history-item-answer">
                ${escapeHtml(item.answer)}
            </div>
            <div class="history-item-time">
                <i class="fas fa-clock"></i> ${time}
            </div>
        </div>
    `;
}

// Clear AI Stream
async function clearChatHistory() {
    if (!confirm('Clear your AI learning stream? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch('/api/user/chat-history', {
            method: 'DELETE'
        });

        if (response.ok) {
            await loadLearningStream();
        } else {
            const error = await response.json();
            alert('Error clearing stream: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error clearing stream:', error);
        alert('Error clearing stream');
    }
}

// Utility Functions

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';

    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hr ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Animate Value Helper
function animateValue(obj, start, end, duration, suffix='') {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start) + suffix;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}