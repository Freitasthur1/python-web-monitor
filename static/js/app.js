// ===================================
// Monitor de Edital - Asas para Todos
// JavaScript Application
// ===================================

// Global variables
let updateInterval = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    loadUserPreferences();
    loadEmailConfig();
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

// Load email configuration
async function loadEmailConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();

        if (config.email) {
            document.getElementById('emailEnabled').checked = config.email.enabled || false;
            document.getElementById('smtpServer').value = config.email.smtp_server || '';
            document.getElementById('smtpPort').value = config.email.smtp_port || 587;
            document.getElementById('smtpUser').value = config.email.smtp_user || '';
            document.getElementById('smtpPassword').value = config.email.smtp_password || '';
            document.getElementById('fromEmail').value = config.email.from_email || '';
            document.getElementById('toEmail').value = config.email.to_email || '';
            document.getElementById('useTLS').checked = config.email.use_tls !== false;

            toggleEmailFields();
        }
    } catch (error) {
        console.error('Erro ao carregar configuração de email:', error);
    }
}

// Toggle email fields
function toggleEmailFields() {
    const enabled = document.getElementById('emailEnabled').checked;
    const fields = document.getElementById('emailFields');
    const testBtn = document.getElementById('testEmailBtn');

    if (enabled) {
        fields.style.display = 'block';
        testBtn.disabled = false;
    } else {
        fields.style.display = 'none';
        testBtn.disabled = true;
    }
}

// Save email configuration
async function saveEmailConfig(event) {
    event.preventDefault();

    // Get existing config first
    const existingResponse = await fetch('/api/config');
    const existingConfig = await existingResponse.json();

    const emailConfig = {
        enabled: document.getElementById('emailEnabled').checked,
        smtp_server: document.getElementById('smtpServer').value,
        smtp_port: parseInt(document.getElementById('smtpPort').value),
        smtp_user: document.getElementById('smtpUser').value,
        smtp_password: document.getElementById('smtpPassword').value,
        from_email: document.getElementById('fromEmail').value,
        to_email: document.getElementById('toEmail').value,
        use_tls: document.getElementById('useTLS').checked
    };

    const config = {
        ...existingConfig,
        email: emailConfig
    };

    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (response.ok) {
            showNotification('Configurações de email salvas com sucesso!', 'success');
        } else {
            const error = await response.json();
            showNotification('Erro: ' + error.error, 'error');
        }
    } catch (error) {
        console.error('Erro ao salvar configuração de email:', error);
        showNotification('Erro ao salvar configuração de email', 'error');
    }
}

// Test email
async function testEmail() {
    const btn = document.getElementById('testEmailBtn');
    const originalHTML = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = 'Enviando...';

    try {
        const response = await fetch('/api/test-email', { method: 'POST' });

        if (response.ok) {
            showNotification('Email de teste enviado com sucesso! Verifique sua caixa de entrada.', 'success');
        } else {
            const error = await response.json();
            showNotification('Erro ao enviar email: ' + error.error, 'error');
        }
    } catch (error) {
        console.error('Erro ao testar email:', error);
        showNotification('Erro ao testar email', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
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
