#!/bin/bash
#
# Monitor de Editais - Script de Inicialização v2.0
# Uso: ./start.sh
#

echo "========================================"
echo "Monitor de Editais Públicos - v2.0"
echo "========================================"
echo ""

# Verifica se Python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 não encontrado."
    echo "Instale com: sudo apt install python3"
    exit 1
fi

# Verifica se pip está instalado
if ! python3 -m pip --version &> /dev/null; then
    echo "ERRO: pip não encontrado."
    echo "Instale com: sudo apt install python3-pip"
    exit 1
fi

# Verifica se as dependências estão instaladas
echo "Verificando dependências..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Instalando dependências..."
    pip3 install -r requirements.txt
fi

# Cria diretórios necessários
mkdir -p config logs data

# Cria arquivo de configuração se não existir
if [ ! -f config/config.json ]; then
    if [ -f config/config.json.example ]; then
        echo "Criando arquivo de configuração inicial..."
        cp config/config.json.example config/config.json
        echo "ATENÇÃO: Edite o arquivo config/config.json com suas configurações"
    fi
fi

echo ""
echo "Iniciando servidor..."
echo ""

# Inicia o servidor
python3 run.py
