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
        except:
            return []
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
            # Aguarda 60 segundos em caso de erro, verificando thread_id
            for _ in range(60):
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
    """Atualiza configuração"""
    try:
        new_config = request.json
        old_config = load_config()

        # IMPORTANTE: Proteção contra alterações não autorizadas
        # Apenas desenvolvedores podem alterar estas configurações editando o arquivo diretamente

        # 1. URL é fixa
        new_config['url'] = old_config.get('url', 'https://fgduque.org.br/edital/projeto-asas-para-todos-ufersa-fgd-anac-edital-18-2024-1718822792')

        # 2. Palavras-chave são fixas
        new_config['palavras_chave'] = old_config.get('palavras_chave', ['Resultado', 'Homologação', 'Classificados'])

        # 3. Intervalo de monitoramento é fixo
        new_config['intervalo_minutos'] = old_config.get('intervalo_minutos', 10)

        # 4. Configurações de servidor são fixas
        new_config['servidor_host'] = old_config.get('servidor_host', '0.0.0.0')
        new_config['servidor_porta'] = old_config.get('servidor_porta', 5000)

        # Se a senha do SMTP for '***', mantém a senha atual
        if 'email' in new_config and new_config['email'].get('smtp_password') == '***':
            if 'email' in old_config:
                new_config['email']['smtp_password'] = old_config['email'].get('smtp_password', '')

        save_config(new_config)
        add_log("Configuração de email atualizada", "SUCESSO")

        return jsonify({'message': 'Configuração atualizada com sucesso'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Testa configuração de email enviando para todos os inscritos"""
    try:
        config = load_config()
        if not config.get('email', {}).get('enabled', False):
            return jsonify({'error': 'Notificações por email desabilitadas'}), 400

        # Carrega lista de inscritos
        subscribers = load_subscribers()
        if not subscribers:
            return jsonify({'error': 'Nenhum email inscrito para testar'}), 400

        notifier = EmailNotifier(config['email'])
        sucesso, mensagem = notifier.testar_conexao()

        if sucesso:
            # Envia email de teste para todos os inscritos
            if notifier.enviar_alerta(
                url=config.get('url', 'https://fgduque.org.br/edital/projeto-asas-para-todos-ufersa-fgd-anac-edital-18-2024-1718822792'),
                palavras_encontradas=["Teste de Notificação"],
                mudanca_conteudo=True,
                destinatarios=subscribers
            ):
                add_log(f"Email de teste enviado para {len(subscribers)} inscrito(s)", "SUCESSO")
                return jsonify({
                    'message': f'Email de teste enviado com sucesso para {len(subscribers)} inscrito(s)!',
                    'count': len(subscribers),
                    'subscribers': subscribers
                })
            else:
                return jsonify({'error': 'Falha ao enviar emails de teste'}), 500
        else:
            return jsonify({'error': mensagem}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/start', methods=['POST'])
def start_monitor():
    """Inicia monitoramento"""
    if monitor_state['running']:
        return jsonify({'error': 'Monitor já está em execução'}), 400

    # Gera ID único para esta thread
    import uuid
    thread_id = str(uuid.uuid4())

    monitor_state['running'] = True
    monitor_state['current_check'] = 0
    monitor_state['mudancas_detectadas'] = 0
    monitor_state['palavras_encontradas'] = []
    monitor_state['thread_id'] = thread_id

    thread = threading.Thread(target=monitor_loop, args=(thread_id,), daemon=True)
    thread.start()
    monitor_state['thread'] = thread

    return jsonify({'message': 'Monitoramento iniciado'})


@app.route('/api/stop', methods=['POST'])
def stop_monitor():
    """Para monitoramento"""
    if not monitor_state['running']:
        return jsonify({'error': 'Monitor não está em execução'}), 400

    monitor_state['running'] = False
    monitor_state['thread_id'] = None  # Invalida o ID da thread
    return jsonify({'message': 'Monitoramento parado'})


@app.route('/api/clear-logs', methods=['POST'])
def clear_logs():
    """Limpa logs"""
    monitor_state['logs'] = []
    return jsonify({'message': 'Logs limpos'})


@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    """Retorna lista de emails inscritos"""
    subscribers = load_subscribers()
    return jsonify({
        'subscribers': subscribers,
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
    """Remove um email da lista de inscritos"""
    try:
        if remove_subscriber(email):
            return jsonify({'message': 'Email removido com sucesso'})
        else:
            return jsonify({'error': 'Email não encontrado'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/check-now', methods=['POST'])
def check_now():
    """Força uma verificação imediata (apenas para testes)"""
    try:
        if not monitor_state['running']:
            return jsonify({'error': 'Monitor não está em execução'}), 400

        monitor = monitor_state['monitor']
        if not monitor:
            return jsonify({'error': 'Monitor não inicializado'}), 400

        add_log("Verificação manual iniciada", "INFO")

        # Busca e processa página
        soup = monitor.buscar_pagina()
        conteudo = monitor.extrair_conteudo_relevante(soup)

        # Verifica palavras-chave
        palavras_encontradas = monitor.verificar_palavras_chave(conteudo)

        # Verifica mudanças
        mudanca_conteudo, hash_atual = monitor.verificar_mudancas(conteudo)

        resultado = {
            'mudanca_detectada': mudanca_conteudo,
            'palavras_encontradas': palavras_encontradas,
            'hash_atual': hash_atual,
            'tamanho_conteudo': len(conteudo)
        }

        if mudanca_conteudo:
            add_log("Verificação manual: MUDANÇA DETECTADA!", "ALERTA")
        else:
            add_log("Verificação manual: Nenhuma mudança detectada - site sem alterações", "INFO")

        if palavras_encontradas:
            add_log(f"Verificação manual: Palavras-chave no site: {', '.join(palavras_encontradas)}", "INFO")

        return jsonify(resultado)

    except Exception as e:
        add_log(f"Erro na verificação manual: {str(e)}", "ERRO")
        return jsonify({'error': str(e)}), 500


@app.route('/api/diagnostic', methods=['GET'])
def diagnostic():
    """Retorna informações de diagnóstico sobre o monitoramento"""
    try:
        if not monitor_state['running']:
            return jsonify({'error': 'Monitor não está em execução. Inicie o monitoramento primeiro.'}), 400

        monitor = monitor_state['monitor']
        if not monitor:
            return jsonify({'error': 'Monitor não inicializado'}), 400

        # Busca página atual
        soup = monitor.buscar_pagina()
        conteudo = monitor.extrair_conteudo_relevante(soup)

        # Calcula hash atual (sem alterar o hash_anterior)
        hash_atual = monitor.calcular_hash(conteudo)

        # Verifica palavras-chave
        palavras_encontradas = monitor.verificar_palavras_chave(conteudo)

        # Preview do conteúdo (primeiros 500 caracteres)
        preview = conteudo[:500] + "..." if len(conteudo) > 500 else conteudo

        resultado = {
            'url': monitor.url,
            'hash_anterior': monitor.hash_anterior,
            'hash_atual': hash_atual,
            'hash_mudou': monitor.hash_anterior is not None and hash_atual != monitor.hash_anterior,
            'palavras_chave_configuradas': monitor.palavras_chave,
            'palavras_encontradas': palavras_encontradas,
            'tamanho_conteudo': len(conteudo),
            'preview_conteudo': preview,
            'intervalo_segundos': monitor.intervalo_segundos
        }

        add_log("Diagnóstico executado", "INFO")
        return jsonify(resultado)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset-hash', methods=['POST'])
def reset_hash():
    """Reseta o hash anterior - a próxima verificação detectará mudança (apenas para testes)"""
    try:
        if not monitor_state['running']:
            return jsonify({'error': 'Monitor não está em execução'}), 400

        monitor = monitor_state['monitor']
        if not monitor:
            return jsonify({'error': 'Monitor não inicializado'}), 400

        hash_anterior = monitor.hash_anterior
        monitor.hash_anterior = None

        add_log("Hash anterior resetado - próxima verificação detectará mudança", "ALERTA")

        return jsonify({
            'message': 'Hash resetado com sucesso',
            'hash_anterior': hash_anterior,
            'observacao': 'A próxima verificação detectará uma mudança mesmo que o conteúdo não tenha sido alterado'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
