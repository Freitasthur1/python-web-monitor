#!/usr/bin/env python3
"""
Entry Point - Monitor de Editais
Inicia a aplicação web
"""

import sys
import os
import logging

# Desabilita buffering do stdout para logs em tempo real
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import app, load_config

if __name__ == '__main__':
    # Configura logging para exibir informações do Flask
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout
    )

    # Força o Flask a usar o logger configurado
    app.logger.setLevel(logging.INFO)

    config = load_config()

    print("=" * 80, flush=True)
    print("Monitor de Editais Públicos - v2.0", flush=True)
    print("=" * 80, flush=True)
    print(f"\nAcesse a interface em:", flush=True)
    print(f"  Local: http://localhost:{config['servidor_porta']}", flush=True)
    print(f"  Rede: http://0.0.0.0:{config['servidor_porta']}", flush=True)
    print(f"\nPressione Ctrl+C para parar o servidor", flush=True)
    print("=" * 80, flush=True)
    print("", flush=True)

    app.run(
        host=config['servidor_host'],
        port=config['servidor_porta'],
        debug=False,
        threaded=True,
        use_reloader=False  # Desabilita reloader para evitar duplicação de logs
    )
