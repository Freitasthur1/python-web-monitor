# Especificações Técnicas - Monitor de Editais v2.0
## Documento para Hospedagem Gratuita

---

## 1. VISÃO GERAL DA APLICAÇÃO

**Nome:** Monitor de Editais Públicos
**Versão:** 2.0
**Tipo:** Aplicação Web Python com monitoramento contínuo
**Finalidade:** Monitoramento automatizado de páginas web de editais públicos com notificações por email

---

## 2. STACK TECNOLÓGICO

### 2.1 Backend
- **Linguagem:** Python 3.7+
- **Framework Web:** Flask 3.0.0+
- **Servidor WSGI:** Flask built-in (dev) / Gunicorn (produção)

### 2.2 Dependências Python
```
requests>=2.31.0          # Cliente HTTP
beautifulsoup4>=4.12.0    # Parser HTML/XML
lxml>=4.9.0               # Parser de alta performance
flask>=3.0.0              # Framework web
flask-cors>=4.0.0         # CORS middleware
gunicorn>=21.0.0          # WSGI server (opcional, produção)
```

### 2.3 Frontend
- HTML5
- CSS3 (Grid, Flexbox)
- JavaScript Vanilla (ES6+)
- Interface responsiva (mobile-first)

### 2.4 Protocolos e Padrões
- HTTP/HTTPS (cliente e servidor)
- SMTP (envio de emails)
- REST API (JSON)
- WebSocket-like polling (atualização em tempo real)

---

## 3. ARQUITETURA

### 3.1 Estrutura da Aplicação
```
Aplicação Flask (Main Thread)
├── API REST Endpoints
├── Interface Web (Templates + Static)
├── Worker Thread (Monitoramento Contínuo)
│   ├── Web Scraping (requests + BeautifulSoup)
│   ├── Hash Comparison (SHA-256)
│   ├── Keyword Detection
│   └── Email Notifications (SMTP)
└── File Storage (JSON)
    ├── config/config.json (configurações)
    ├── data/subscribers.json (emails inscritos)
    └── logs/ (logs de execução)
```

### 3.2 Modelo de Execução
- **Tipo:** Long-running process (daemon)
- **Threading:** Multi-threaded (Flask main + Worker background)
- **Persistência:** Filesystem (JSON files)
- **Estado:** In-memory + File-based

---

## 4. REQUISITOS DE RECURSOS

### 4.1 Recursos Computacionais
| Recurso | Mínimo | Recomendado | Observações |
|---------|---------|-------------|-------------|
| **CPU** | 0.1 vCPU | 0.25 vCPU | Baixo consumo, maioria idle |
| **RAM** | 64 MB | 128 MB | ~50-100MB em uso típico |
| **Armazenamento** | 10 MB | 50 MB | 1.2MB app + logs crescentes |
| **Banda** | 100 MB/mês | 500 MB/mês | Depende do intervalo |

### 4.2 Armazenamento de Dados
- **Tipo:** Filesystem (JSON)
- **Volumes necessários:**
  - `/config` - Arquivo de configuração (< 1 KB)
  - `/data` - Lista de emails inscritos (< 10 KB)
  - `/logs` - Logs da aplicação (crescente, ~1 MB/mês)
- **Backup:** Desejável mas não crítico
- **Banco de dados:** Não requerido

### 4.3 Rede e Conectividade

#### Requisitos de Rede
- **Porta de entrada:** 5000 (TCP) - configurável
- **Protocolo:** HTTP/HTTPS
- **IP Binding:** 0.0.0.0 (todas interfaces)

#### Requisitos de Saída (Outbound)
1. **Web Scraping:**
   - Protocolo: HTTPS
   - Destino: URL configurada do edital
   - Frequência: A cada X minutos (padrão: 10 min)
   - Banda: ~50-200 KB por request

