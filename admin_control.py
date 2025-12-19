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

from src.app import monitor_state, load_config, iniciar_monitoramento, parar_monitoramento


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

    print("\n[AVISO] Este script nao funciona mais com o monitoramento auto-start.")
    print("O monitoramento agora inicia automaticamente quando o servico Flask e iniciado.")
    print("\nPara controlar o servico, use os comandos systemd:")
    print("  sudo systemctl start monitor-edital.service   - Inicia o servico e o monitoramento")
    print("  sudo systemctl stop monitor-edital.service    - Para o servico e o monitoramento")
    print("  sudo systemctl restart monitor-edital.service - Reinicia o servico e o monitoramento")
    print("  sudo systemctl status monitor-edital.service  - Verifica status do servico")
    print("\nPara ver logs em tempo real:")
    print("  tail -f /opt/monitoramento-ufersa/logs/service.log")
    print("  journalctl -u monitor-edital.service -f\n")

    if comando == 'status':
        status_monitoramento()


if __name__ == '__main__':
    main()
