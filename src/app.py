#!/usr/bin/env python3
"""
Aplicação Web para Monitoramento de Editais
Servidor Flask com interface web e API REST
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import json
import os
import sys
from datetime import datetime
from typing import List, Dict
import time

# Adiciona o diretório pai ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.monitor import MonitorEdital
from src.email_notifier import EmailNotifier

# Configuração de paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
DATA_DIR = os.path.join(BASE_DIR, 'data')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Cria diretórios se não existirem
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__,
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR)
CORS(app)

# Configurações
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
SUBSCRIBERS_FILE = os.path.join(DATA_DIR, 'subscribers.json')
LOGS_MAX = 100

# Estado global do monitor
monitor_state = {
    'running': False,
    'logs': [],
    'current_check': 0,
    'last_check': None,
    'next_check': None,
    'palavras_encontradas': [],
    'mudancas_detectadas': 0,
    'thread': None,
    'thread_id': None,  # ID único da thread ativa
    'monitor': None,
    'email_notifier': None
}


def load_config() -> Dict:
    """Carrega configuração do arquivo JSON"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Configuração padrão
    default_config = {
        'url': 'https://exemplo.com/edital',
        'palavras_chave': [
            'Resultado',
            'Homologação',
            'Classificados'
        ],
        'intervalo_minutos': 10,
        'servidor_host': '0.0.0.0',
        'servidor_porta': 5000,
        'email': {
            'enabled': False,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_user': '',
            'smtp_password': '',
            'from_email': '',
            'to_email': '',
            'use_tls': True
        }
    }
    save_config(default_config)
    return default_config


def save_config(config: Dict):
    """Salva configuração no arquivo JSON"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def load_subscribers() -> List[str]:
    """Carrega lista de emails inscritos"""
    if os.path.exists(SUBSCRIBERS_FILE):
        try:
            with open(SUBSCRIBERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('emails', [])
        except Exception as e:
            print(f"Erro ao carregar subscribers: {e}", flush=True)
            return []

    # Se não existe, cria arquivo vazio
    save_subscribers([])
    return []


def save_subscribers(emails: List[str]):
    """Salva lista de emails inscritos"""
    with open(SUBSCRIBERS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'emails': emails}, f, indent=4, ensure_ascii=False)


def add_subscriber(email: str) -> bool:
    """Adiciona um email à lista de inscritos"""
    if not email or '@' not in email:
        return False

    emails = load_subscribers()
    email_lower = email.lower().strip()

    if email_lower not in [e.lower() for e in emails]:
        emails.append(email_lower)
        save_subscribers(emails)
        add_log(f"Novo inscrito: {email_lower}", "INFO")
        return True
    return False


def remove_subscriber(email: str) -> bool:
    """Remove um email da lista de inscritos"""
    emails = load_subscribers()
    email_lower = email.lower().strip()

    emails_filtered = [e for e in emails if e.lower() != email_lower]

    if len(emails_filtered) < len(emails):
        save_subscribers(emails_filtered)
        add_log(f"Inscrito removido: {email_lower}", "INFO")
        return True
    return False


def add_log(mensagem: str, tipo: str = "INFO"):
    """Adiciona log ao estado global"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'tipo': tipo,
        'mensagem': mensagem
    }

    monitor_state['logs'].insert(0, log_entry)

    if len(monitor_state['logs']) > LOGS_MAX:
        monitor_state['logs'] = monitor_state['logs'][:LOGS_MAX]

    # Força flush para garantir que logs apareçam imediatamente
    print(f"[{timestamp}] [{tipo}] {mensagem}", flush=True)


def iniciar_monitoramento():
    """Inicia o monitoramento (uso interno)"""
    import uuid

    if monitor_state['running']:
        add_log("Monitor já está em execução", "ALERTA")
        return False

    # Gera ID único para esta thread
    thread_id = str(uuid.uuid4())

    monitor_state['running'] = True
    monitor_state['current_check'] = 0
    monitor_state['mudancas_detectadas'] = 0
    monitor_state['palavras_encontradas'] = []
    monitor_state['thread_id'] = thread_id

    thread = threading.Thread(target=monitor_loop, args=(thread_id,), daemon=True)
    thread.start()
    monitor_state['thread'] = thread

    add_log("Sistema de monitoramento pronto", "INFO")
    return True


def parar_monitoramento():
    """Para o monitoramento (uso interno)"""
    if not monitor_state['running']:
        add_log("Monitor não está em execução", "ALERTA")
        return False

    monitor_state['running'] = False
    monitor_state['thread_id'] = None
    add_log("Monitoramento parado", "ALERTA")
    return True