2. **Email (SMTP):**
   - Protocolo: SMTP/TLS (porta 587) ou SMTP/SSL (porta 465)
   - Destinos comuns:
     - Gmail: smtp.gmail.com:587
     - Outlook: smtp.office365.com:587
     - Outros provedores SMTP
   - Frequência: Apenas quando detecta mudanças
   - Banda: ~10-50 KB por email

#### Restrições de Firewall
- **Crítico:** Permitir conexões HTTPS de saída (porta 443)
- **Crítico:** Permitir conexões SMTP de saída (porta 587/465)
- **Desejável:** IP estático ou domínio fixo para acesso

---

## 5. FUNCIONALIDADES PRINCIPAIS

### 5.1 Monitoramento Web
- Scraping de páginas HTML via requests + BeautifulSoup
- Extração inteligente de conteúdo relevante
- Detecção de mudanças via hash SHA-256
- Busca por palavras-chave configuráveis
- Verificação periódica (intervalo configurável)

### 5.2 Notificações
- Sistema de email via SMTP
- Templates HTML responsivos
- Suporte multi-destinatário (sistema de inscrição)
- Alertas apenas quando detecta mudanças reais

### 5.3 Interface Web
- Dashboard em tempo real
- Controles de start/stop do monitor
- Configuração de URL e palavras-chave
- Configuração SMTP
- Sistema de inscrição de emails
- Visualização de logs
- API REST completa

### 5.4 API REST Endpoints
```
GET  /api/status          - Status do monitoramento
GET  /api/logs            - Logs recentes
GET  /api/config          - Configuração atual
POST /api/config          - Atualizar configuração
POST /api/start           - Iniciar monitoramento
POST /api/stop            - Parar monitoramento
POST /api/test-email      - Testar notificação
GET  /api/subscribers     - Lista de inscritos
POST /api/subscribers     - Adicionar inscrito
DELETE /api/subscribers/<email> - Remover inscrito
POST /api/check-now       - Forçar verificação
GET  /api/diagnostic      - Diagnóstico do sistema
POST /api/reset-hash      - Reset hash (debug)
```

---

## 6. VARIÁVEIS DE AMBIENTE E CONFIGURAÇÃO

### 6.1 Configuração via Arquivo (config/config.json)
```json
{
  "url": "https://exemplo.com/edital",
  "palavras_chave": ["Resultado", "Homologação"],
  "intervalo_minutos": 10,
  "servidor_host": "0.0.0.0",
  "servidor_porta": 5000,
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "user@gmail.com",
    "smtp_password": "senha_app",
    "from_email": "user@gmail.com",
    "use_tls": true
  }
}
```

### 6.2 Variáveis de Ambiente Opcionais
A aplicação atualmente usa arquivo JSON, mas pode ser adaptada para:
```bash
MONITOR_URL=https://exemplo.com/edital
MONITOR_INTERVAL=10
FLASK_PORT=5000
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=email@example.com
SMTP_PASSWORD=senha
```

---

## 7. PROCESSO DE EXECUÇÃO

### 7.1 Inicialização
```bash
# Método 1: Script de inicialização
./start.sh

# Método 2: Python direto
python3 run.py

# Método 3: Gunicorn (produção)
gunicorn --bind 0.0.0.0:5000 --workers 2 run:app
```

### 7.2 Processo Contínuo
- **Tipo:** Daemon / Long-running process
- **Requer:** Processo que não seja interrompido após inatividade
- **Workers:** 1 thread principal + 1 thread de monitoramento
- **Auto-restart:** Recomendado (via systemd, supervisord, ou plataforma)

### 7.3 Health Check
```bash
# Endpoint de verificação
curl http://localhost:5000/api/status

# Resposta esperada
{"running": true, "current_check": 42, ...}
```

---

## 8. SEGURANÇA

### 8.1 Credenciais
- Senhas SMTP armazenadas em arquivo JSON (não criptografadas)
- **Recomendação:** Usar senhas de aplicativo (Gmail App Passwords)
- **Atenção:** Não commitar arquivo config.json com credenciais

