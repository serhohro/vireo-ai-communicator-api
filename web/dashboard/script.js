/**
 * Vireo Dashboard - Main Application Script
 * Complete dashboard functionality for Vireo AI platform
 * 
 * @version 3.0.0
 * @author Serhii (serhohro)
 */

// ============================================================
// Application State
// ============================================================
const AppState = {
    // Connection
    connected: false,
    connecting: false,
    ws: null,
    reconnectAttempts: 0,
    maxReconnectAttempts: 10,
    reconnectDelay: 1000,
    
    // Data
    agents: [],
    messages: [],
    contracts: [],
    activities: [],
    networkNodes: [],
    networkEdges: [],
    
    // Stats
    stats: {
        agentCount: 0,
        messageCount: 0,
        contractCount: 0,
        activeContracts: 0,
        pendingContracts: 0,
        completedContracts: 0,
        connections: 0,
        memory: 0,
        uptime: 0,
        cpu: 0,
    },
    
    // UI State
    currentSection: 'overview',
    selectedAgent: null,
    selectedContract: null,
    chartPeriod: '1h',
    isLoading: false,
    darkMode: false,
    
    // Settings
    settings: {
        apiUrl: localStorage.getItem('vireo_api_url') || 'http://localhost:8000/api/v1',
        wsUrl: localStorage.getItem('vireo_ws_url') || 'ws://localhost:8000/ws',
        apiKey: localStorage.getItem('vireo_api_key') || '',
        theme: localStorage.getItem('vireo_theme') || 'auto',
        autoRefresh: localStorage.getItem('vireo_auto_refresh') !== 'false',
        soundAlerts: localStorage.getItem('vireo_sound_alerts') === 'true',
        notifications: localStorage.getItem('vireo_notifications') !== 'false',
    },
    
    // Timers
    refreshInterval: null,
    uptimeInterval: null,
    startTime: Date.now(),
    
    // Chart instances
    charts: {
        activity: null,
        status: null,
        network: null,
    },
    
    // Event handlers
    eventHandlers: {},
};

// ============================================================
// API Client
// ============================================================
class VireoAPI {
    constructor() {
        this.baseUrl = AppState.settings.apiUrl;
        this.apiKey = AppState.settings.apiKey;
        this.timeout = 30000;
    }
    