def iniciar_monitoramento_automatico():
    """Inicia o monitoramento automaticamente ao startar a aplicação"""
    # Aguarda 2 segundos para garantir que o Flask está completamente iniciado
    time.sleep(2)
    iniciar_monitoramento()


def monitor_loop(thread_id):
    """Loop principal de monitoramento"""
    config = load_config()

    url = config['url']
    palavras_chave = config['palavras_chave']
    intervalo_minutos = config['intervalo_minutos']
    intervalo_segundos = intervalo_minutos * 60

    # Inicializa monitor
    monitor_state['monitor'] = MonitorEdital(url, palavras_chave, intervalo_minutos)

    # Inicializa notificador de email
    if config.get('email', {}).get('enabled', False):
        monitor_state['email_notifier'] = EmailNotifier(config['email'])
        add_log("Sistema de notificação por email ativado", "INFO")

    add_log("Monitoramento iniciado", "SUCESSO")
    add_log(f"URL: {url}", "INFO")
    add_log(f"Intervalo: {intervalo_minutos} minutos", "INFO")

    while monitor_state['running'] and monitor_state['thread_id'] == thread_id:
        try:
            monitor_state['current_check'] += 1
            check_num = monitor_state['current_check']

            add_log(f"Verificação #{check_num}", "INFO")
            monitor_state['last_check'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Busca e processa página
            monitor = monitor_state['monitor']
            soup = monitor.buscar_pagina()
            conteudo = monitor.extrair_conteudo_relevante(soup)

            # Verifica palavras-chave
            palavras_encontradas = monitor.verificar_palavras_chave(conteudo)

            # Verifica mudanças
            mudanca_conteudo, _ = monitor.verificar_mudancas(conteudo)

            # Atualiza estado com palavras encontradas (para dashboard)
            monitor_state['palavras_encontradas'] = palavras_encontradas

            # Registra palavras-chave encontradas (apenas informativo)
            if palavras_encontradas:
                add_log(f"Palavras-chave no site: {', '.join(palavras_encontradas)}", "INFO")

            # IMPORTANTE: Só envia notificação quando houver MUDANÇA REAL no conteúdo
            if mudanca_conteudo:
                monitor_state['mudancas_detectadas'] += 1
                add_log("MUDANÇA NO CONTEÚDO DETECTADA!", "ALERTA")

                # Envia notificação por email APENAS quando há mudança
                if monitor_state['email_notifier']:
                    # Carrega lista de emails inscritos
                    subscribers = load_subscribers()

                    if subscribers:
                        # Envia para todos os inscritos
                        if monitor_state['email_notifier'].enviar_alerta(
                            url, palavras_encontradas, mudanca_conteudo, destinatarios=subscribers
                        ):
                            add_log(f"Notificação enviada para {len(subscribers)} inscrito(s)", "SUCESSO")
                        else:
                            add_log("Falha ao enviar notificações", "ERRO")
                    else:
                        add_log("Mudança detectada mas nenhum email inscrito para notificar", "ALERTA")
            else:
                add_log("Nenhuma mudança detectada - site sem alterações", "INFO")

            # Calcula próxima verificação
            proxima = datetime.now().timestamp() + intervalo_segundos
            monitor_state['next_check'] = datetime.fromtimestamp(proxima).strftime("%Y-%m-%d %H:%M:%S")

            add_log(f"Próxima verificação: {monitor_state['next_check']}", "INFO")

            # Aguarda intervalo - verifica thread_id a cada segundo para responder rapidamente ao stop
            for _ in range(intervalo_segundos):
                if monitor_state['thread_id'] != thread_id:
                    add_log("Thread de monitoramento substituída, encerrando esta thread", "INFO")
                    return
                time.sleep(1)

        except Exception as e:
            add_log(f"Erro: {str(e)}", "ERRO")

            # Calcula próxima verificação mesmo em caso de erro
            proxima = datetime.now().timestamp() + intervalo_segundos
            monitor_state['next_check'] = datetime.fromtimestamp(proxima).strftime("%Y-%m-%d %H:%M:%S")
            add_log(f"Próxima tentativa: {monitor_state['next_check']}", "INFO")

            # Aguarda intervalo completo em caso de erro para não sobrecarregar o servidor
            for _ in range(intervalo_segundos):
                if monitor_state['thread_id'] != thread_id:
                    add_log("Thread de monitoramento substituída, encerrando esta thread", "INFO")
                    return
                time.sleep(1)

    add_log("Monitoramento interrompido", "ALERTA")


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Retorna status atual do monitor"""
    return jsonify({
        'running': monitor_state['running'],
        'current_check': monitor_state['current_check'],
        'last_check': monitor_state['last_check'],
        'next_check': monitor_state['next_check'],
        'palavras_encontradas': monitor_state['palavras_encontradas'],
        'mudancas_detectadas': monitor_state['mudancas_detectadas']
    })


@app.route('/api/logs')
def get_logs():
    """Retorna logs recentes"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify({'logs': monitor_state['logs'][:limit]})


@app.route('/api/config', methods=['GET'])
def get_config():
    """Retorna configuração atual"""
    config = load_config()
    # Remove senha do SMTP antes de enviar
    if 'email' in config and 'smtp_password' in config['email']:
        config_copy = config.copy()
        config_copy['email'] = config['email'].copy()
        config_copy['email']['smtp_password'] = '***' if config['email']['smtp_password'] else ''
        return jsonify(config_copy)
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
def update_config():
    """Atualiza configuração - DESABILITADO PARA SEGURANCA"""
    return jsonify({'error': 'Acesso negado. Esta operacao requer privilegios de administrador.'}), 403


@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Testa configuração de email - DESABILITADO PARA SEGURANCA"""
    return jsonify({'error': 'Acesso negado. Esta operacao requer privilegios de administrador.'}), 403


@app.route('/api/start', methods=['POST'])
def start_monitor():
    """Inicia monitoramento - DESABILITADO PARA SEGURANCA"""
    return jsonify({'error': 'Acesso negado. Esta operacao requer privilegios de administrador.'}), 403


@app.route('/api/stop', methods=['POST'])
def stop_monitor():
    """Para monitoramento - DESABILITADO PARA SEGURANCA"""
    return jsonify({'error': 'Acesso negado. Esta operacao requer privilegios de administrador.'}), 403


@app.route('/api/clear-logs', methods=['POST'])
def clear_logs():
    """Limpa logs - DESABILITADO PARA SEGURANCA"""
    return jsonify({'error': 'Acesso negado. Esta operacao requer privilegios de administrador.'}), 403


@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    """Retorna apenas a contagem de emails inscritos (sem revelar os emails)"""
    subscribers = load_subscribers()
    return jsonify({
        'count': len(subscribers)
    })


@app.route('/api/subscribers', methods=['POST'])
def add_subscriber_endpoint():
    """Adiciona um email à lista de inscritos"""
    try:
        data = request.json
        email = data.get('email', '').strip()

        if not email:
            return jsonify({'error': 'Email não fornecido'}), 400

        if '@' not in email:
            return jsonify({'error': 'Email inválido'}), 400

        if add_subscriber(email):
            subscribers_count = len(load_subscribers())
            return jsonify({
                'message': 'Email cadastrado com sucesso!',
                'email': email,
                'total_subscribers': subscribers_count
            })
        else:
            return jsonify({'error': 'Este email já está cadastrado'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/subscribers/<email>', methods=['DELETE'])
def remove_subscriber_endpoint(email):
    """Remove um email da lista de inscritos - DESABILITADO PARA SEGURANCA"""
    return jsonify({'error': 'Acesso negado. Esta operacao requer privilegios de administrador.'}), 403


@app.route('/api/check-now', methods=['POST'])
def check_now():
    """Força uma verificação imediata - DESABILITADO PARA SEGURANCA"""
    return jsonify({'error': 'Acesso negado. Esta operacao requer privilegios de administrador.'}), 403


@app.route('/api/diagnostic', methods=['GET'])
def diagnostic():
    """Retorna informações de diagnóstico - DESABILITADO PARA SEGURANCA"""
    return jsonify({'error': 'Acesso negado. Esta operacao requer privilegios de administrador.'}), 403


@app.route('/api/reset-hash', methods=['POST'])
def reset_hash():
    """Reseta o hash anterior - DESABILITADO PARA SEGURANCA"""
    return jsonify({'error': 'Acesso negado. Esta operacao requer privilegios de administrador.'}), 403


if __name__ == '__main__':
    config = load_config()

    print("=" * 80)
    print("Monitor de Editais - Servidor Web v2.0")
    print("=" * 80)
    print(f"Acesse: http://{config['servidor_host']}:{config['servidor_porta']}")
    print(f"Ou: http://localhost:{config['servidor_porta']}")
    print("=" * 80)

    app.run(
        host=config['servidor_host'],
        port=config['servidor_porta'],
        debug=False,
        threaded=True
    )