### 8.2 Exposição Web
- Aplicação Flask em modo debug=False
- CORS habilitado (configurável)
- Sem autenticação na interface (adicionar se necessário)

### 8.3 Melhorias Recomendadas
- [ ] HTTPS via proxy reverso (nginx, Caddy)
- [ ] Autenticação básica na interface
- [ ] Rate limiting
- [ ] Variáveis de ambiente para credenciais
- [ ] Criptografia de senhas em repouso

---

## 9. PLATAFORMAS DE HOSPEDAGEM GRATUITA

### 9.1 Opções Viáveis

#### A. **Render.com** (RECOMENDADO)
**Características:**
- Free tier: 750 horas/mês
- RAM: 512 MB
- Auto-deploy via Git
- Suporte a workers contínuos
- HTTPS automático

**Limitações:**
- Aplicação "dorme" após 15 min de inatividade
- Necessário upgrade para manter 24/7

**Configuração:**
```yaml
# render.yaml
services:
  - type: web
    name: monitor-edital
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT run:app
```

#### B. **Railway.app**
**Características:**
- $5 grátis/mês (500h de execução)
- RAM: 512 MB
- Deploy via Git
- Boa performance

**Limitações:**
- Crédito limitado mensal
- Pode acabar no meio do mês

#### C. **Fly.io**
**Características:**
- 3 VMs pequenas gratuitas
- RAM: 256 MB cada
- Persistência de volumes
- Boa para apps Python

**Limitações:**
- Configuração mais complexa
- Requer Dockerfile

#### D. **PythonAnywhere**
**Características:**
- Especializado em Python
- Free tier: 1 web app
- Fácil configuração

**Limitações:**
- Free tier não permite processos contínuos em background
- Apenas para web apps síncronos
- **NÃO RECOMENDADO para esta aplicação** (precisa de worker contínuo)

#### E. **Replit**
**Características:**
- IDE online + hosting
- Deploy simples
- Boa para prototipagem

**Limitações:**
- App dorme após inatividade
- Performance limitada
- Não ideal para produção

#### F. **Oracle Cloud Free Tier** (MELHOR PARA 24/7)
**Características:**
- 2 VMs AMD com 1 GB RAM cada (SEMPRE GRÁTIS)
- 4 VMs ARM com 24 GB RAM total
- 200 GB de armazenamento
- 10 TB de tráfego/mês
- Sem tempo limite

**Vantagens:**
- 100% grátis para sempre
- Controle total (VPS)
- Pode rodar 24/7
- Melhor opção para produção

**Configuração:**
1. Criar conta Oracle Cloud
2. Criar VM (Ubuntu/Debian)
3. Instalar Python + dependências
4. Configurar como serviço systemd
5. Abrir porta 5000 no firewall

#### G. **Google Cloud Run**
**Características:**
- 2 milhões de requests/mês grátis
- Escala automática
- Pay-per-use

**Limitações:**
- Não ideal para processos contínuos
- Melhor para request-driven apps
- **NÃO RECOMENDADO** (app precisa rodar continuamente)

### 9.2 Comparativo Rápido

| Plataforma | RAM | Uptime 24/7 | Worker Contínuo | Facilidade | Nota |
|-----------|-----|-------------|-----------------|------------|------|
| **Oracle Cloud** | 1-24 GB | Sim | Sim | 3/5 | 10/10 |
| **Render** | 512 MB | Dorme | Limitado | 5/5 | 7/10 |
| **Railway** | 512 MB | Crédito | Sim | 4/5 | 8/10 |
| **Fly.io** | 256 MB | Sim | Sim | 3/5 | 8/10 |
| **Replit** | 500 MB | Dorme | Não | 5/5 | 5/10 |
| PythonAnywhere | 512 MB | Sim | Não | 4/5 | 3/10 |

