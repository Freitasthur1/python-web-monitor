# Guia do Administrador - Monitor de Editais

## Controle Administrativo

Esta aplicacao foi configurada com boas praticas de seguranca para uso publico.
Usuarios publicos NAO tem acesso a funcoes administrativas.

### Acesso Administrativo

Como administrador, voce tem acesso exclusivo via SSH para:

1. Iniciar/Parar o monitoramento
2. Testar configuracoes de email
3. Gerenciar subscribers
4. Visualizar logs completos

## Script de Controle Administrativo

Use o script `admin_control.py` para controlar o monitoramento:

### Comandos Disponiveis

```bash
# Iniciar monitoramento
python3 /opt/monitoramento-ufersa/admin_control.py start

# Parar monitoramento
python3 /opt/monitoramento-ufersa/admin_control.py stop

# Ver status
python3 /opt/monitoramento-ufersa/admin_control.py status

# Reiniciar
python3 /opt/monitoramento-ufersa/admin_control.py restart
```

## Controle via API (Local)

Como administrador com acesso SSH, voce pode usar curl localmente:

```bash
# Iniciar (BLOQUEADO - use admin_control.py)
# curl -X POST http://localhost:5000/api/start

# Status (publico)
curl http://localhost:5000/api/status

# Testar email (BLOQUEADO - configure no arquivo)
# curl -X POST http://localhost:5000/api/test-email
```

## Configuracoes

### Editar configuracoes manualmente

```bash
nano /opt/monitoramento-ufersa/config/config.json
```

Apos editar, reinicie o servico:

```bash
sudo systemctl restart monitor-edital.service
```

### Testar Email (via Python)

```bash
cd /opt/monitoramento-ufersa
python3 -c "
from src.email_notifier import EmailNotifier
from src.app import load_config, load_subscribers

config = load_config()
notifier = EmailNotifier(config['email'])
subscribers = load_subscribers()

# Testa conexao
sucesso, msg = notifier.testar_conexao()
print(f'Conexao: {msg}')

# Envia teste
if sucesso and subscribers:
    notifier.enviar_alerta(
        url=config['url'],
        palavras_encontradas=['Teste Admin'],
        mudanca_conteudo=True,
        destinatarios=subscribers
    )
    print(f'Email de teste enviado para {len(subscribers)} inscrito(s)')
"
```

## Gerenciar Subscribers

### Ver lista completa

```bash
cat /opt/monitoramento-ufersa/data/subscribers.json
```

### Adicionar email manualmente

```bash
python3 -c "
import json
email = 'novo@email.com'
with open('/opt/monitoramento-ufersa/data/subscribers.json', 'r') as f:
    data = json.load(f)
if email not in data['emails']:
    data['emails'].append(email)
    with open('/opt/monitoramento-ufersa/data/subscribers.json', 'w') as f:
        json.dump(data, f, indent=4)
    print(f'Email {email} adicionado')
else:
    print('Email ja existe')
"
```

### Remover email manualmente

```bash
python3 -c "
import json
email = 'remover@email.com'
with open('/opt/monitoramento-ufersa/data/subscribers.json', 'r') as f:
    data = json.load(f)
if email in data['emails']:
    data['emails'].remove(email)
    with open('/opt/monitoramento-ufersa/data/subscribers.json', 'w') as f:
        json.dump(data, f, indent=4)
    print(f'Email {email} removido')
else:
    print('Email nao encontrado')
"
```

## Logs

### Ver logs em tempo real

```bash
tail -f /opt/monitoramento-ufersa/logs/service.log
```

### Ver apenas erros

```bash
grep "\[ERRO\]" /opt/monitoramento-ufersa/logs/service.log
```

### Ver alertas

```bash
grep "\[ALERTA\]" /opt/monitoramento-ufersa/logs/service.log
```

### Limpar logs

```bash
> /opt/monitoramento-ufersa/logs/service.log
```

## Servico Systemd

### Status do servico

```bash
sudo systemctl status monitor-edital.service
```

### Reiniciar servico

```bash
sudo systemctl restart monitor-edital.service
```

### Parar servico

```bash
sudo systemctl stop monitor-edital.service
```

### Iniciar servico

```bash
sudo systemctl start monitor-edital.service
```

### Ver logs do systemd

```bash
journalctl -u monitor-edital.service -f
```

## Seguranca Implementada

### Endpoints Bloqueados (403 Forbidden)

Os seguintes endpoints retornam erro 403 para usuarios publicos:

- POST /api/config - Alterar configuracoes
- POST /api/start - Iniciar monitoramento
- POST /api/stop - Parar monitoramento
- POST /api/test-email - Testar email
- POST /api/clear-logs - Limpar logs
- DELETE /api/subscribers/<email> - Remover inscrito
- POST /api/check-now - Forcar verificacao
- GET /api/diagnostic - Diagnostico
- POST /api/reset-hash - Resetar hash

### Endpoints Publicos (Somente Leitura)

- GET / - Interface web
- GET /api/status - Status do sistema
- GET /api/logs - Logs (limitado a 50 entradas)
- GET /api/subscribers - Contagem de inscritos (SEM revelar emails)
- POST /api/subscribers - Adicionar email (usuarios podem se inscrever)

### Privacidade de Dados

- Emails dos inscritos NAO sao exibidos na interface publica
- Apenas a contagem de inscritos e mostrada
- Senhas SMTP nunca sao exibidas na API

## Backup e Restauracao

### Fazer backup

```bash
tar -czf monitor-backup-$(date +%Y%m%d).tar.gz \
  /opt/monitoramento-ufersa/config/ \
  /opt/monitoramento-ufersa/data/ \
  /opt/monitoramento-ufersa/logs/
```

### Restaurar backup

```bash
tar -xzf monitor-backup-YYYYMMDD.tar.gz -C /
sudo systemctl restart monitor-edital.service
```

## Atualizacoes

### Atualizar codigo

```bash
cd /opt/monitoramento-ufersa
git pull
sudo systemctl restart monitor-edital.service
```

## Solucao de Problemas

### Aplicacao nao inicia

```bash
# Verificar logs
journalctl -u monitor-edital.service -n 50

# Verificar permissoes
ls -la /opt/monitoramento-ufersa/

# Verificar porta
netstat -tulpn | grep 5000
```

### Email nao esta enviando

```bash
# Testar conexao SMTP
python3 -c "
from src.email_notifier import EmailNotifier
from src.app import load_config

config = load_config()
notifier = EmailNotifier(config['email'])
sucesso, msg = notifier.testar_conexao()
print(msg)
"
```

### Monitoramento nao detecta mudancas

```bash
# Resetar hash (ira detectar mudanca na proxima verificacao)
# Execute isso apenas via script Python direto no servidor

python3 -c "
import sys
sys.path.insert(0, '/opt/monitoramento-ufersa')
from src.monitor import MonitorEdital
from src.app import load_config

config = load_config()
monitor = MonitorEdital(
    config['url'],
    config['palavras_chave'],
    config['intervalo_minutos']
)

# Isso fara a proxima verificacao detectar mudanca
monitor.hash_anterior = None
print('Hash resetado')
"
```

---

**Importante**: Nunca compartilhe as credenciais SMTP ou acesso SSH com usuarios nao autorizados.
