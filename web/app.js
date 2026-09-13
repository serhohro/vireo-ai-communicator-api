/**
 * Vireo Web Interface - Main Application
 * Complete frontend for Vireo AI platform
 */

// ============================================================
// Application State
// ============================================================
const AppState = {
    // Connection
    connected: false,
    connecting: false,
    ws: null,
    
    // Data
    agents: [],
    messages: [],
    contracts: [],
    activities: [],
    
    // Stats
    stats: {
        agentCount: 0,
        messageCount: 0,
        contractCount: 0,
        uptime: 0,
    },
    
    // UI
    currentPage: 'dashboard',
    selectedAgent: null,
    selectedContract: null,
    
    // Settings
    settings: {
        apiUrl: localStorage.getItem('vireo_api_url') || 'http://localhost:8000/api/v1',
        wsUrl: localStorage.getItem('vireo_ws_url') || 'ws://localhost:8000/ws',
        apiKey: localStorage.getItem('vireo_api_key') || '',
        jwtToken: localStorage.getItem('vireo_jwt_token') || '',
        autoRefresh: localStorage.getItem('vireo_auto_refresh') !== 'false',
        theme: localStorage.getItem('vireo_theme') || 'auto',
    },
    
    // Timers
    refreshInterval: null,
    uptimeInterval: null,
    startTime: Date.now(),
};

// ============================================================
// API Client
// ============================================================
class VireoAPI {
    constructor() {
        this.baseUrl = AppState.settings.apiUrl;
        this.apiKey = AppState.settings.apiKey;
        this.jwtToken = AppState.settings.jwtToken;
    }
    
    get headers() {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }
        if (this.jwtToken) {
            headers['Authorization'] = `Bearer ${this.jwtToken}`;
        }
        return headers;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const response = await fetch(url, {
            ...options,
            headers: {
                ...this.headers,
                ...options.headers,
            },
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: response.statusText }));
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        
        return response.json();
    }
    
    // Agents
    async getAgents(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/agents${query ? '?' + query : ''}`);
    }
    
    async createAgent(data) {
        return this.request('/agents', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
    
    async deleteAgent(agentId) {
        return this.request(`/agents/${agentId}`, {
            method: 'DELETE',
        });
    }
    
    // Messages
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
    
    // Contracts
    async createContract(data) {
        return this.request('/contracts', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
    
    async getContracts() {
        return this.request('/contracts');
    }
    
    async signContract(contractId) {
        return this.request(`/contracts/${contractId}/sign`, {
            method: 'POST',
        });
    }
    
    // System
    async getStatus() {
        return this.request('/system/status');
    }
    
    async getHealth() {
        return this.request('/system/health');
    }
    
    // Discovery
    async discover(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/discover${query ? '?' + query : ''}`);
    }
    
    async getTrust(agentId) {
        return this.request(`/trust/${agentId}`);
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
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000;
        this.handlers = {};
        this.pingInterval = null;
        this.pingTimeout = null;
    }
    
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return;
        }
        
        this.connected = false;
        updateConnectionStatus('connecting');
        
        const url = AppState.settings.wsUrl;
        const params = new URLSearchParams();
        if (AppState.settings.apiKey) {
            params.append('api_key', AppState.settings.apiKey);
        }
        if (AppState.settings.jwtToken) {
            params.append('token', AppState.settings.jwtToken);
        }
        
        const fullUrl = `${url}?${params.toString()}`;
        
        try {
            this.ws = new WebSocket(fullUrl);
            
            this.ws.onopen = () => {
                this.connected = true;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;
                updateConnectionStatus('connected');
                AppState.connected = true;
                
                this.startPing();
                this.emit('connected');
                
                showToast('Connected to Vireo server', 'success');
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };
            
            this.ws.onclose = () => {
                this.connected = false;
                AppState.connected = false;
                this.stopPing();
                updateConnectionStatus('disconnected');
                this.emit('disconnected');
                
                showToast('Disconnected from Vireo server', 'warning');
                
                this.reconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.emit('error', error);
            };
            
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.reconnect();
        }
    }
    
    reconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            showToast('Maximum reconnect attempts reached', 'error');
            return;
        }
        
        this.reconnectAttempts++;
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
        
        setTimeout(() => {
            if (!this.connected) {
                this.connect();
            }
        }, this.reconnectDelay);
    }
    
    disconnect() {
        this.stopPing();
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.connected = false;
        AppState.connected = false;
        updateConnectionStatus('disconnected');
    }
    
    startPing() {
        this.stopPing();
        this.pingInterval = setInterval(() => {
            if (this.connected && this.ws && this.ws.readyState === WebSocket.OPEN) {
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
        if (this.connected && this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
            return true;
        }
        return false;
    }
    
    handleMessage(data) {
        this.emit('message', data);
        
        switch (data.type) {
            case 'welcome':
                showToast(`Connected as ${data.payload.agent_id || 'anonymous'}`, 'info');
                break;
            
            case 'heartbeat_ack':
                // Heartbeat acknowledged
                break;
            
            case 'message':
                // Message from another agent
                this.emit('message_received', data.payload);
                addActivity('message', `${data.payload.sender} sent a message`, data.payload);
                break;
            
            case 'publish':
                // Published message from room
                this.emit('publish', data.payload);
                break;
            
            case 'error':
                showToast(`WebSocket error: ${data.payload.error}`, 'error');
                break;
            
            default:
                // Unknown message type
                break;
        }
    }
    
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
                } catch (e) {
                    console.error(`Handler error for ${event}:`, e);
                }
            });
        }
    }
}