---

## 10. RECOMENDAÇÕES FINAIS

### 10.1 Para Hospedagem Gratuita 24/7
**MELHOR OPÇÃO: Oracle Cloud Free Tier**
- Criar VM gratuita (Always Free)
- Instalar Ubuntu 22.04
- Configurar como serviço systemd
- Monitoramento 24/7 sem interrupções

### 10.2 Para Deploy Rápido (Protótipo)
**MELHOR OPÇÃO: Render.com ou Railway.app**
- Deploy automático via Git
- Configuração simples
- Aceita inatividade (para testes)

### 10.3 Adaptações Necessárias

#### Para plataformas com sleep (Render, Replit):
1. Adicionar endpoint de "keep-alive"
2. Usar serviço externo de ping (UptimeRobot, cron-job.org)
3. Aceitar que pode perder algumas verificações

#### Para Oracle Cloud/VPS:
1. Criar serviço systemd
2. Configurar firewall
3. Usar nginx como proxy reverso
4. Configurar SSL com Let's Encrypt

---

## 11. EXEMPLO DE CONFIGURAÇÃO (ORACLE CLOUD)

### 11.1 Instalação na VM
```bash
# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar Python e pip
sudo apt install python3 python3-pip git -y

# 3. Clonar repositório
git clone [seu-repo] /opt/monitor-edital
cd /opt/monitor-edital

# 4. Instalar dependências
pip3 install -r requirements.txt

# 5. Criar arquivo de configuração
cp config/config.json.example config/config.json
nano config/config.json  # Editar configurações

# 6. Testar manualmente
python3 run.py
```

### 11.2 Configurar como Serviço (systemd)
```ini
# /etc/systemd/system/monitor-edital.service
[Unit]
Description=Monitor de Editais Públicos
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/monitor-edital
ExecStart=/usr/bin/python3 /opt/monitor-edital/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable monitor-edital
sudo systemctl start monitor-edital
sudo systemctl status monitor-edital
```

### 11.3 Configurar Firewall
```bash
# Abrir porta 5000
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 5000 -j ACCEPT
sudo netfilter-persistent save

# Ou usar ufw
sudo ufw allow 5000/tcp
```

---

## 12. CHECKLIST DE HOSPEDAGEM

### Antes de Escolher Plataforma
- [ ] Verifica se permite processos contínuos (workers)
- [ ] Verifica se permite conexões SMTP de saída
- [ ] Verifica se permite conexões HTTPS de saída
- [ ] Verifica limites de RAM (mín. 128 MB)
- [ ] Verifica se fornece IP/domínio público
- [ ] Verifica se tem auto-restart em caso de crash

### Após Deploy
- [ ] Testar acesso à interface web
- [ ] Testar API REST
- [ ] Iniciar monitoramento via interface
- [ ] Verificar logs em tempo real
- [ ] Testar envio de email
- [ ] Adicionar email para inscrição
- [ ] Forçar verificação manual
- [ ] Verificar se worker está rodando continuamente

---

## 13. SUPORTE E CONTATO

**Documentação Completa:**
- README.md
- docs/INSTALL.md
- docs/GUIA_RAPIDO.txt

**Autor:** Arthur Freitas
**Versão do Documento:** 1.0
**Data:** Dezembro 2025

---

## RESUMO EXECUTIVO

**O que é:** Aplicação web Python que monitora páginas de editais e envia alertas por email quando detecta mudanças.

**Recursos necessários:** ~100 MB RAM, 50 MB disco, porta HTTP, acesso SMTP.

**Melhor opção gratuita 24/7:** Oracle Cloud Free Tier (VPS grátis para sempre)

**Melhor opção deploy rápido:** Render.com ou Railway.app (com limitações)

**Processo:** Long-running (precisa rodar continuamente, não apenas sob demanda)

**Dificuldade de deploy:** Fácil a média (dependendo da plataforma)
