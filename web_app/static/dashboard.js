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
        
        // 4. Update Role Icon
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
        setTimeout(() => {
            bar.style.width = `${percent}%`;
        }, 100);
        score.textContent = `${percent}%`;
    }
}

// Render Visual Roadmap
function renderRoadmap(nodes) {
    const container = document.querySelector('.roadmap-placeholder');
    if (!container) return;

    container.innerHTML = ''; // Clear placeholder

    if (!nodes || nodes.length === 0) return;

    const totalNodes = nodes.length;
    const spacing = 85 / (totalNodes - 1); 

    nodes.forEach((node, index) => {
        // Create Node Container
        const nodeDiv = document.createElement('div');
        nodeDiv.className = `roadmap-node ${node.status}`;
        nodeDiv.style.top = '50%';
        nodeDiv.style.left = `${10 + (index * spacing)}%`;
        nodeDiv.title = node.description || node.title; // Use description for tooltip

        // Icon
        const icon = document.createElement('i');
        icon.className = node.icon;
        nodeDiv.appendChild(icon);

        // Label
        const label = document.createElement('span');
        label.className = 'node-label';
        label.textContent = node.title;
        nodeDiv.appendChild(label);

        // Progress Ring (if active)
        if (node.status === 'active' && node.progress) {
            const badge = document.createElement('div');
            badge.className = 'node-progress-badge';
            badge.textContent = `${node.progress}%`;
            nodeDiv.appendChild(badge);
        }

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
        card.innerHTML = `
            <div class="next-move-icon">
                <i class="${nextMove.icon || 'fas fa-play-circle'}"></i>
            </div>
            <div class="next-move-content">
                <h3>${nextMove.title}</h3>
                <p>${nextMove.description}</p>
                ${nextMove.courses_text ? `<div class="next-move-detail"><i class="fas fa-list-ul"></i> ${nextMove.courses_text}</div>` : ''}
                <div class="next-move-meta">
                    <span><i class="fas fa-clock"></i> 4 Hours</span>
                    <span><i class="fas fa-signal"></i> ${nextMove.status === 'active' ? 'In Progress' : 'Start Now'}</span>
                </div>
                <a href="${nextMove.url || '#'}" target="_blank" class="btn-primary btn-large">
                    Continue Learning <i class="fas fa-arrow-right"></i>
                </a>
            </div>
        `;
    } else {
        card.innerHTML = `
            <div class="next-move-icon" style="background: rgba(118, 185, 0, 0.2); color: #76b900;">
                <i class="fas fa-trophy"></i>
            </div>
            <div class="next-move-content">
                <h3>All Milestones Completed!</h3>
                <p>You have mastered the core path for this role. Check the AI Stream for advanced topics.</p>
            </div>
        `;
    }
}

// Load AI Learning Stream
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

async function clearChatHistory() {
    if (!confirm('Clear your AI learning stream? This action cannot be undone.')) {
        return;
    }
    try {
        const response = await fetch('/api/user/chat-history', { method: 'DELETE' });
        if (response.ok) {
            await loadLearningStream();
        } else {
            alert('Error clearing stream');
        }
    } catch (error) {
        alert('Error clearing stream');
    }
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}