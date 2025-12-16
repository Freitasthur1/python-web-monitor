// ===================================
// Monitor de Edital - Asas para Todos
// JavaScript Application
// ===================================

// Global variables
let updateInterval = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    loadUserPreferences();
    loadSubscribers();
    updateStatus();
    updateLogs();

    // Update status every 2 seconds
    updateInterval = setInterval(() => {
        updateStatus();
        updateLogs();
    }, 2000);
});

// Show view
function showView(viewName) {
    // Remove active class from all views
    document.querySelectorAll('.content-view').forEach(view => {
        view.classList.remove('active');
    });

    // Remove active class from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Add active class to selected view
    const view = document.getElementById(`view-${viewName}`);
    if (view) {
        view.classList.add('active');
    }

    // Add active class to selected nav button
    const navBtn = document.querySelector(`[data-view="${viewName}"]`);
    if (navBtn) {
        navBtn.classList.add('active');
    }
}

// Load user preferences from localStorage
function loadUserPreferences() {
    const darkMode = localStorage.getItem('darkMode') === 'true';
    const autoRefresh = localStorage.getItem('autoRefresh') !== 'false'; // default true
    const soundNotifications = localStorage.getItem('soundNotifications') === 'true';

    document.getElementById('darkModeToggle').checked = darkMode;
    document.getElementById('autoRefreshToggle').checked = autoRefresh;
    document.getElementById('soundNotificationsToggle').checked = soundNotifications;

    // Apply dark mode if enabled
    if (darkMode) {
        document.body.classList.add('dark-mode');
    }
}

// Save user preferences
function saveConfig(event) {
    event.preventDefault();

    const darkMode = document.getElementById('darkModeToggle').checked;
    const autoRefresh = document.getElementById('autoRefreshToggle').checked;
    const soundNotifications = document.getElementById('soundNotificationsToggle').checked;

    // Save to localStorage
    localStorage.setItem('darkMode', darkMode);
    localStorage.setItem('autoRefresh', autoRefresh);
    localStorage.setItem('soundNotifications', soundNotifications);

    showNotification('Preferências salvas com sucesso!', 'success');
}

// Toggle dark mode
function toggleDarkMode() {
    const darkMode = document.getElementById('darkModeToggle').checked;

    if (darkMode) {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }

    localStorage.setItem('darkMode', darkMode);
}

// Load subscribers
async function loadSubscribers() {
    try {
        const response = await fetch('/api/subscribers');
        const data = await response.json();

        const count = data.count || 0;
        const subscribers = data.subscribers || [];

        document.getElementById('subscriberCount').textContent = count;

        const listContainer = document.getElementById('subscribersList');

        if (subscribers.length === 0) {
            listContainer.innerHTML = '<p style="text-align: center; color: var(--gray-600, #718096); padding: 20px;">Nenhum email inscrito ainda</p>';
        } else {
            let html = '<div style="display: flex; flex-direction: column; gap: 10px;">';
            subscribers.forEach(email => {
                html += `
                    <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px; background: var(--gray-50, #f7fafc); border-radius: 6px; border: 1px solid var(--gray-200, #e2e8f0);">
                        <span style="font-size: 14px; color: var(--gray-700, #4a5568);">${escapeHtml(email)}</span>
                        <button onclick="unsubscribeEmail('${escapeHtml(email)}')" style="padding: 6px 12px; background: var(--accent-alert, #ef4444); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
                            Remover
                        </button>
                    </div>
                `;
            });
            html += '</div>';
            listContainer.innerHTML = html;
        }
    } catch (error) {
        console.error('Erro ao carregar inscritos:', error);
    }
}

// Subscribe email
async function subscribeEmail(event) {
    event.preventDefault();

    const emailInput = document.getElementById('subscribeEmailInput');
    const email = emailInput.value.trim();

    if (!email) {
        showNotification('Por favor, digite um email', 'error');
        return;
    }

    try {
        const response = await fetch('/api/subscribers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Email cadastrado com sucesso! Você receberá alertas quando houver mudanças.', 'success');
            emailInput.value = '';
            loadSubscribers();
        } else {
            showNotification(data.error || 'Erro ao cadastrar email', 'error');
        }
    } catch (error) {
        console.error('Erro ao cadastrar email:', error);
        showNotification('Erro ao cadastrar email', 'error');
    }
}

