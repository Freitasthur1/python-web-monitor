#!/usr/bin/env python3
"""
Entry Point - Monitor de Editais
Inicia a aplicação web
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import app, load_config

if __name__ == '__main__':
    config = load_config()

    print("=" * 80)
    print("Monitor de Editais Públicos - v2.0")
    print("=" * 80)
    print(f"\nAcesse a interface em:")
    print(f"  Local: http://localhost:{config['servidor_porta']}")
    print(f"  Rede: http://0.0.0.0:{config['servidor_porta']}")
    print(f"\nPressione Ctrl+C para parar o servidor")
    print("=" * 80)
    print()

    app.run(
        host=config['servidor_host'],
        port=config['servidor_porta'],
        debug=False,
        threaded=True
    )
