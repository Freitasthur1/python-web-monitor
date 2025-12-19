# Guia de Deploy Gratuito - Passo a Passo
## Monitor de Editais v2.0

Este guia fornece instruções detalhadas para fazer deploy da aplicação em plataformas gratuitas.

---

## Índice
1. [Oracle Cloud (Recomendado para 24/7)](#1-oracle-cloud-free-tier)
2. [Render.com (Mais Fácil)](#2-rendercom)
3. [Railway.app](#3-railwayapp)
4. [Fly.io](#4-flyio)
5. [Configurações Pós-Deploy](#5-configurações-pós-deploy)

---

## 1. Oracle Cloud Free Tier
**Melhor para: Produção 24/7 sem interrupções**

### 1.1 Criar Conta Oracle Cloud
1. Acesse https://www.oracle.com/cloud/free/
2. Clique em "Start for free"
3. Preencha dados e crie conta
4. Aguarde aprovação (pode levar até 24h)

### 1.2 Criar VM Gratuita

#### Passo 1: Criar Instância
```
1. No painel, vá em: Menu > Compute > Instances
2. Clique em "Create Instance"
3. Configurações:
   - Name: monitor-edital
   - Image: Canonical Ubuntu 22.04
   - Shape: VM.Standard.E2.1.Micro (Always Free)
   - Add SSH Keys: Gerar ou fazer upload
4. Clique em "Create"
```

#### Passo 2: Configurar Firewall
```
1. Na página da instância, vá em "Subnet"
2. Clique na Security List
3. Add Ingress Rule:
   - Source CIDR: 0.0.0.0/0
   - Destination Port: 5000
   - Description: Monitor Edital Web
4. Save
```

#### Passo 3: Conectar via SSH
```bash
# No seu computador local
ssh -i /caminho/para/chave.pem ubuntu@<IP-PUBLICO>

# Após conectar:
sudo apt update && sudo apt upgrade -y
```

### 1.3 Instalar Aplicação

```bash
# 1. Instalar Python e dependências
sudo apt install python3 python3-pip git -y

# 2. Clonar repositório (ajuste a URL)
cd /opt
sudo git clone https://github.com/seu-usuario/monitoramento-ufersa.git
sudo chown -R ubuntu:ubuntu monitoramento-ufersa
cd monitoramento-ufersa

# 3. Instalar dependências Python
pip3 install -r requirements.txt

# 4. Criar configuração
cp config/config.json.example config/config.json 2>/dev/null || echo '{
  "url": "https://fgduque.org.br/edital/...",
  "palavras_chave": ["Resultado", "Homologação"],
  "intervalo_minutos": 10,
  "servidor_host": "0.0.0.0",
  "servidor_porta": 5000,
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "seu-email@gmail.com",
    "smtp_password": "senha-app",
    "from_email": "seu-email@gmail.com",
    "use_tls": true
  }
}' > config/config.json

# 5. Editar configuração
nano config/config.json
# Ajuste: URL do edital, email, senha de app do Gmail
```

### 1.4 Configurar como Serviço

```bash
# 1. Criar arquivo de serviço
sudo nano /etc/systemd/system/monitor-edital.service
```

```ini
[Unit]
Description=Monitor de Editais Públicos
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/monitoramento-ufersa
ExecStart=/usr/bin/python3 /opt/monitoramento-ufersa/run.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/monitoramento-ufersa/logs/service.log
StandardError=append:/opt/monitoramento-ufersa/logs/service-error.log

[Install]
WantedBy=multi-user.target
```

```bash
# 2. Criar diretório de logs
mkdir -p /opt/monitoramento-ufersa/logs

# 3. Ativar e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable monitor-edital
sudo systemctl start monitor-edital

# 4. Verificar status
sudo systemctl status monitor-edital

# 5. Ver logs em tempo real
sudo journalctl -u monitor-edital -f
```

### 1.5 Configurar Firewall da VM

```bash
# Abrir porta 5000
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 5000 -j ACCEPT
sudo netfilter-persistent save

# Ou usar ufw (mais fácil)
sudo ufw allow 5000/tcp
sudo ufw status
```

### 1.6 Acessar Aplicação

```
Acesse: http://<IP-PUBLICO-DA-VM>:5000
```

### 1.7 (Opcional) Configurar Domínio e HTTPS

```bash
# 1. Instalar nginx
sudo apt install nginx certbot python3-certbot-nginx -y

# 2. Configurar nginx
sudo nano /etc/nginx/sites-available/monitor-edital
```

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# 3. Ativar site
sudo ln -s /etc/nginx/sites-available/monitor-edital /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 4. Obter certificado SSL (após apontar domínio para IP)
sudo certbot --nginx -d seu-dominio.com
```

---

## 2. Render.com
**Melhor para: Deploy rápido e fácil**

### 2.1 Preparar Repositório

Adicione os arquivos necessários ao seu repositório Git:

#### Arquivo: `render.yaml`
```yaml
services:
  - type: web
    name: monitor-edital
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 2 run:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

#### Arquivo: `requirements.txt` (adicionar gunicorn)
```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
flask>=3.0.0
flask-cors>=4.0.0
gunicorn>=21.0.0
```

### 2.2 Deploy no Render

1. Acesse https://render.com e crie conta
2. Conecte sua conta GitHub
3. Clique em "New +" > "Web Service"
4. Selecione seu repositório
5. Configurações:
   - Name: monitor-edital
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 run:app`
6. Clique em "Create Web Service"

### 2.3 Configurar Variáveis de Ambiente (Opcional)

No dashboard do Render:
1. Vá em "Environment"
2. Adicione:
   - `SMTP_USER=seu-email@gmail.com`
   - `SMTP_PASSWORD=senha-app`
   - Etc.

### 2.4 Manter Ativo (Evitar Sleep)

Render free tier dorme após 15 min de inatividade. Soluções:

#### Opção A: UptimeRobot (Recomendado)
1. Acesse https://uptimerobot.com
2. Crie conta gratuita
3. Add New Monitor:
   - Type: HTTP(s)
   - URL: https://seu-app.onrender.com/api/status
   - Interval: 5 minutes
4. Salvar

#### Opção B: Cron-job.org
1. Acesse https://cron-job.org
2. Crie conta
3. Create Cronjob:
   - URL: https://seu-app.onrender.com/api/status
   - Schedule: Every 5 minutes

**Atenção:** Mesmo com ping, o Render pode ter pequenas interrupções.

---

## 3. Railway.app
**Melhor para: Deploy com créditos mensais**

### 3.1 Preparar Projeto

#### Arquivo: `Procfile`
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 run:app
```

#### Arquivo: `railway.json` (opcional)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT run:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3.2 Deploy no Railway

1. Acesse https://railway.app e faça login com GitHub
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha seu repositório
5. Railway detecta Python automaticamente
6. Clique em "Deploy"

### 3.3 Configurar Variáveis

1. No dashboard, clique no serviço
2. Vá em "Variables"
3. Adicione:
   - `PORT=5000` (Railway fornece automaticamente)
   - Outras variáveis conforme necessário

### 3.4 Ver Logs

```
Dashboard > Seu Projeto > Deployments > View Logs
```

---

## 4. Fly.io
**Melhor para: Controle avançado**

### 4.1 Instalar CLI do Fly

```bash
# Linux/Mac
curl -L https://fly.io/install.sh | sh

# Adicionar ao PATH
export FLYCTL_INSTALL="/home/user/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

### 4.2 Fazer Login

```bash
flyctl auth login
```

### 4.3 Criar Dockerfile

Crie `Dockerfile` na raiz do projeto:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Criar diretórios
RUN mkdir -p config logs data

# Expor porta
EXPOSE 8080

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "run:app"]
```

### 4.4 Inicializar e Deploy

```bash
# 1. Inicializar app
flyctl launch
# Responda as perguntas:
# - App name: monitor-edital
# - Region: escolha mais próxima
# - PostgreSQL: No
# - Redis: No

# 2. Deploy
flyctl deploy

# 3. Abrir no browser
flyctl open

# 4. Ver logs
flyctl logs
```

### 4.5 Configurar Secrets

```bash
flyctl secrets set SMTP_USER=seu-email@gmail.com
flyctl secrets set SMTP_PASSWORD=senha-app
```

---

## 5. Configurações Pós-Deploy

### 5.1 Configurar Gmail para SMTP

1. Acesse https://myaccount.google.com/security
2. Ative "Verificação em duas etapas"
3. Vá em "Senhas de app"
4. Gerar senha de app:
   - App: Mail
   - Device: Other (Monitor Edital)
5. Copie a senha gerada (16 caracteres)
6. Use essa senha no campo `smtp_password`

### 5.2 Testar Aplicação

1. Acesse a URL da sua aplicação
2. Vá em "Configurações"
3. Configure a URL do edital
4. Vá em "Notificações Email"
5. Preencha dados SMTP
6. Clique em "Enviar Email de Teste"
7. Verifique sua caixa de entrada

### 5.3 Iniciar Monitoramento

1. Vá em "Controles"
2. Clique em "Iniciar Monitoramento"
3. Observe os logs em tempo real
4. Aguarde primeira verificação

---

## 6. Troubleshooting

### Problema: Porta já em uso
```bash
# Verificar processo na porta 5000
sudo lsof -i :5000

# Matar processo
sudo kill -9 <PID>
```

### Problema: Erro ao conectar SMTP
```
Soluções:
1. Verificar se senha de app está correta
2. Verificar se 2FA está ativado no Gmail
3. Testar com outro provedor SMTP (Outlook, etc.)
4. Verificar firewall da plataforma permite SMTP de saída
```

### Problema: App não inicia
```bash
# Verificar logs
sudo journalctl -u monitor-edital -n 50

# Testar manualmente
cd /opt/monitoramento-ufersa
python3 run.py
```

### Problema: Render/Railway dormindo
```
Solução:
1. Usar UptimeRobot para ping a cada 5 min
2. Aceitar pequenos períodos offline
3. Ou fazer upgrade para plano pago
```

---

## 7. Comparação Rápida

| Aspecto | Oracle Cloud | Render | Railway | Fly.io |
|---------|-------------|---------|---------|--------|
| **Setup** | 3/5 Médio | 5/5 Fácil | 5/5 Fácil | 3/5 Médio |
| **24/7** | Sim | Dorme | Crédito | Sim |
| **RAM** | 1 GB | 512 MB | 512 MB | 256 MB |
| **Custo** | Grátis | Grátis* | $5/mês | Grátis |
| **Manutenção** | Manual | Auto | Auto | Auto |
| **SSL** | Manual | Auto | Auto | Auto |
| **Logs** | journalctl | Dashboard | Dashboard | CLI |

**Recomendação Final:**
- **Para aprender:** Render ou Railway
- **Para produção 24/7:** Oracle Cloud
- **Para protótipo rápido:** Render
- **Para controle total:** Oracle Cloud ou Fly.io

---

## 8. Checklist Final

Após deploy, verifique:

- [ ] Aplicação acessível via navegador
- [ ] Interface web carrega corretamente
- [ ] API `/api/status` responde
- [ ] Consegue iniciar/parar monitoramento
- [ ] Logs aparecem em tempo real
- [ ] Teste de email funciona
- [ ] Email chega na caixa de entrada
- [ ] Monitoramento roda continuamente
- [ ] App reinicia após crash (auto-restart)

---

## 9. Recursos Adicionais

### Documentação Oficial das Plataformas
- Oracle Cloud: https://docs.oracle.com/en-us/iaas/
- Render: https://render.com/docs
- Railway: https://docs.railway.app
- Fly.io: https://fly.io/docs

### Ferramentas Úteis
- UptimeRobot: https://uptimerobot.com (keep-alive)
- Cron-job.org: https://cron-job.org (scheduled pings)
- Let's Encrypt: https://letsencrypt.org (SSL grátis)
- Cloudflare: https://cloudflare.com (DNS + CDN)

---

**Última atualização:** Dezembro 2025
**Versão:** 1.0
**Autor:** Arthur Freitas