// Unsubscribe email
async function unsubscribeEmail(email) {
    if (!confirm(`Tem certeza que deseja remover ${email} da lista?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/subscribers/${encodeURIComponent(email)}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showNotification('Email removido com sucesso', 'success');
            loadSubscribers();
        } else {
            const data = await response.json();
            showNotification(data.error || 'Erro ao remover email', 'error');
        }
    } catch (error) {
        console.error('Erro ao remover email:', error);
        showNotification('Erro ao remover email', 'error');
    }
}

// Test email notifications
async function testEmailNotifications() {
    if (!confirm('Enviar email de teste para todos os inscritos?')) {
        return;
    }

    try {
        const response = await fetch('/api/test-email', {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(`${data.message}\nVerifique a caixa de entrada dos emails cadastrados.`, 'success');
        } else {
            showNotification(data.error || 'Erro ao enviar email de teste', 'error');
        }
    } catch (error) {
        console.error('Erro ao testar email:', error);
        showNotification('Erro ao testar email', 'error');
    }
}

// Update status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        // Update header status
        const headerPulse = document.querySelector('#headerStatus .status-pulse');
        const headerText = document.querySelector('#headerStatus .status-text');

        if (status.running) {
            headerPulse.classList.add('active');
            headerText.textContent = 'Sistema Ativo';

            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
        } else {
            headerPulse.classList.remove('active');
            headerText.textContent = 'Sistema Parado';

            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        }

        // Update dashboard cards
        document.getElementById('totalChecks').textContent = status.current_check;
        document.getElementById('totalChanges').textContent = status.mudancas_detectadas;

        if (status.last_check) {
            document.getElementById('lastCheckTime').textContent = status.last_check;
        }

        if (status.next_check) {
            document.getElementById('nextCheckTime').textContent = status.next_check;
        }

    } catch (error) {
        console.error('Erro ao atualizar status:', error);
    }
}

// Update logs
async function updateLogs() {
    try {
        const response = await fetch('/api/logs?limit=50');
        const data = await response.json();

        const logsContainer = document.getElementById('logsContainer');

        if (data.logs.length === 0) {
            logsContainer.innerHTML = `
                <div class="logs-empty">
                    <p>Nenhum log disponível</p>
                    <small>Os logs aparecerão aqui quando o monitoramento iniciar</small>
                </div>
            `;
            return;
        }

        let html = '';
        data.logs.forEach(log => {
            html += `
                <div class="log-entry ${log.tipo}">
                    <span class="log-timestamp">${log.timestamp}</span>
                    <span class="log-type ${log.tipo}">[${log.tipo}]</span>
                    <span class="log-message">${escapeHtml(log.mensagem)}</span>
                </div>
            `;
        });

        logsContainer.innerHTML = html;

    } catch (error) {
        console.error('Erro ao atualizar logs:', error);
    }
}

// Start monitoring
async function startMonitor() {
    try {
        const response = await fetch('/api/start', { method: 'POST' });

        if (response.ok) {
            showNotification('Monitoramento iniciado com sucesso!', 'success');
            setTimeout(() => {
                updateStatus();
                updateLogs();
            }, 500);
        } else {
            const error = await response.json();
            showNotification('Erro: ' + error.error, 'error');
        }
    } catch (error) {
        console.error('Erro ao iniciar monitoramento:', error);
        showNotification('Erro ao iniciar monitoramento', 'error');
    }
}

// Stop monitoring
async function stopMonitor() {
    try {
        const response = await fetch('/api/stop', { method: 'POST' });

        if (response.ok) {
            showNotification('Monitoramento parado com sucesso', 'success');
            setTimeout(() => {
                updateStatus();
                updateLogs();
            }, 500);
        } else {
            const error = await response.json();
            showNotification('Erro: ' + error.error, 'error');
        }
    } catch (error) {
        console.error('Erro ao parar monitoramento:', error);
        showNotification('Erro ao parar monitoramento', 'error');
    }
}

// Clear logs
async function clearLogs() {
    if (!confirm('Deseja limpar todos os logs?')) {
        return;
    }

    try {
        const response = await fetch('/api/clear-logs', { method: 'POST' });

        if (response.ok) {
            showNotification('Logs limpos com sucesso', 'success');
            updateLogs();
        } else {
            showNotification('Erro ao limpar logs', 'error');
        }
    } catch (error) {
        console.error('Erro ao limpar logs:', error);
        showNotification('Erro ao limpar logs', 'error');
    }
}

// Show notification
function showNotification(message, type) {
    console.log(`[${type.toUpperCase()}] ${message}`);

    // Simple alert - can be replaced with toast library
    if (type === 'success') {
        alert(message);
    } else if (type === 'error') {
        alert('Erro: ' + message);
    }
}

// Escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Cleanup on exit
window.addEventListener('beforeunload', function() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
