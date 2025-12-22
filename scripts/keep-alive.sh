#!/bin/bash

# Keep-Alive Script para Oracle Cloud Free Tier
# Mantém o uso de CPU acima de 20% para evitar reclamação da VM

# Configurações
TARGET_CPU=25  # Percentual alvo de CPU (25% é seguro)
LOG_FILE="/opt/monitoramento-ufersa/logs/keep-alive.log"

# Cria diretório de logs se não existir
mkdir -p "$(dirname "$LOG_FILE")"

# Log de inicialização
echo "$(date '+%Y-%m-%d %H:%M:%S') - [KEEP-ALIVE] Iniciando keep-alive script (target: ${TARGET_CPU}% CPU)" >> "$LOG_FILE"

# Loop infinito para manter CPU ocupada
while true; do
    # Inicia processo que consome CPU
    yes > /dev/null &
    PID=$!

    # Mantém por um período para atingir ~25% de uso médio
    sleep 0.7

    # Mata o processo
    kill $PID 2>/dev/null

    # Pausa para não sobrecarregar (ajusta o percentual médio)
    sleep 2

    # Log a cada 6 horas para não encher o log
    CURRENT_HOUR=$(date '+%H')
    if [ "$CURRENT_HOUR" = "00" ] || [ "$CURRENT_HOUR" = "06" ] || [ "$CURRENT_HOUR" = "12" ] || [ "$CURRENT_HOUR" = "18" ]; then
        if [ ! -f "/tmp/keep-alive-logged-$CURRENT_HOUR" ]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - [KEEP-ALIVE] Rodando normalmente" >> "$LOG_FILE"
            touch "/tmp/keep-alive-logged-$CURRENT_HOUR"
            # Limpa marcadores antigos
            find /tmp -name "keep-alive-logged-*" -mmin +360 -delete 2>/dev/null
        fi
    fi
done
