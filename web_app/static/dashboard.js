/**
 * Dashboard JavaScript
 * Handles user statistics, progress tracking, chat history, and session management
 */

// Global variables
let currentEditingCourse = null;

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
});

// Main function to load all dashboard data
async function loadDashboard() {
    try {
        await Promise.all([
            loadStatistics(),
            loadProgress(),
            loadChatHistory(),
            loadSessions()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Load user statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/user/statistics');
        const stats = await response.json();

        document.getElementById('stat-total-courses').textContent = stats.total_courses;
        document.getElementById('stat-completed-courses').textContent = stats.completed_courses;
        document.getElementById('stat-avg-progress').textContent = stats.avg_progress + '%';
        document.getElementById('stat-total-questions').textContent = stats.total_questions;

        // Animate the numbers
        animateValue('stat-total-courses', 0, stats.total_courses, 1000);
        animateValue('stat-completed-courses', 0, stats.completed_courses, 1000);
        animateValue('stat-avg-progress', 0, stats.avg_progress, 1000, '%');
        animateValue('stat-total-questions', 0, stats.total_questions, 1000);
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Load course progress
async function loadProgress() {
    const loadingEl = document.getElementById('progress-loading');
    const emptyEl = document.getElementById('progress-empty');
    const listEl = document.getElementById('progress-list');

    try {
        const response = await fetch('/api/user/progress');
        const progress = await response.json();

        loadingEl.style.display = 'none';

        if (progress.length === 0) {
            emptyEl.style.display = 'block';
            listEl.style.display = 'none';
        } else {
            emptyEl.style.display = 'none';
            listEl.style.display = 'block';
            listEl.innerHTML = progress.map(item => createProgressItem(item)).join('');
        }
    } catch (error) {
        console.error('Error loading progress:', error);
        loadingEl.innerHTML = '<p style="color: #d32f2f;">Error loading progress</p>';
    }
}

// Create progress item HTML
function createProgressItem(item) {
    const percentage = item.completion_percentage || 0;
    const lastAccessed = item.last_accessed ? formatDate(item.last_accessed) : 'Never';

    return `
        <div class="progress-item">
            <div class="progress-item-header">
                <div class="progress-item-title">
                    <h4>${escapeHtml(item.course_title)}</h4>
                    <small>${escapeHtml(item.course_id)}</small>
                </div>
                <div class="progress-item-actions">
                    <button class="icon-btn" onclick="editProgress('${escapeHtml(item.course_id)}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="icon-btn delete" onclick="deleteProgress('${escapeHtml(item.course_id)}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>

            <div class="progress-bar-container">
                <div class="progress-bar-label">
                    <span>Progress</span>
                    <strong>${percentage}%</strong>
                </div>
                <div class="progress-bar">
                    <div class="progress-bar-fill" style="width: ${percentage}%"></div>
                </div>
            </div>

            ${item.notes ? `<div class="progress-notes">${escapeHtml(item.notes)}</div>` : ''}

            <div class="progress-meta">
                <span><i class="fas fa-clock"></i>Last accessed: ${lastAccessed}</span>
            </div>
        </div>
    `;
}

// Load chat history
async function loadChatHistory() {
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
            listEl.innerHTML = history.map(item => createHistoryItem(item)).join('');
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
        loadingEl.innerHTML = '<p style="color: #d32f2f;">Error loading chat history</p>';
    }
}

// Create history item HTML
function createHistoryItem(item) {
    const time = formatDate(item.created_at);

    return `
        <div class="history-item">
            <div class="history-item-question">
                <i class="fas fa-user"></i>
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

// Load active sessions
async function loadSessions() {
    const loadingEl = document.getElementById('sessions-loading');
    const listEl = document.getElementById('sessions-list');

    try {
        const response = await fetch('/api/user/sessions');
        const sessions = await response.json();

        loadingEl.style.display = 'none';
        listEl.style.display = 'block';

        if (sessions.length === 0) {
            listEl.innerHTML = '<div class="empty-state"><p>No active sessions</p></div>';
        } else {
            listEl.innerHTML = sessions.map(session => createSessionItem(session)).join('');
        }
    } catch (error) {
        console.error('Error loading sessions:', error);
        loadingEl.innerHTML = '<p style="color: #d32f2f;">Error loading sessions</p>';
    }
}

// Create session item HTML
function createSessionItem(session) {
    const createdAt = formatDate(session.created_at);
    const expiresAt = formatDate(session.expires_at);
    const isCurrent = session.is_current;

    return `
        <div class="session-item ${isCurrent ? 'current' : ''}">
            <div class="session-info">
                <div class="session-info-header">
                    <span class="session-badge ${isCurrent ? 'current' : 'other'}">
                        ${isCurrent ? 'Current Session' : 'Other Device'}
                    </span>
                </div>
                <p><i class="fas fa-calendar"></i> Created: ${createdAt}</p>
                <small><i class="fas fa-clock"></i> Expires: ${expiresAt}</small>
            </div>
            ${!isCurrent ? `
                <button class="btn-danger" onclick="revokeSession(${session.id})">
                    <i class="fas fa-sign-out-alt"></i> Revoke
                </button>
            ` : ''}
        </div>
    `;
}

// Add course modal
function addCourse() {
    document.getElementById('add-course-modal').classList.add('show');
    document.getElementById('course-id').value = '';
    document.getElementById('course-title').value = '';
    document.getElementById('course-progress').value = '0';
    document.getElementById('course-notes').value = '';
}

function closeModal() {
    document.getElementById('add-course-modal').classList.remove('show');
}

async function saveCourse() {
    const courseId = document.getElementById('course-id').value.trim();
    const courseTitle = document.getElementById('course-title').value.trim();
    const progress = parseInt(document.getElementById('course-progress').value) || 0;
    const notes = document.getElementById('course-notes').value.trim();

    if (!courseId || !courseTitle) {
        alert('Please fill in Course ID and Title');
        return;
    }

    if (progress < 0 || progress > 100) {
        alert('Progress must be between 0 and 100');
        return;
    }

    try {
        const response = await fetch('/api/user/progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                course_id: courseId,
                course_title: courseTitle,
                completion_percentage: progress,
                notes: notes || null
            })
        });

        if (response.ok) {
            closeModal();
            await loadProgress();
            await loadStatistics();
        } else {
            const error = await response.json();
            alert('Error saving course: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error saving course:', error);
        alert('Error saving course');
    }
}

// Edit progress
async function editProgress(courseId) {
    try {
        const response = await fetch('/api/user/progress');
        const allProgress = await response.json();
        const item = allProgress.find(p => p.course_id === courseId);

        if (item) {
            currentEditingCourse = item;
            document.getElementById('edit-course-title').textContent = item.course_title;
            document.getElementById('edit-completion').value = item.completion_percentage || 0;
            document.getElementById('edit-notes').value = item.notes || '';
            document.getElementById('edit-notes-modal').classList.add('show');
        }
    } catch (error) {
        console.error('Error loading course for edit:', error);
    }
}

function closeEditModal() {
    document.getElementById('edit-notes-modal').classList.remove('show');
    currentEditingCourse = null;
}

async function saveEditedNotes() {
    if (!currentEditingCourse) return;

    const completion = parseInt(document.getElementById('edit-completion').value) || 0;
    const notes = document.getElementById('edit-notes').value.trim();

    if (completion < 0 || completion > 100) {
        alert('Progress must be between 0 and 100');
        return;
    }

    try {
        const response = await fetch('/api/user/progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                course_id: currentEditingCourse.course_id,
                course_title: currentEditingCourse.course_title,
                completion_percentage: completion,
                notes: notes || null
            })
        });

        if (response.ok) {
            closeEditModal();
            await loadProgress();
            await loadStatistics();
        } else {
            const error = await response.json();
            alert('Error updating progress: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error updating progress:', error);
        alert('Error updating progress');
    }
}

// Delete progress
async function deleteProgress(courseId) {
    if (!confirm('Are you sure you want to remove this course from your progress?')) {
        return;
    }

    try {
        const response = await fetch(`/api/user/progress/${courseId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            await loadProgress();
            await loadStatistics();
        } else {
            const error = await response.json();
            alert('Error deleting progress: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error deleting progress:', error);
        alert('Error deleting progress');
    }
}

// Clear chat history
async function clearChatHistory() {
    if (!confirm('Are you sure you want to clear all chat history? This cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch('/api/user/chat-history', {
            method: 'DELETE'
        });

        if (response.ok) {
            await loadChatHistory();
            await loadStatistics();
        } else {
            const error = await response.json();
            alert('Error clearing chat history: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error clearing chat history:', error);
        alert('Error clearing chat history');
    }
}

// Revoke session
async function revokeSession(sessionId) {
    if (!confirm('Are you sure you want to revoke this session?')) {
        return;
    }

    try {
        const response = await fetch(`/api/user/sessions/${sessionId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            await loadSessions();
        } else {
            const error = await response.json();
            alert('Error revoking session: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error revoking session:', error);
        alert('Error revoking session');
    }
}

// Logout all devices
async function logoutAllDevices() {
    if (!confirm('Are you sure you want to logout from all devices? You will be logged out from this device as well.')) {
        return;
    }

    try {
        const response = await fetch('/api/user/logout-all', {
            method: 'POST'
        });

        if (response.ok) {
            alert('Logged out from all devices. Redirecting to login...');
            window.location.href = '/login';
        } else {
            const error = await response.json();
            alert('Error logging out: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error logging out:', error);
        alert('Error logging out');
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
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
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

// Animate number counting
function animateValue(id, start, end, duration, suffix = '') {
    const element = document.getElementById(id);
    if (!element) return;

    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current) + suffix;
    }, 16);
}

// Close modals when clicking outside
window.addEventListener('click', function(event) {
    const addModal = document.getElementById('add-course-modal');
    const editModal = document.getElementById('edit-notes-modal');

    if (event.target === addModal) {
        closeModal();
    }
    if (event.target === editModal) {
        closeEditModal();
    }
});