// ============================================================
// UI Helpers
// ============================================================
function updateConnectionStatus(state) {
    const dot = document.getElementById('connectionStatus').querySelector('.status-dot');
    const text = document.getElementById('connectionStatus').querySelector('.status-text');
    const btn = document.getElementById('connectBtn');
    
    dot.className = 'status-dot';
    switch (state) {
        case 'connected':
            dot.classList.add('connected');
            text.textContent = 'Connected';
            btn.textContent = 'Disconnect';
            btn.className = 'btn btn-danger btn-sm';
            break;
        case 'connecting':
            dot.classList.add('connecting');
            text.textContent = 'Connecting...';
            btn.textContent = 'Connecting';
            btn.disabled = true;
            break;
        case 'disconnected':
        default:
            dot.classList.add('disconnected');
            text.textContent = 'Disconnected';
            btn.textContent = 'Connect';
            btn.className = 'btn btn-primary btn-sm';
            btn.disabled = false;
            break;
    }
}

function showToast(message, type = 'info', title = '') {
    const container = document.getElementById('toastContainer');
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
            ${title ? `<div class="toast-title">${title}</div>` : ''}
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close">&times;</button>
    `;
    
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.remove();
    });
    
    container.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(20px)';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

function addActivity(type, title, data = null) {
    const list = document.getElementById('activityList');
    const empty = list.querySelector('.activity-empty');
    if (empty) empty.remove();
    
    const item = document.createElement('div');
    item.className = 'activity-item';
    
    const icons = {
        message: '💬',
        agent: '🤖',
        contract: '📄',
        system: '⚙️',
        error: '❌',
    };
    
    const time = new Date().toLocaleTimeString();
    
    item.innerHTML = `
        <span class="activity-icon">${icons[type] || '📌'}</span>
        <div class="activity-content">
            <div class="activity-title">${title}</div>
            ${data ? `<div class="activity-desc">${JSON.stringify(data).slice(0, 60)}...</div>` : ''}
        </div>
        <span class="activity-time">${time}</span>
    `;
    
    list.prepend(item);
    
    // Limit activities
    while (list.children.length > 50) {
        list.removeChild(list.lastChild);
    }
}

function formatTime(seconds) {
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
    return new Date(date).toLocaleString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================
// Page Navigation
// ============================================================
function navigateTo(page) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    
    // Show target page
    const targetPage = document.getElementById(`page-${page}`);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.page === page);
    });
    
    AppState.currentPage = page;
    
    // Load data for page
    switch (page) {
        case 'dashboard':
            refreshDashboard();
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
    }
}

// ============================================================
// Dashboard
// ============================================================
async function refreshDashboard() {
    try {
        const api = new VireoAPI();
        
        // Get status
        const status = await api.getStatus();
        
        // Update stats
        const stats = AppState.stats;
        document.getElementById('agentCount').textContent = stats.agentCount;
        document.getElementById('messageCount').textContent = stats.messageCount;
        document.getElementById('contractCount').textContent = stats.contractCount;
        document.getElementById('uptimeDisplay').textContent = formatTime(stats.uptime);
        
        // Update chart
        updateChart();
        
    } catch (error) {
        console.error('Failed to refresh dashboard:', error);
    }
}

// ============================================================
// Chart
// ============================================================
let chartInstance = null;

function updateChart() {
    const canvas = document.getElementById('activityChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Generate sample data
    const labels = [];
    const data = [];
    const now = Date.now();
    const hour = 3600000;
    
    for (let i = 23; i >= 0; i--) {
        labels.push(new Date(now - i * hour).toLocaleTimeString([], { hour: '2-digit' }));
        data.push(Math.floor(Math.random() * 30) + 5);
    }
    
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Messages',
                data: data,
                borderColor: '#2d5a27',
                backgroundColor: 'rgba(45, 90, 39, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false,
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.05)',
                    }
                }
            }
        }
    });
}

// ============================================================
// Agents
// ============================================================
async function refreshAgents() {
    try {
        const api = new VireoAPI();
        const search = document.getElementById('agentSearch').value;
        const status = document.getElementById('agentStatusFilter').value;
        const capability = document.getElementById('agentCapabilityFilter').value;
        
        const params = {};
        if (status && status !== 'all') params.status = status;
        if (capability && capability !== 'all') params.capability = capability;
        if (search) params.search = search;
        
        const agents = await api.getAgents(params);
        AppState.agents = agents;
        
        renderAgents(agents);
        
    } catch (error) {
        console.error('Failed to refresh agents:', error);
        showToast('Failed to load agents', 'error');
    }
}

function renderAgents(agents) {
    const grid = document.getElementById('agentGrid');
    
    if (!agents || agents.length === 0) {
        grid.innerHTML = `
            <div class="agent-empty" style="text-align:center;padding:60px 20px;color:var(--text-muted);grid-column:1/-1;">
                <div style="font-size:48px;margin-bottom:16px;">🤖</div>
                <p>No agents found</p>
                <p style="font-size:13px;">Create your first agent to get started</p>
                <button class="btn btn-primary" style="margin-top:12px;" onclick="openCreateAgentModal()">
                    + Create Agent
                </button>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = agents.map(agent => `
        <div class="agent-card" data-agent-id="${agent.agent_id}">
            <div class="agent-header">
                <div>
                    <div class="agent-name">${escapeHtml(agent.name)}</div>
                    <div class="agent-did">${escapeHtml(agent.did || agent.agent_id)}</div>
                </div>
                <span class="agent-status-badge ${agent.status || 'idle'}">${agent.status || 'idle'}</span>
            </div>
            <div style="font-size:13px;color:var(--text-secondary);margin-bottom:8px;">
                v${agent.version || '1.0.0'}
            </div>
            <div class="agent-capabilities">
                ${(agent.capabilities || []).map(cap => 
                    `<span class="agent-capability">${escapeHtml(cap)}</span>`
                ).join('')}
            </div>
            <div style="font-size:12px;color:var(--text-muted);margin-bottom:8px;">
                ${agent.created_at ? `Created: ${formatDate(agent.created_at)}` : ''}
            </div>
            <div class="agent-actions">
                <button class="btn btn-sm btn-outline" onclick="viewAgent('${agent.agent_id}')">View</button>
                <button class="btn btn-sm btn-outline" onclick="messageAgent('${agent.agent_id}')">Message</button>
                <button class="btn btn-sm btn-danger" onclick="deleteAgent('${agent.agent_id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

async function deleteAgent(agentId) {
    if (!confirm(`Are you sure you want to delete agent ${agentId}?`)) return;
    
    try {
        const api = new VireoAPI();
        await api.deleteAgent(agentId);
        showToast('Agent deleted successfully', 'success');
        refreshAgents();
    } catch (error) {
        showToast(`Failed to delete agent: ${error.message}`, 'error');
    }
}

function viewAgent(agentId) {
    showToast(`Viewing agent ${agentId}`, 'info');
}

function messageAgent(agentId) {
    showToast(`Opening message dialog for ${agentId}`, 'info');
}

// ============================================================
// Messages
// ============================================================
async function refreshMessages() {
    try {
        const api = new VireoAPI();
        const search = document.getElementById('messageSearch').value;
        const type = document.getElementById('messageTypeFilter').value;
        
        // Get messages for first agent or use sample
        const agents = await api.getAgents({ limit: 1 });
        if (agents && agents.length > 0) {
            const params = {};
            if (type && type !== 'all') params.type = type;
            if (search) params.search = search;
            
            const messages = await api.getMessages(agents[0].agent_id, params);
            AppState.messages = messages;
            renderMessages(messages);
        } else {
            renderMessages([]);
        }
        
    } catch (error) {
        console.error('Failed to refresh messages:', error);
        renderMessages([]);
    }
}

function renderMessages(messages) {
    const list = document.getElementById('messageList');
    
    if (!messages || messages.length === 0) {
        list.innerHTML = `
            <div class="message-empty">
                <div style="font-size:48px;margin-bottom:16px;">💬</div>
                <p>No messages found</p>
                <p style="font-size:13px;">Messages between agents will appear here</p>
            </div>
        `;
        return;
    }
    
    list.innerHTML = messages.map(msg => `
        <div class="message-item">
            <span class="message-type ${msg.type}">${msg.type}</span>
            <div class="message-content">
                <div class="message-sender">
                    ${escapeHtml(msg.sender || 'unknown')} → ${escapeHtml(msg.recipient || 'unknown')}
                </div>
                <div class="message-preview">
                    ${escapeHtml(JSON.stringify(msg.payload || {}))}
                </div>
            </div>
            <span class="message-time">${msg.timestamp ? formatDate(msg.timestamp) : ''}</span>
        </div>
    `).join('');
}

// ============================================================
// Contracts
// ============================================================
async function refreshContracts() {
    try {
        const api = new VireoAPI();
        const contracts = await api.getContracts();
        AppState.contracts = contracts;
        renderContracts(contracts);
        updateContractStats(contracts);
        
    } catch (error) {
        console.error('Failed to refresh contracts:', error);
        renderContracts([]);
    }
}

function renderContracts(contracts) {
    const list = document.getElementById('contractList');
    
    if (!contracts || contracts.length === 0) {
        list.innerHTML = `
            <div class="contract-empty">
                <div style="font-size:48px;margin-bottom:16px;">📄</div>
                <p>No contracts found</p>
                <p style="font-size:13px;">Create a contract to formalize agreements between agents</p>
            </div>
        `;
        return;
    }
    
    list.innerHTML = contracts.map(contract => `
        <div class="contract-item">
            <span class="contract-id">${escapeHtml(contract.contract_id || 'N/A')}</span>
            <span class="contract-status-badge ${contract.status || 'pending'}">${contract.status || 'pending'}</span>
            <div class="contract-info">
                <div class="contract-parties">
                    ${(contract.parties || []).join(' → ')}
                </div>
                <div class="contract-terms">
                    ${escapeHtml(JSON.stringify(contract.terms || {}))}
                </div>
            </div>
            <div class="contract-expiry">
                ${contract.expires_at ? `Expires: ${formatDate(contract.expires_at)}` : ''}
            </div>
            ${contract.status === 'pending' ? `
                <button class="btn btn-sm btn-success" onclick="signContract('${contract.contract_id}')">Sign</button>
            ` : ''}
        </div>
    `).join('');
}

function updateContractStats(contracts) {
    const total = contracts ? contracts.length : 0;
    const active = contracts ? contracts.filter(c => c.status === 'active').length : 0;
    const pending = contracts ? contracts.filter(c => c.status === 'pending').length : 0;
    const completed = contracts ? contracts.filter(c => c.status === 'completed').length : 0;
    
    document.getElementById('contractTotal').textContent = total;
    document.getElementById('contractActive').textContent = active;
    document.getElementById('contractPending').textContent = pending;
    document.getElementById('contractCompleted').textContent = completed;
}

async function signContract(contractId) {
    try {
        const api = new VireoAPI();
        await api.signContract(contractId);
        showToast('Contract signed successfully', 'success');
        refreshContracts();
    } catch (error) {
        showToast(`Failed to sign contract: ${error.message}`, 'error');
    }
}

// ============================================================
// Modals
// ============================================================
function openModal(title, content, confirmText = 'Confirm', onConfirm = null) {
    const overlay = document.getElementById('modalOverlay');
    const modal = document.getElementById('modal');
    const titleEl = document.getElementById('modalTitle');
    const bodyEl = document.getElementById('modalBody');
    const footerEl = document.getElementById('modalFooter');
    const confirmBtn = document.getElementById('modalConfirm');
    const cancelBtn = document.getElementById('modalCancel');
    const closeBtn = document.getElementById('modalClose');
    
    titleEl.textContent = title;
    bodyEl.innerHTML = content;
    confirmBtn.textContent = confirmText;
    
    // Show modal
    overlay.classList.add('active');
    
    // Setup handlers
    const cleanup = () => {
        overlay.classList.remove('active');
        confirmBtn.onclick = null;
        cancelBtn.onclick = null;
        closeBtn.onclick = null;
        overlay.onclick = null;
    };
    
    confirmBtn.onclick = () => {
        if (onConfirm) {
            onConfirm();
        }
        cleanup();
    };
    
    cancelBtn.onclick = cleanup;
    closeBtn.onclick = cleanup;
    overlay.onclick = (e) => {
        if (e.target === overlay) cleanup();
    };
}

function openCreateAgentModal() {
    const content = `
        <div class="settings-item">
            <label>Agent Name</label>
            <input type="text" id="agentNameInput" placeholder="MyAgent" value="Agent_${Date.now().toString(36)}">
        </div>
        <div class="settings-item">
            <label>Version</label>
            <input type="text" id="agentVersionInput" placeholder="1.0.0" value="1.0.0">
        </div>
        <div class="settings-item">
            <label>Capabilities</label>
            <input type="text" id="agentCapabilitiesInput" placeholder="text-generation, code-analysis" value="text-generation">
        </div>
        <div class="settings-item">
            <label>Description</label>
            <input type="text" id="agentDescInput" placeholder="My AI agent" value="Created via Web UI">
        </div>
    `;
    
    openModal('Create New Agent', content, 'Create', async () => {
        const name = document.getElementById('agentNameInput').value.trim();
        const version = document.getElementById('agentVersionInput').value.trim();
        const capabilities = document.getElementById('agentCapabilitiesInput').value.split(',').map(s => s.trim()).filter(Boolean);
        const description = document.getElementById('agentDescInput').value.trim();
        
        if (!name) {
            showToast('Agent name is required', 'error');
            return;
        }
        
        try {
            const api = new VireoAPI();
            await api.createAgent({ name, version, capabilities, description });
            showToast('Agent created successfully', 'success');
            refreshAgents();
        } catch (error) {
            showToast(`Failed to create agent: ${error.message}`, 'error');
        }
    });
}

function openCreateContractModal() {
    const content = `
        <div class="settings-item">
            <label>Parties (comma-separated agent IDs)</label>
            <input type="text" id="contractPartiesInput" placeholder="agent_abc, agent_def">
        </div>
        <div class="settings-item">
            <label>Terms (JSON)</label>
            <textarea id="contractTermsInput" rows="4" style="width:100%;padding:8px 12px;border:2px solid var(--border-color);border-radius:var(--radius-sm);background:var(--bg-primary);color:var(--text-primary);font-family:monospace;font-size:13px;">{"price": 100, "deadline": "2024-12-31"}</textarea>
        </div>
        <div class="settings-item">
            <label>Duration (days)</label>
            <input type="number" id="contractDurationInput" value="30" min="1" max="365">
        </div>
    `;
    
    openModal('Create New Contract', content, 'Create', async () => {
        const partiesStr = document.getElementById('contractPartiesInput').value.trim();
        const termsStr = document.getElementById('contractTermsInput').value.trim();
        const duration = parseInt(document.getElementById('contractDurationInput').value);
        
        if (!partiesStr) {
            showToast('At least one party is required', 'error');
            return;
        }
        
        let terms;
        try {
            terms = JSON.parse(termsStr);
        } catch (e) {
            showToast('Invalid JSON in terms', 'error');
            return;
        }
        
        const parties = partiesStr.split(',').map(s => s.trim()).filter(Boolean);
        
        try {
            const api = new VireoAPI();
            await api.createContract({ terms, parties, duration_days: duration });
            showToast('Contract created successfully', 'success');
            refreshContracts();
        } catch (error) {
            showToast(`Failed to create contract: ${error.message}`, 'error');
        }
    });
}

// ============================================================
// Settings
// ============================================================
function saveSettings() {
    const apiUrl = document.getElementById('apiUrl').value.trim();
    const wsUrl = document.getElementById('wsUrl').value.trim();
    const apiKey = document.getElementById('apiKey').value.trim();
    const jwtToken = document.getElementById('jwtToken').value.trim();
    const autoRefresh = document.getElementById('autoRefresh').checked;
    const theme = document.getElementById('themeSelect').value;
    
    AppState.settings.apiUrl = apiUrl;
    AppState.settings.wsUrl = wsUrl;
    AppState.settings.apiKey = apiKey;
    AppState.settings.jwtToken = jwtToken;
    AppState.settings.autoRefresh = autoRefresh;
    AppState.settings.theme = theme;
    
    localStorage.setItem('vireo_api_url', apiUrl);
    localStorage.setItem('vireo_ws_url', wsUrl);
    localStorage.setItem('vireo_api_key', apiKey);
    localStorage.setItem('vireo_jwt_token', jwtToken);
    localStorage.setItem('vireo_auto_refresh', String(autoRefresh));
    localStorage.setItem('vireo_theme', theme);
    
    applyTheme(theme);
    
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
    } else {
        document.documentElement.setAttribute('data-theme', theme);
    }
}

// ============================================================
// Initialization
// ============================================================
const api = new VireoAPI();
const wsClient = new VireoWS();

function init() {
    // Apply theme
    applyTheme(AppState.settings.theme);
    
    // Load settings into UI
    document.getElementById('apiUrl').value = AppState.settings.apiUrl;
    document.getElementById('wsUrl').value = AppState.settings.wsUrl;
    document.getElementById('apiKey').value = AppState.settings.apiKey;
    document.getElementById('jwtToken').value = AppState.settings.jwtToken;
    document.getElementById('autoRefresh').checked = AppState.settings.autoRefresh;
    document.getElementById('themeSelect').value = AppState.settings.theme;
    
    // Setup navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            if (page) {
                navigateTo(page);
            }
        });
    });
    
    // Setup connect button
    document.getElementById('connectBtn').addEventListener('click', () => {
        if (AppState.connected) {
            wsClient.disconnect();
        } else {
            wsClient.connect();
        }
    });
    
    // Setup filter events
    document.getElementById('agentSearch').addEventListener('input', refreshAgents);
    document.getElementById('agentStatusFilter').addEventListener('change', refreshAgents);
    document.getElementById('agentCapabilityFilter').addEventListener('change', refreshAgents);
    document.getElementById('messageSearch').addEventListener('input', refreshMessages);
    document.getElementById('messageTypeFilter').addEventListener('change', refreshMessages);
    
    // Setup chart buttons
    document.querySelectorAll('.chart-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.chart-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            updateChart();
        });
    });
    
    // Setup create buttons
    document.getElementById('createAgentBtn').addEventListener('click', openCreateAgentModal);
    document.getElementById('createContractBtn').addEventListener('click', openCreateContractModal);
    document.getElementById('clearMessagesBtn').addEventListener('click', () => {
        document.getElementById('messageList').innerHTML = `
            <div class="message-empty">
                <div style="font-size:48px;margin-bottom:16px;">🧹</div>
                <p>Messages cleared</p>
            </div>
        `;
        showToast('Messages cleared', 'info');
    });
    
    // Setup settings save
    document.getElementById('saveAuthBtn').addEventListener('click', saveSettings);
    
    // Setup show/hide password
    document.getElementById('showApiKeyBtn').addEventListener('click', () => {
        const input = document.getElementById('apiKey');
        input.type = input.type === 'password' ? 'text' : 'password';
    });
    document.getElementById('showJwtBtn').addEventListener('click', () => {
        const input = document.getElementById('jwtToken');
        input.type = input.type === 'password' ? 'text' : 'password';
    });
    
    // WebSocket events
    wsClient.on('connected', () => {
        AppState.connected = true;
        refreshDashboard();
    });
    
    wsClient.on('disconnected', () => {
        AppState.connected = false;
    });
    
    wsClient.on('message_received', (data) => {
        AppState.stats.messageCount++;
        document.getElementById('messageCount').textContent = AppState.stats.messageCount;
    });
    
    // Auto-refresh
    if (AppState.settings.autoRefresh) {
        AppState.refreshInterval = setInterval(() => {
            if (AppState.connected) {
                switch (AppState.currentPage) {
                    case 'dashboard':
                        refreshDashboard();
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
                }
            }
        }, 5000);
    }
    
    // Uptime
    AppState.uptimeInterval = setInterval(() => {
        const uptime = (Date.now() - AppState.startTime) / 1000;
        document.getElementById('uptimeDisplay').textContent = formatTime(uptime);
        AppState.stats.uptime = uptime;
    }, 1000);
    
    // Auto-connect
    setTimeout(() => {
        if (AppState.settings.apiKey || AppState.settings.jwtToken) {
            wsClient.connect();
        }
    }, 500);
    
    // Initial load
    navigateTo('dashboard');
    
    console.log('🌿 Vireo v3.0.0 Web Interface initialized');
}

// Init when DOM ready
document.addEventListener('DOMContentLoaded', init);