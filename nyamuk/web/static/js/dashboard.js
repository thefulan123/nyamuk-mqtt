/**
 * Nyamuk MQTT Manager - Dashboard JavaScript
 */

// Socket.IO connection
const socket = io();

// Connection status
socket.on('connect', function() {
    console.log('Connected to Nyamuk server');
    updateConnectionStatus(true);
    socket.emit('request_status');
});

socket.on('disconnect', function() {
    console.log('Disconnected from server');
    updateConnectionStatus(false);
});

// Status updates
socket.on('status_update', function(data) {
    updateDashboard(data);
});

// Real-time messages
socket.on('message_received', function(data) {
    addMessageToLog(data);
});

// Connection status indicator
function updateConnectionStatus(connected) {
    const indicator = document.getElementById('connection-status');
    if (indicator) {
        indicator.textContent = connected ? '🟢 Connected' : '🔴 Disconnected';
        indicator.className = connected ? 'status-connected' : 'status-disconnected';
    }
}

// Update dashboard with broker status
function updateDashboard(data) {
    const status = data.status;
    const stats = data.stats;

    // Update status
    const statusEl = document.getElementById('broker-status');
    if (statusEl) {
        statusEl.textContent = status.status === 'running' ? '✅ Running' : '❌ Stopped';
        statusEl.className = status.status === 'running' ? 'stat-value success' : 'stat-value error';
    }

    // Update uptime
    const uptimeEl = document.getElementById('broker-uptime');
    if (uptimeEl) {
        uptimeEl.textContent = status.started_at ? formatUptime(status.started_at) : 'N/A';
    }

    // Update CPU
    const cpuEl = document.getElementById('cpu-usage');
    if (cpuEl) {
        cpuEl.textContent = stats.cpu_percent ? `${stats.cpu_percent}%` : 'N/A';
    }

    // Update Memory
    const memEl = document.getElementById('memory-usage');
    if (memEl) {
        memEl.textContent = stats.memory_percent ? `${stats.memory_percent}%` : 'N/A';
    }
}

// Format uptime from ISO timestamp
function formatUptime(startedAt) {
    const start = new Date(startedAt);
    const now = new Date();
    const diff = Math.floor((now - start) / 1000);

    const days = Math.floor(diff / 86400);
    const hours = Math.floor((diff % 86400) / 3600);
    const minutes = Math.floor((diff % 3600) / 60);

    if (days > 0) {
        return `${days}d ${hours}h ${minutes}m`;
    } else if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else {
        return `${minutes}m`;
    }
}

// Add message to log
function addMessageToLog(data) {
    const log = document.getElementById('messages-log');
    if (!log) return;

    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `
        <span class="log-time">${new Date().toLocaleTimeString()}</span>
        <span class="log-topic">${escapeHtml(data.topic)}</span>
        <span class="log-payload">${escapeHtml(data.payload)}</span>
    `;

    log.insertBefore(entry, log.firstChild);

    // Keep only last 50 messages
    while (log.children.length > 50) {
        log.removeChild(log.lastChild);
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// API helpers
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function postAPI(endpoint, data) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Export functions for use in other scripts
window.NyamukAPI = {
    fetchAPI,
    postAPI,
    socket,
};