    get headers() {
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Vireo-Dashboard/3.0.0',
        };
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }
        return headers;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        try {
            const response = await fetch(url, {
                ...options,
                headers: { ...this.headers, ...options.headers },
                signal: controller.signal,
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json();
                } catch {
                    errorData = { error: response.statusText };
                }
                throw new Error(errorData.error || errorData.message || `HTTP ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            }
            return response;
            
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }
    
    // ============================================================
    // Agent Endpoints
    // ============================================================
    
    async getAgents(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/agents${query ? '?' + query : ''}`);
    }
    
    async getAgent(agentId) {
        return this.request(`/agents/${agentId}`);
    }
    
    async createAgent(data) {
        return this.request('/agents', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
    
    async updateAgent(agentId, data) {
        return this.request(`/agents/${agentId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }
    
    async deleteAgent(agentId) {
        return this.request(`/agents/${agentId}`, {
            method: 'DELETE',
        });
    }
    
    // ============================================================
    // Message Endpoints
    // ============================================================
    
    async sendMessage(data) {
        return this.request('/messages', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
    
    async getMessages(agentId, params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/agents/${agentId}/messages${query ? '?' + query : ''}`);
    }
    
    async getMessage(messageId) {
        return this.request(`/messages/${messageId}`);
    }
    
    // ============================================================
    // Contract Endpoints
    // ============================================================
    
    async createContract(data) {
        return this.request('/contracts', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
    
    async getContracts() {
        return this.request('/contracts');
    }
    
    async getContract(contractId) {
        return this.request(`/contracts/${contractId}`);
    }
    
    async signContract(contractId) {
        return this.request(`/contracts/${contractId}/sign`, {
            method: 'POST',
        });
    }
    
    // ============================================================
    // Negotiation Endpoints
    // ============================================================
    
    async startNegotiation(data) {
        return this.request('/negotiations', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
    
    async submitOffer(negotiationId, offer) {
        return this.request(`/negotiations/${negotiationId}/offer`, {
            method: 'POST',
            body: JSON.stringify(offer),
        });
    }
    
    // ============================================================
    // Trust & Discovery
    // ============================================================
    
    async getTrust(agentId) {
        return this.request(`/trust/${agentId}`);
    }
    
    async discover(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/discover${query ? '?' + query : ''}`);
    }
    
    // ============================================================
    // System Endpoints
    // ============================================================
    
    async getStatus() {
        return this.request('/system/status');
    }
    
    async getHealth() {
        return this.request('/system/health');
    }
}

// ============================================================
// WebSocket Client
// ============================================================
class VireoWS {
    constructor() {
        this.ws = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxAttempts = 10;
        this.delay = 1000;
        this.handlers = {};
        this.pingInterval = null;
        this.messageQueue = [];
        this.reconnecting = false;
    }
    
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return;
        }
        
        if (this.reconnecting) {
            return;
        }
        
        this.connected = false;
        updateConnectionStatus('connecting');
        
        const url = AppState.settings.wsUrl;
        const params = new URLSearchParams();
        if (AppState.settings.apiKey) {
            params.append('api_key', AppState.settings.apiKey);
        }
        
        const fullUrl = `${url}?${params.toString()}`;
        
        try {
            this.ws = new WebSocket(fullUrl);
            
            this.ws.onopen = () => {
                this.connected = true;
                this.reconnectAttempts = 0;
                this.delay = 1000;
                this.reconnecting = false;
                AppState.connected = true;
                updateConnectionStatus('connected');
                this.startPing();
                this.emit('connected');
                this.flushQueue();
                showToast('Connected to Vireo server', 'success');
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };
            
            this.ws.onclose = () => {
                this.connected = false;
                AppState.connected = false;
                this.stopPing();
                updateConnectionStatus('disconnected');
                this.emit('disconnected');
                this.reconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.emit('error', error);
                // Don't close here, let onclose handle it
            };
            
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.reconnect();
        }
    }
    
    reconnect() {
        if (this.reconnecting) return;
        this.reconnecting = true;
        
        if (this.reconnectAttempts >= this.maxAttempts) {
            showToast('Maximum reconnect attempts reached', 'error');
            this.reconnecting = false;
            return;
        }
        
        this.reconnectAttempts++;
        this.delay = Math.min(this.delay * 2, 30000);
        
        setTimeout(() => {
            this.reconnecting = false;
            if (!this.connected) {
                this.connect();
            }
        }, this.delay);
    }
    
    disconnect() {
        this.stopPing();
        if (this.ws) {
            try {
                this.ws.close(1000, 'User disconnected');
            } catch (e) {}
            this.ws = null;
        }
        this.connected = false;
        AppState.connected = false;
        this.reconnecting = false;
        updateConnectionStatus('disconnected');
        this.emit('disconnected');
    }
    
    startPing() {
        this.stopPing();
        this.pingInterval = setInterval(() => {
            if (this.connected && this.ws?.readyState === WebSocket.OPEN) {
                this.send({
                    type: 'heartbeat',
                    payload: { timestamp: Date.now() }
                });
            }
        }, 30000);
    }
    
    stopPing() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }
    
    send(data) {
        if (this.connected && this.ws?.readyState === WebSocket.OPEN) {
            try {
                this.ws.send(JSON.stringify(data));
                return true;
            } catch (error) {
                console.error('Failed to send WebSocket message:', error);
                this.messageQueue.push(data);
                return false;
            }
        } else {
            this.messageQueue.push(data);
            return false;
        }
    }
    
    flushQueue() {
        while (this.messageQueue.length > 0) {
            const data = this.messageQueue.shift();
            this.send(data);
        }
    }
    
    handleMessage(data) {
        this.emit('message', data);
        
        switch (data.type) {
            case 'welcome':
                showToast(`Connected as ${data.payload.agent_id || 'agent'}`, 'info');
                this.emit('welcome', data.payload);
                break;
            
            case 'heartbeat_ack':
                this.emit('heartbeat', data.payload);
                break;
            
            case 'message':
                this.emit('message_received', data.payload);
                addActivity('message', `${data.payload.sender || 'unknown'} sent a message`, data.payload);
                AppState.stats.messageCount++;
                updateStats();
                break;
            
            case 'publish':
                this.emit('publish', data.payload);
                addActivity('publish', `Published to room: ${data.payload.room}`, data.payload);
                break;
            
            case 'agent_status':
                this.emit('agent_status', data.payload);
                AppState.stats.agentCount = data.payload.count || AppState.stats.agentCount;
                updateStats();
                break;
            
            case 'contract_update':
                this.emit('contract_update', data.payload);
                addActivity('contract', `Contract ${data.payload.contract_id} updated: ${data.payload.status}`, data.payload);
                if (data.payload.status === 'active') {
                    AppState.stats.activeContracts++;
                }
                updateStats();
                break;
            
            case 'error':
                showToast(`Error: ${data.payload.error}`, 'error');
                this.emit('error', data.payload);
                break;
            
            default:
                // Unknown message type
                this.emit('unknown', data);
                break;
        }
    }
    
    // Event handling
    on(event, handler) {
        if (!this.handlers[event]) {
            this.handlers[event] = [];
        }
        this.handlers[event].push(handler);
    }
    
    off(event, handler) {
        if (this.handlers[event]) {
            this.handlers[event] = this.handlers[event].filter(h => h !== handler);
        }
    }
    
    emit(event, data) {
        if (this.handlers[event]) {
            this.handlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Handler error for ${event}:`, error);
                }
            });
        }
    }
}

// ============================================================
// UI Helpers
// ============================================================

function updateConnectionStatus(state) {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    const btn = document.getElementById('connectBtn');
    
    if (!dot || !text || !btn) return;
    
    dot.className = 'status-dot';
    switch (state) {
        case 'connected':
            dot.classList.add('connected');
            text.textContent = 'Connected';
            btn.textContent = 'Disconnect';
            btn.className = 'btn-connect';
            btn.style.background = '#fc8181';
            btn.style.color = 'white';
            btn.disabled = false;
            break;
        case 'connecting':
            dot.classList.add('connecting');
            text.textContent = 'Connecting...';
            btn.textContent = '⏳';
            btn.className = 'btn-connect';
            btn.style.background = '';
            btn.disabled = true;
            break;
        case 'disconnected':
        default:
            dot.classList.add('disconnected');
            text.textContent = 'Disconnected';
            btn.textContent = 'Connect';
            btn.className = 'btn-connect';
            btn.style.background = '';
            btn.style.color = '';
            btn.disabled = false;
            break;
    }
}

function showToast(message, type = 'info', title = '') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️',
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
        <div class="toast-content">
            ${title ? `<div class="toast-title">${escapeHtml(title)}</div>` : ''}
            <div class="toast-message">${escapeHtml(message)}</div>
        </div>
        <button class="toast-close">&times;</button>
    `;
    
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.remove();
    });
    
    container.appendChild(toast);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(20px)';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
    
    // Sound alerts
    if (AppState.settings.soundAlerts) {
        playNotificationSound(type);
    }
}

function playNotificationSound(type) {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        if (type === 'error') {
            oscillator.frequency.value = 200;
            oscillator.type = 'sawtooth';
            gainNode.gain.value = 0.15;
        } else if (type === 'success') {
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            gainNode.gain.value = 0.1;
        } else {
            oscillator.frequency.value = 600;
            oscillator.type = 'sine';
            gainNode.gain.value = 0.08;
        }
        
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.15);
    } catch (error) {
        // Audio not supported, silently ignore
    }
}

function addActivity(type, title, data = null) {
    const list = document.getElementById('activityList');
    if (!list) return;
    
    const empty = list.querySelector('.activity-empty');
    if (empty) empty.remove();
    
    const item = document.createElement('div');
    item.className = 'activity-item';
    
    const icons = {
        message: '💬',
        agent: '🤖',
        contract: '📄',
        system: '⚙️',
        publish: '📢',
        error: '❌',
        success: '✅',
        warning: '⚠️',
        info: 'ℹ️',
    };
    
    const time = new Date().toLocaleTimeString();
    
    item.innerHTML = `
        <span class="activity-icon">${icons[type] || '📌'}</span>
        <div class="activity-content">
            <div class="activity-title">${escapeHtml(title)}</div>
            ${data ? `<div class="activity-desc">${escapeHtml(typeof data === 'string' ? data : JSON.stringify(data).slice(0, 60))}${JSON.stringify(data).length > 60 ? '...' : ''}</div>` : ''}
        </div>
        <span class="activity-time">${time}</span>
    `;
    
    list.prepend(item);
    
    // Limit activities
    while (list.children.length > 100) {
        list.removeChild(list.lastChild);
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(seconds) {
    if (seconds < 0) return '0s';
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (days > 0) return `${days}d ${hours}h ${minutes}m`;
    if (hours > 0) return `${hours}h ${minutes}m ${secs}s`;
    if (minutes > 0) return `${minutes}m ${secs}s`;
    return `${secs}s`;
}

function formatDate(date) {
    if (!date) return 'N/A';
    try {
        const d = new Date(date);
        if (isNaN(d.getTime())) return 'Invalid date';
        return d.toLocaleString();
    } catch {
        return 'Invalid date';
    }
}

function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
}

function getStatusColor(status) {
    const colors = {
        active: '#48bb78',
        idle: '#f6ad55',
        busy: '#fc8181',
        offline: '#a0aec0',
        pending: '#f6ad55',
        completed: '#48bb78',
        terminated: '#fc8181',
        expired: '#a0aec0',
        success: '#48bb78',
        error: '#fc8181',
        warning: '#f6ad55',
        info: '#3b82f6',
    };
    return colors[status] || '#a0aec0';
}

function getStatusLabel(status) {
    const labels = {
        active: 'Active',
        idle: 'Idle',
        busy: 'Busy',
        offline: 'Offline',
        pending: 'Pending',
        completed: 'Completed',
        terminated: 'Terminated',
        expired: 'Expired',
    };
    return labels[status] || status || 'Unknown';
}

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substring(2, 8);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================================
// Navigation
// ============================================================

function navigateTo(section) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(s => {
        s.classList.remove('active');
    });
    
    // Deactivate all nav items
    document.querySelectorAll('.nav-item').forEach(n => {
        n.classList.remove('active');
    });
    
    // Show target section
    const target = document.getElementById(`section-${section}`);
    if (target) {
        target.classList.add('active');
    }
    
    // Activate nav item
    const navItem = document.querySelector(`.nav-item[data-section="${section}"]`);
    if (navItem) {
        navItem.classList.add('active');
    }
    
    AppState.currentSection = section;
    
    // Load data for section
    switch (section) {
        case 'overview':
            refreshOverview();
            break;
        case 'agents':
            refreshAgents();
            break;
        case 'messages':
            refreshMessages();
            break;
        case 'contracts':
            refreshContracts();
            break;
        case 'network':
            refreshNetwork();
            break;
        case 'settings':
            loadSettings();
            break;
    }
}

// ============================================================
// Overview / Dashboard
// ============================================================

function refreshOverview() {
    updateStats();
    updateCharts();
    updateActivityList();
    document.getElementById('headerTime').textContent = new Date().toLocaleString();
}

function updateStats() {
    const stats = AppState.stats;
    
    // Update stat displays
    setElementText('statAgents', stats.agentCount);
    setElementText('statMessages', stats.messageCount);
    setElementText('statContracts', stats.contractCount);
    setElementText('statUptime', formatTime(stats.uptime));
    setElementText('statConnections', stats.connections || 0);
    setElementText('statMemory', formatBytes(stats.memory));
    
    // Update contract breakdown
    setElementText('statActiveContracts', stats.activeContracts);
    setElementText('statPendingContracts', stats.pendingContracts);
    setElementText('statCompletedContracts', stats.completedContracts);
    
    // Update badges
    document.getElementById('agentBadge').textContent = stats.agentCount;
    document.getElementById('messageBadge').textContent = stats.messageCount;
    document.getElementById('contractBadge').textContent = stats.contractCount;
}

function setElementText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function updateActivityList() {
    // Activity list is updated by addActivity calls
}

// ============================================================
// Charts
// ============================================================

function updateCharts() {
    updateActivityChart();
    updateStatusChart();
}

function updateActivityChart() {
    const canvas = document.getElementById('activityChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const period = AppState.chartPeriod;
    
    // Generate data based on period
    let points, labels;
    const now = Date.now();
    
    switch (period) {
        case '1h':
            points = 60;
            const hourMs = 3600000;
            labels = Array.from({ length: points }, (_, i) => 
                new Date(now - (points - 1 - i) * 60000).toLocaleTimeString([], { minute: '2-digit' })
            );
            break;
        case '24h':
            points = 24;
            const dayMs = 3600000;
            labels = Array.from({ length: points }, (_, i) => 
                new Date(now - (points - 1 - i) * dayMs).toLocaleTimeString([], { hour: '2-digit' })
            );
            break;
        case '7d':
            points = 7;
            const weekMs = 86400000;
            labels = Array.from({ length: points }, (_, i) => 
                new Date(now - (points - 1 - i) * weekMs).toLocaleDateString([], { weekday: 'short' })
            );
            break;
        default:
            points = 24;
            labels = Array.from({ length: 24 }, (_, i) => 
                new Date(now - (23 - i) * 3600000).toLocaleTimeString([], { hour: '2-digit' })
            );
    }
    
    // Generate realistic data
    const data = Array.from({ length: points }, () => {
        const base = Math.floor(Math.random() * 20) + 5;
        const spike = Math.random() > 0.9 ? Math.floor(Math.random() * 40) : 0;
        return base + spike;
    });
    
    // Smooth data slightly
    const smoothed = data.map((val, idx) => {
        if (idx === 0 || idx === data.length - 1) return val;
        return (data[idx - 1] + data[idx] + data[idx + 1]) / 3;
    });
    
    // Destroy existing chart
    if (AppState.charts.activity) {
        AppState.charts.activity.destroy();
    }
    
    // Create new chart
    AppState.charts.activity = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Messages',
                data: smoothed,
                borderColor: getComputedStyle(document.documentElement).getPropertyValue('--primary').trim() || '#2d5a27',
                backgroundColor: 'rgba(45, 90, 39, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 2,
                pointHoverRadius: 6,
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 500,
            },
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 10,
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false,
                    },
                    ticks: {
                        maxTicksLimit: 12,
                        font: { size: 10 },
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.05)',
                        drawBorder: false,
                    },
                    ticks: {
                        font: { size: 10 },
                        maxTicksLimit: 5,
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index',
            },
        }
    });
}

function updateStatusChart() {
    const canvas = document.getElementById('statusChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Count agent statuses
    const statuses = { active: 0, idle: 0, busy: 0, offline: 0 };
    AppState.agents.forEach(a => {
        const status = a.status || 'idle';
        statuses[status] = (statuses[status] || 0) + 1;
    });
    
    // Destroy existing chart
    if (AppState.charts.status) {
        AppState.charts.status.destroy();
    }
    
    const colors = {
        active: '#48bb78',
        idle: '#f6ad55',
        busy: '#fc8181',
        offline: '#a0aec0',
    };
    
    const labels = Object.keys(statuses).filter(k => statuses[k] > 0);
    const data = labels.map(k => statuses[k]);
    const backgroundColors = labels.map(k => colors[k] || '#a0aec0');
    
    if (data.length === 0) {
        // No data, show empty state
        AppState.charts.status = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['No Agents'],
                datasets: [{
                    data: [1],
                    backgroundColor: ['#e2e8f0'],
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 8,
                            font: { size: 11 },
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#4a5568',
                        }
                    }
                },
                cutout: '70%',
            }
        });
        return;
    }
    
    AppState.charts.status = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.map(l => getStatusLabel(l)),
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderWidth: 0,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                animateRotate: true,
                duration: 800,
            },
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 8,
                        font: { size: 11 },
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#4a5568',
                        usePointStyle: true,
                        pointStyle: 'circle',
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '70%',
        }
    });
}

// ============================================================
// Agents
// ============================================================

async function refreshAgents() {
    if (AppState.isLoading) return;
    
    try {
        AppState.isLoading = true;
        const api = new VireoAPI();
        const search = document.getElementById('agentSearch')?.value || '';
        const status = document.getElementById('agentStatusFilter')?.value || 'all';
        const capability = document.getElementById('agentCapabilityFilter')?.value || 'all';
        
        const params = {};
        if (status && status !== 'all') params.status = status;
        if (capability && capability !== 'all') params.capability = capability;
        if (search) params.search = search;
        
        const agents = await api.getAgents(params);
        AppState.agents = Array.isArray(agents) ? agents : [];
        AppState.stats.agentCount = AppState.agents.length;
        
        renderAgents(AppState.agents);
        updateStats();
        updateStatusChart();
        
    } catch (error) {
        console.error('Failed to refresh agents:', error);
        showToast(`Failed to load agents: ${error.message}`, 'error');
        renderAgents([]);
    } finally {
        AppState.isLoading = false;
    }
}

function renderAgents(agents) {
    const grid = document.getElementById('agentGrid');
    if (!grid) return;
    
    if (!agents || agents.length === 0) {
        grid.innerHTML = `
            <div style="text-align:center;padding:60px 20px;color:var(--text-muted);grid-column:1/-1;">
                <div style="font-size:64px;margin-bottom:16px;">🤖</div>
                <p style="font-size:18px;font-weight:500;margin-bottom:8px;">No agents found</p>
                <p style="font-size:14px;margin-bottom:16px;">Create your first agent to get started</p>
                <button class="btn btn-primary" onclick="openCreateAgentModal()">
                    + Create Agent
                </button>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = agents.map(agent => {
        const status = agent.status || 'idle';
        const statusColor = getStatusColor(status);
        const statusLabel = getStatusLabel(status);
        const capabilities = agent.capabilities || [];
        
        return `
            <div class="agent-card" data-agent-id="${escapeHtml(agent.agent_id)}">
                <div class="agent-header">
                    <div>
                        <div class="agent-name">${escapeHtml(agent.name || 'Unnamed')}</div>
                        <div class="agent-did">${escapeHtml(agent.did || agent.agent_id)}</div>
                    </div>
                    <span class="agent-status" style="background:${statusColor}20;color:${statusColor}">
                        ${statusLabel}
                    </span>
                </div>
                <div style="font-size:12px;color:var(--text-secondary);margin-bottom:6px;">
                    v${escapeHtml(agent.version || '1.0.0')}
                    ${agent.created_at ? `• Created: ${formatDate(agent.created_at)}` : ''}
                </div>
                <div class="agent-capabilities">
                    ${capabilities.length > 0 ? 
                        capabilities.map(c => `<span class="agent-cap">${escapeHtml(c)}</span>`).join('') :
                        '<span style="font-size:12px;color:var(--text-muted);">No capabilities</span>'
                    }
                </div>
                <div class="agent-actions">
                    <button class="btn btn-sm btn-outline" onclick="viewAgent('${escapeHtml(agent.agent_id)}')">
                        👁️ View
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="messageAgent('${escapeHtml(agent.agent_id)}')">
                        💬 Message
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteAgent('${escapeHtml(agent.agent_id)}')">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

async function deleteAgent(agentId) {
    if (!agentId) {
        showToast('Invalid agent ID', 'error');
        return;
    }
    
    if (!confirm(`Are you sure you want to delete agent "${agentId}"? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const api = new VireoAPI();
        await api.deleteAgent(agentId);
        showToast(`Agent ${agentId} deleted successfully`, 'success');
        refreshAgents();
    } catch (error) {
        showToast(`Failed to delete agent: ${error.message}`, 'error');
    }
}

function viewAgent(agentId) {
    const agent = AppState.agents.find(a => a.agent_id === agentId);
    if (!agent) {
        showToast('Agent not found', 'error');
        return;
    }
    
    const content = `
        <div style="margin-bottom:12px;">
            <strong>ID:</strong> ${escapeHtml(agent.agent_id)}
        </div>
        <div style="margin-bottom:12px;">
            <strong>Name:</strong> ${escapeHtml(agent.name || 'Unnamed')}
        </div>
        <div style="margin-bottom:12px;">
            <strong>DID:</strong> ${escapeHtml(agent.did || 'N/A')}
        </div>
        <div style="margin-bottom:12px;">
            <strong>Version:</strong> ${escapeHtml(agent.version || '1.0.0')}
        </div>
        <div style="margin-bottom:12px;">
            <strong>Status:</strong> 
            <span style="color:${getStatusColor(agent.status || 'idle')}">
                ${getStatusLabel(agent.status || 'idle')}
            </span>
        </div>
        <div style="margin-bottom:12px;">
            <strong>Capabilities:</strong><br>
            ${(agent.capabilities || []).map(c => 
                `<span class="agent-cap">${escapeHtml(c)}</span>`
            ).join(' ') || 'None'}
        </div>
        <div style="margin-bottom:12px;">
            <strong>Created:</strong> ${formatDate(agent.created_at)}
        </div>
        ${agent.description ? `
            <div style="margin-bottom:12px;">
                <strong>Description:</strong><br>
                ${escapeHtml(agent.description)}
            </div>
        ` : ''}
    `;
    
    showModal(`Agent Details: ${escapeHtml(agent.name)}`, content, 'Close', () => {
        closeModal();
    });
}

function messageAgent(agentId) {
    const content = `
        <div class="settings-item">
            <label>Message Type</label>
            <select id="messageType" style="width:100%;padding:8px 12px;border:2px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-primary);color:var(--text-primary);">
                <option value="propose">Propose</option>
                <option value="commit">Commit</option>
                <option value="execute">Execute</option>
                <option value="verify">Verify</option>
                <option value="escalate">Escalate</option>
                <option value="done">Done</option>
            </select>
        </div>
        <div class="settings-item">
            <label>Payload (JSON)</label>
            <textarea id="messagePayload" rows="4" style="width:100%;padding:8px 12px;border:2px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-primary);color:var(--text-primary);font-family:monospace;font-size:13px;">{"task": "example"}</textarea>
        </div>
        <div class="settings-item">
            <label>Recipient</label>
            <input type="text" id="messageRecipient" value="${escapeHtml(agentId)}" readonly style="width:100%;padding:8px 12px;border:2px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-hover);color:var(--text-secondary);">
        </div>
    `;
    
    showModal('Send Message', content, 'Send', async () => {
        const type = document.getElementById('messageType').value;
        const payloadStr = document.getElementById('messagePayload').value;
        const recipient = document.getElementById('messageRecipient').value;
        
        let payload;
        try {
            payload = JSON.parse(payloadStr);
        } catch (e) {
            showToast('Invalid JSON payload', 'error');
            return;
        }
        
        try {
            const api = new VireoAPI();
            await api.sendMessage({ type, payload, recipient });
            showToast('Message sent successfully', 'success');
            closeModal();
        } catch (error) {
            showToast(`Failed to send message: ${error.message}`, 'error');
        }
    });
}

// ============================================================
// Messages
// ============================================================

async function refreshMessages() {
    try {
        const api = new VireoAPI();
        const search = document.getElementById('messageSearch')?.value || '';
        const type = document.getElementById('messageTypeFilter')?.value || 'all';
        
        // Get messages from first available agent
        let messages = [];
        if (AppState.agents.length > 0) {
            const params = {};
            if (type && type !== 'all') params.type = type;
            if (search) params.search = search;
            
            const agentId = AppState.agents[0].agent_id;
            messages = await api.getMessages(agentId, params);
        }
        
        AppState.messages = Array.isArray(messages) ? messages : [];
        renderMessages(AppState.messages);
        AppState.stats.messageCount = AppState.messages.length;
        updateStats();
        
    } catch (error) {
        console.error('Failed to refresh messages:', error);
        renderMessages([]);
    }
}

function renderMessages(messages) {
    const list = document.getElementById('messageList');
    if (!list) return;
    
    if (!messages || messages.length === 0) {
        list.innerHTML = `
            <div class="message-empty">
                <div style="font-size:64px;margin-bottom:16px;">💬</div>
                <p style="font-size:18px;font-weight:500;margin-bottom:8px;">No messages</p>
                <p style="font-size:14px;color:var(--text-muted);">Messages between agents will appear here</p>
            </div>
        `;
        return;
    }
    
    list.innerHTML = messages.map(msg => {
        const type = msg.type || 'unknown';
        const typeClass = type.toLowerCase();
        
        return `
            <div class="message-item">
                <span class="message-type ${typeClass}">${escapeHtml(type)}</span>
                <div class="message-content">
                    <div class="message-sender">
                        ${escapeHtml(msg.sender || 'unknown')} → ${escapeHtml(msg.recipient || 'unknown')}
                    </div>
                    <div class="message-preview">
                        ${escapeHtml(JSON.stringify(msg.payload || {}, null, 2).slice(0, 100))}
                        ${JSON.stringify(msg.payload || {}).length > 100 ? '...' : ''}
                    </div>
                </div>
                <span class="message-time">${formatDate(msg.timestamp)}</span>
            </div>
        `;
    }).join('');
}

// ============================================================
// Contracts
// ============================================================

async function refreshContracts() {
    try {
        const api = new VireoAPI();
        const contracts = await api.getContracts();
        AppState.contracts = Array.isArray(contracts) ? contracts : [];
        AppState.stats.contractCount = AppState.contracts.length;
        AppState.stats.activeContracts = AppState.contracts.filter(c => c.status === 'active').length;
        AppState.stats.pendingContracts = AppState.contracts.filter(c => c.status === 'pending').length;
        AppState.stats.completedContracts = AppState.contracts.filter(c => c.status === 'completed').length;
        
        renderContracts(AppState.contracts);
        updateStats();
        
    } catch (error) {
        console.error('Failed to refresh contracts:', error);
        renderContracts([]);
    }
}

function renderContracts(contracts) {
    const list = document.getElementById('contractList');
    if (!list) return;
    
    if (!contracts || contracts.length === 0) {
        list.innerHTML = `
            <div class="contract-empty">
                <div style="font-size:64px;margin-bottom:16px;">📄</div>
                <p style="font-size:18px;font-weight:500;margin-bottom:8px;">No contracts</p>
                <p style="font-size:14px;color:var(--text-muted);">Create a contract to formalize agreements between agents</p>
            </div>
        `;
        return;
    }
    
    list.innerHTML = contracts.map(contract => {
        const status = contract.status || 'pending';
        const statusLabel = getStatusLabel(status);
        
        return `
            <div class="contract-item">
                <span class="contract-id">${escapeHtml(contract.contract_id || 'N/A')}</span>
                <span class="contract-status ${status}">${statusLabel}</span>
                <div class="contract-info">
                    <div class="contract-parties">
                        ${(contract.parties || []).map(p => escapeHtml(p)).join(' → ')}
                    </div>
                    <div class="contract-terms">
                        ${escapeHtml(JSON.stringify(contract.terms || {}).slice(0, 80))}
                        ${JSON.stringify(contract.terms || {}).length > 80 ? '...' : ''}
                    </div>
                </div>
                <div class="contract-expiry">
                    ${contract.expires_at ? `Expires: ${formatDate(contract.expires_at)}` : 'No expiry'}
                </div>
                ${status === 'pending' ? `
                    <button class="btn btn-sm btn-success" onclick="signContract('${escapeHtml(contract.contract_id)}')">
                        ✍️ Sign
                    </button>
                ` : ''}
            </div>
        `;
    }).join('');
}

async function signContract(contractId) {
    if (!contractId) {
        showToast('Invalid contract ID', 'error');
        return;
    }
    
    try {
        const api = new VireoAPI();
        await api.signContract(contractId);
        showToast(`Contract ${contractId} signed successfully`, 'success');
        refreshContracts();
    } catch (error) {
        showToast(`Failed to sign contract: ${error.message}`, 'error');
    }
}

// ============================================================
// Network
// ============================================================

function refreshNetwork() {
    // Build network graph from agents
    const nodes = AppState.agents.map(agent => ({
        id: agent.agent_id,
        label: agent.name || agent.agent_id,
        status: agent.status || 'idle',
        capabilities: agent.capabilities || [],
        size: 30 + (agent.capabilities?.length || 0) * 5,
    }));
    
    // Generate edges from message history
    const edges = [];
    const messagePairs = new Set();
    
    AppState.messages.forEach(msg => {
        if (msg.sender && msg.recipient) {
            const key = [msg.sender, msg.recipient].sort().join('-');
            if (!messagePairs.has(key)) {
                messagePairs.add(key);
                edges.push({
                    source: msg.sender,
                    target: msg.recipient,
                    weight: 1,
                });
            }
        }
    });
    
    AppState.networkNodes = nodes;
    AppState.networkEdges = edges;
    
    renderNetwork(nodes, edges);
}

function renderNetwork(nodes, edges) {
    const container = document.getElementById('networkVis');
    if (!container) return;
    
    if (nodes.length === 0) {
        container.innerHTML = `
            <div class="network-empty">
                <div style="font-size:64px;margin-bottom:16px;">🌐</div>
                <p style="font-size:18px;font-weight:500;margin-bottom:8px;">Network Visualization</p>
                <p style="font-size:14px;color:var(--text-muted);">Connect agents to see the network graph</p>
            </div>
        `;
        return;
    }
    
    // Simple force-directed layout using canvas
    container.innerHTML = `
        <canvas id="networkCanvas" style="width:100%;height:100%;"></canvas>
    `;
    
    const canvas = document.getElementById('networkCanvas');
    if (!canvas) return;
    
    const rect = container.getBoundingClientRect();
    canvas.width = rect.width || 600;
    canvas.height = rect.height || 400;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Simple layout: position nodes in a circle
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 60;
    
    // Draw edges
    ctx.strokeStyle = 'rgba(160, 174, 192, 0.3)';
    ctx.lineWidth = 1;
    edges.forEach(edge => {
        const sourceIdx = nodes.findIndex(n => n.id === edge.source);
        const targetIdx = nodes.findIndex(n => n.id === edge.target);
        if (sourceIdx === -1 || targetIdx === -1) return;
        
        const angle1 = (sourceIdx / nodes.length) * 2 * Math.PI - Math.PI / 2;
        const angle2 = (targetIdx / nodes.length) * 2 * Math.PI - Math.PI / 2;
        
        const x1 = centerX + radius * Math.cos(angle1);
        const y1 = centerY + radius * Math.sin(angle1);
        const x2 = centerX + radius * Math.cos(angle2);
        const y2 = centerY + radius * Math.sin(angle2);
        
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
    });
    
    // Draw nodes
    nodes.forEach((node, index) => {
        const angle = (index / nodes.length) * 2 * Math.PI - Math.PI / 2;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        const size = Math.min(node.size || 30, 50);
        
        // Node circle
        const gradient = ctx.createRadialGradient(x - 5, y - 5, 0, x, y, size);
        const color = getStatusColor(node.status);
        gradient.addColorStop(0, color);
        gradient.addColorStop(1, color + '80');
        
        ctx.beginPath();
        ctx.arc(x, y, size / 2, 0, 2 * Math.PI);
        ctx.fillStyle = gradient;
        ctx.fill();
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Label
        ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim() || '#1a2332';
        ctx.font = '12px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        ctx.fillText(node.label.slice(0, 10), x, y - size / 2 - 4);
        
        // Status dot
        ctx.beginPath();
        ctx.arc(x, y + size / 2 + 6, 4, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
    });
}

// ============================================================
// Settings
// ============================================================

function loadSettings() {
    document.getElementById('apiUrl').value = AppState.settings.apiUrl;
    document.getElementById('wsUrl').value = AppState.settings.wsUrl;
    document.getElementById('apiKey').value = AppState.settings.apiKey;
    document.getElementById('themeSelect').value = AppState.settings.theme;
    document.getElementById('autoRefresh').checked = AppState.settings.autoRefresh;
    document.getElementById('soundAlerts').checked = AppState.settings.soundAlerts;
    document.getElementById('notifications').checked = AppState.settings.notifications;
}

function saveSettings() {
    const apiUrl = document.getElementById('apiUrl').value.trim();
    const wsUrl = document.getElementById('wsUrl').value.trim();
    const apiKey = document.getElementById('apiKey').value.trim();
    const theme = document.getElementById('themeSelect').value;
    const autoRefresh = document.getElementById('autoRefresh').checked;
    const soundAlerts = document.getElementById('soundAlerts').checked;
    const notifications = document.getElementById('notifications').checked;
    
    // Validate URLs
    try {
        new URL(apiUrl);
    } catch {
        showToast('Invalid API URL', 'error');
        return;
    }
    
    try {
        new URL(wsUrl);
    } catch {
        showToast('Invalid WebSocket URL', 'error');
        return;
    }
    
    AppState.settings.apiUrl = apiUrl;
    AppState.settings.wsUrl = wsUrl;
    AppState.settings.apiKey = apiKey;
    AppState.settings.theme = theme;
    AppState.settings.autoRefresh = autoRefresh;
    AppState.settings.soundAlerts = soundAlerts;
    AppState.settings.notifications = notifications;
    
    localStorage.setItem('vireo_api_url', apiUrl);
    localStorage.setItem('vireo_ws_url', wsUrl);
    localStorage.setItem('vireo_api_key', apiKey);
    localStorage.setItem('vireo_theme', theme);
    localStorage.setItem('vireo_auto_refresh', String(autoRefresh));
    localStorage.setItem('vireo_sound_alerts', String(soundAlerts));
    localStorage.setItem('vireo_notifications', String(notifications));
    
    applyTheme(theme);
    updateRefreshInterval();
    
    showToast('Settings saved successfully', 'success');
    
    // Reconnect with new settings
    if (AppState.connected) {
        wsClient.disconnect();
        setTimeout(() => wsClient.connect(), 500);
    }
}

function applyTheme(theme) {
    if (theme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
        AppState.darkMode = prefersDark;
    } else {
        document.documentElement.setAttribute('data-theme', theme);
        AppState.darkMode = theme === 'dark';
    }
}

function updateRefreshInterval() {
    if (AppState.refreshInterval) {
        clearInterval(AppState.refreshInterval);
        AppState.refreshInterval = null;
    }
    
    if (AppState.settings.autoRefresh) {
        AppState.refreshInterval = setInterval(() => {
            if (AppState.connected) {
                switch (AppState.currentSection) {
                    case 'overview':
                        refreshOverview();
                        break;
                    case 'agents':
                        refreshAgents();
                        break;
                    case 'messages':
                        refreshMessages();
                        break;
                    case 'contracts':
                        refreshContracts();
                        break;
                    case 'network':
                        refreshNetwork();
                        break;
                }
            }
        }, 5000);
    }
}

// ============================================================
// Modals
// ============================================================

function showModal(title, content, confirmText = 'Confirm', onConfirm = null, onCancel = null) {
    // Remove existing modal
    const existing = document.querySelector('.modal-overlay');
    if (existing) existing.remove();
    
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(4px);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.2s ease;
    `;
    
    const modal = document.createElement('div');
    modal.style.cssText = `
        background: var(--bg-card);
        border-radius: 16px;
        max-width: 560px;
        width: 92%;
        max-height: 90vh;
        overflow: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: slideUp 0.3s ease;
    `;
    
    const hasConfirm = typeof onConfirm === 'function';
    
    modal.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:16px 20px;border-bottom:1px solid var(--border-color);">
            <h2 style="font-size:18px;font-weight:600;margin:0;">${escapeHtml(title)}</h2>
            <button id="modalCloseBtn" style="background:none;border:none;font-size:24px;color:var(--text-muted);cursor:pointer;padding:0 4px;">&times;</button>
        </div>
        <div style="padding:20px;">${content}</div>
        <div style="display:flex;justify-content:flex-end;gap:10px;padding:12px 20px;border-top:1px solid var(--border-color);">
            <button id="modalCancelBtn" class="btn btn-outline">${hasConfirm ? 'Cancel' : 'Close'}</button>
            ${hasConfirm ? `<button id="modalConfirmBtn" class="btn btn-primary">${escapeHtml(confirmText)}</button>` : ''}
        </div>
    `;
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    const cleanup = () => {
        if (overlay.parentNode) {
            overlay.remove();
        }
        if (typeof onCancel === 'function' && !modal._confirmed) {
            onCancel();
        }
    };
    
    document.getElementById('modalCloseBtn').onclick = cleanup;
    document.getElementById('modalCancelBtn').onclick = cleanup;
    overlay.onclick = (e) => {
        if (e.target === overlay) cleanup();
    };
    
    if (hasConfirm) {
        document.getElementById('modalConfirmBtn').onclick = () => {
            modal._confirmed = true;
            onConfirm();
        };
    }
    
    // Keyboard support
    const handleKeydown = (e) => {
        if (e.key === 'Escape') {
            cleanup();
            document.removeEventListener('keydown', handleKeydown);
        }
    };
    document.addEventListener('keydown', handleKeydown);
}

function closeModal() {
    const overlay = document.querySelector('.modal-overlay');
    if (overlay) overlay.remove();
}

// ============================================================
// Modal Opening Functions
// ============================================================

function openCreateAgentModal() {
    const name = `Agent_${Date.now().toString(36)}`;
    const content = `
        <div class="settings-item">
            <label>Agent Name</label>
            <input type="text" id="agentNameInput" value="${name}" style="width:100%;padding:8px 12px;border:2px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-primary);color:var(--text-primary);">
        </div>
        <div class="settings-item">
            <label>Version</label>
            <input type="text" id="agentVersionInput" value="1.0.0" style="width:100%;padding:8px 12px;border:2px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-primary);color:var(--text-primary);">
        </div>
        <div class="settings-item">
            <label>Capabilities (comma-separated)</label>
            <input type="text" id="agentCapsInput" value="text-generation, code-analysis" style="width:100%;padding:8px 12px;border:2px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-primary);color:var(--text-primary);">
        </div>
        <div class="settings-item">
            <label>Description</label>
            <input type="text" id="agentDescInput" value="Created via Dashboard" style="width:100%;padding:8px 12px;border:2px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-primary);color:var(--text-primary);">
        </div>
    `;
    
    showModal('Create New Agent', content, 'Create', async () => {
        const name = document.getElementById('agentNameInput').value.trim();
        const version = document.getElementById('agentVersionInput').value.trim();
        const capsStr = document.getElementById('agentCapsInput').value.trim();
        const description = document.getElementById('agentDescInput').value.trim();
        
        if (!name) {
            showToast('Agent name is required', 'error');
            return;
        }
        
        const capabilities = capsStr.split(',').map(s => s.trim()).filter(Boolean);
        
        try {
            const api = new VireoAPI();
            await api.createAgent({ name, version, capabilities, description });
            showToast(`Agent "${name}" created successfully`, 'success');
            refreshAgents();
            closeModal();
        } catch (error) {
            showToast(`Failed to create agent: ${error.message}`, 'error');
        }
    });
}

function openCreateContractModal() {
    const content = `
        <div class="settings-item">
            <label>Parties (comma-separated agent IDs)</label>
            <input type="text" id="contractPartiesInput" placeholder="agent_abc, agent_def" style="width:100%;padding:8px 12px;border:2px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-primary);color:var(--text-primary);">
        </div>
        <div class="settings-item">
            <label>Terms (JSON)</label>
            <textarea id="contractTermsInput" rows="4" style="width:100%;padding:8px 12px;border:2px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-primary);color:var(--text-primary);font-family:monospace;font-size:13px;">{"price": 100, "deadline": "2024-12-31", "scope": "Data analysis"}</textarea>
        </div>
        <div class="settings-item">
            <label>Duration (days)</label>
            <input type="number" id="contractDurationInput" value="30" min="1" max="365" style="width:100%;padding:8px 12px;border:2px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-primary);color:var(--text-primary);">
        </div>
        <div class="settings-item">
            <label>Escrow Enabled</label>
            <select id="contractEscrowInput" style="width:100%;padding:8px 12px;border:2px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-primary);color:var(--text-primary);">
                <option value="true">Yes</option>
                <option value="false">No</option>
            </select>
        </div>
    `;
    
    showModal('Create New Contract', content, 'Create', async () => {
        const partiesStr = document.getElementById('contractPartiesInput').value.trim();
        const termsStr = document.getElementById('contractTermsInput').value.trim();
        const duration = parseInt(document.getElementById('contractDurationInput').value);
        const escrowEnabled = document.getElementById('contractEscrowInput').value === 'true';
        
        if (!partiesStr) {
            showToast('At least one party is required', 'error');
            return;
        }
        
        let terms;
        try {
            terms = JSON.parse(termsStr);
        } catch (e) {
            showToast('Invalid JSON in terms field', 'error');
            return;
        }
        
        const parties = partiesStr.split(',').map(s => s.trim()).filter(Boolean);
        
        try {
            const api = new VireoAPI();
            await api.createContract({ 
                terms, 
                parties, 
                duration_days: duration,
                escrow_enabled: escrowEnabled 
            });
            showToast('Contract created successfully', 'success');
            refreshContracts();
            closeModal();
        } catch (error) {
            showToast(`Failed to create contract: ${error.message}`, 'error');
        }
    });
}

// ============================================================
// Initialization
// ============================================================

const api = new VireoAPI();
const wsClient = new VireoWS();

function init() {
    console.log('🌿 Vireo Dashboard v3.0.0 initializing...');
    
    // Apply theme
    applyTheme(AppState.settings.theme);
    
    // Load settings into UI
    loadSettings();
    
    // Set up navigation
    document.querySelectorAll('.nav-item').forEach(el => {
        el.addEventListener('click', (e) => {
            e.preventDefault();
            const section = el.dataset.section;
            if (section) {
                navigateTo(section);
            }
        });
    });
    
    // Set up connect button
    document.getElementById('connectBtn').addEventListener('click', () => {
        if (AppState.connected) {
            wsClient.disconnect();
        } else {
            wsClient.connect();
        }
    });
    
    // Set up create buttons
    document.getElementById('createAgentBtn').addEventListener('click', openCreateAgentModal);
    document.getElementById('createContractBtn').addEventListener('click', openCreateContractModal);
    
    // Set up clear messages
    document.getElementById('clearMessagesBtn').addEventListener('click', () => {
        document.getElementById('messageList').innerHTML = `
            <div class="message-empty">
                <div style="font-size:64px;margin-bottom:16px;">🧹</div>
                <p>Messages cleared</p>
            </div>
        `;
        AppState.messages = [];
        updateStats();
        showToast('Messages cleared', 'info');
    });
    
    // Set up settings save
    document.getElementById('saveSettingsBtn').addEventListener('click', saveSettings);
    
    // Set up filter events with debounce
    const debouncedRefreshAgents = debounce(refreshAgents, 300);
    const debouncedRefreshMessages = debounce(refreshMessages, 300);
    
    document.getElementById('agentSearch').addEventListener('input', debouncedRefreshAgents);
    document.getElementById('agentStatusFilter').addEventListener('change', refreshAgents);
    document.getElementById('agentCapabilityFilter').addEventListener('change', refreshAgents);
    document.getElementById('messageSearch').addEventListener('input', debouncedRefreshMessages);
    document.getElementById('messageTypeFilter').addEventListener('change', refreshMessages);
    
    // Set up chart period buttons
    document.querySelectorAll('.chart-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.chart-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            AppState.chartPeriod = btn.dataset.period || '1h';
            updateCharts();
        });
    });
    
    // WebSocket events
    wsClient.on('connected', () => {
        AppState.connected = true;
        AppState.reconnectAttempts = 0;
        refreshOverview();
        refreshAgents();
        refreshMessages();
        refreshContracts();
        refreshNetwork();
    });
    
    wsClient.on('disconnected', () => {
        AppState.connected = false;
        updateConnectionStatus('disconnected');
    });
    
    wsClient.on('message_received', () => {
        AppState.stats.messageCount++;
        updateStats();
        updateActivityList();
    });
    
    wsClient.on('agent_status', (data) => {
        if (data.status) {
            AppState.stats.agentCount = data.count || AppState.stats.agentCount;
            updateStats();
        }
    });
    
    // Auto-connect
    setTimeout(() => {
        if (AppState.settings.apiKey) {
            wsClient.connect();
        } else {
            updateConnectionStatus('disconnected');
        }
    }, 500);
    
    // Uptime counter
    AppState.uptimeInterval = setInterval(() => {
        AppState.stats.uptime = (Date.now() - AppState.startTime) / 1000;
        document.getElementById('statUptime').textContent = formatTime(AppState.stats.uptime);
    }, 1000);
    
    // Initial refresh
    updateRefreshInterval();
    navigateTo('overview');
    
    console.log('🌿 Vireo Dashboard v3.0.0 ready');
}

// Handle window resize for charts
const throttledResize = throttle(() => {
    updateCharts();
    if (AppState.currentSection === 'network') {
        refreshNetwork();
    }
}, 500);

window.addEventListener('resize', throttledResize);

// Handle theme change from system
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (AppState.settings.theme === 'auto') {
        applyTheme('auto');
    }
});

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}