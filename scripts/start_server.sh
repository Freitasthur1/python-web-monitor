#!/bin/bash
#
# Script de inicialização do servidor de monitoramento
# Uso: ./start_server.sh
#

echo "=========================================="
echo "Monitor de Editais - Servidor Web"
echo "=========================================="
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

# Cria arquivo de configuração se não existir
if [ ! -f config.json ]; then
    echo "Criando arquivo de configuração inicial..."
    cp config.json.example config.json
    echo "ATENÇÃO: Edite o arquivo config.json com suas configurações"
fi

echo ""
echo "Iniciando servidor..."
echo "Acesse a interface em: http://localhost:5000"
echo "Para acesso externo: http://SEU_IP:5000"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo ""

# Inicia o servidor
python3 app.py
