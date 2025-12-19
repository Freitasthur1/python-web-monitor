#!/usr/bin/env python3
"""
Script Administrativo para Controle do Monitor de Editais
USO EXCLUSIVO DO ADMINISTRADOR VIA SSH
"""

import sys
import os
import json

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import monitor_state, load_config
import threading
import uuid


def iniciar_monitoramento():
    """Inicia o monitoramento programaticamente"""
    if monitor_state['running']:
        print("ERRO: Monitor ja esta em execucao")
        return False

    # Importa a funcao de loop
    from src.app import monitor_loop

    # Gera ID unico para esta thread
    thread_id = str(uuid.uuid4())

    monitor_state['running'] = True
    monitor_state['current_check'] = 0
    monitor_state['mudancas_detectadas'] = 0
    monitor_state['palavras_encontradas'] = []
    monitor_state['thread_id'] = thread_id

    thread = threading.Thread(target=monitor_loop, args=(thread_id,), daemon=True)
    thread.start()
    monitor_state['thread'] = thread

    print("SUCESSO: Monitoramento iniciado")
    return True


def parar_monitoramento():
    """Para o monitoramento"""
    if not monitor_state['running']:
        print("ERRO: Monitor nao esta em execucao")
        return False

    monitor_state['running'] = False
    monitor_state['thread_id'] = None
    print("SUCESSO: Monitoramento parado")
    return True


def status_monitoramento():
    """Exibe status do monitoramento"""
    print("\n" + "="*60)
    print("STATUS DO MONITOR DE EDITAIS")
    print("="*60)
    print(f"Status: {'ATIVO' if monitor_state['running'] else 'PARADO'}")
    print(f"Verificacoes realizadas: {monitor_state['current_check']}")
    print(f"Mudancas detectadas: {monitor_state['mudancas_detectadas']}")

    if monitor_state['last_check']:
        print(f"Ultima verificacao: {monitor_state['last_check']}")

    if monitor_state['next_check']:
        print(f"Proxima verificacao: {monitor_state['next_check']}")

    config = load_config()
    print(f"\nURL monitorada: {config['url']}")
    print(f"Intervalo: {config['intervalo_minutos']} minutos")
    print(f"Email ativo: {'SIM' if config.get('email', {}).get('enabled') else 'NAO'}")
    print("="*60 + "\n")


def main():
    """Funcao principal"""
    if len(sys.argv) < 2:
        print("\nUSO: python3 admin_control.py [comando]")
        print("\nComandos disponiveis:")
        print("  start   - Inicia o monitoramento")
        print("  stop    - Para o monitoramento")
        print("  status  - Exibe status atual")
        print("  restart - Reinicia o monitoramento")
        print("\nExemplos:")
        print("  python3 admin_control.py start")
        print("  python3 admin_control.py status")
        sys.exit(1)

    comando = sys.argv[1].lower()

    # Importa app para ter acesso ao estado
    from src.app import app

    with app.app_context():
        if comando == 'start':
            iniciar_monitoramento()
        elif comando == 'stop':
            parar_monitoramento()
        elif comando == 'status':
            status_monitoramento()
        elif comando == 'restart':
            print("Parando monitoramento...")
            parar_monitoramento()
            import time
            time.sleep(2)
            print("Iniciando monitoramento...")
            iniciar_monitoramento()
        else:
            print(f"ERRO: Comando desconhecido: {comando}")
            sys.exit(1)


if __name__ == '__main__':
    main()
