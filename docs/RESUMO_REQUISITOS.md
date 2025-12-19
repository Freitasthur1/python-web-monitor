# Monitor de Editais - Resumo de Requisitos para Hospedagem

## Aplicação
**Nome:** Monitor de Editais Públicos v2.0
**Tipo:** Web Application (Python Flask) com worker de monitoramento contínuo
**Finalidade:** Monitoramento automatizado de páginas web com notificações por email

---

## Requisitos Mínimos

### Recursos Computacionais
- **CPU:** 0.1-0.25 vCPU
- **RAM:** 128 MB (recomendado: 256 MB)
- **Armazenamento:** 50 MB
- **Banda:** 500 MB/mês

### Stack Tecnológico
- **Runtime:** Python 3.7+
- **Framework:** Flask 3.0+
- **Dependências:** 5 pacotes pip (requests, beautifulsoup4, lxml, flask, flask-cors)
- **Banco de dados:** Nenhum (usa arquivos JSON)
- **Servidor Web:** Flask built-in ou Gunicorn

### Requisitos de Rede
- **Porta de entrada:** 1 porta HTTP (ex: 5000)
- **Conexões de saída:**
  - HTTPS (porta 443) - para web scraping
  - SMTP (porta 587/465) - para envio de emails
- **IP:** Público (para acesso web)

### Requisitos de Execução
- **Tipo de processo:** Long-running (daemon/worker contínuo)
- **Threads:** 2 (Flask main + worker background)
- **Uptime:** Preferível 24/7 (mas pode tolerar sleep curtos)
- **Auto-restart:** Recomendado

---

## Especificações Técnicas Resumidas

| Item | Especificação |
|------|---------------|
| Linguagem | Python 3.7+ |
| Framework | Flask 3.0 + Gunicorn |
| Processo | Daemon (background worker) |
| Persistência | Filesystem (JSON) |
| API | REST JSON |
| Protocolos | HTTP, HTTPS, SMTP |
| Segurança | TLS/SSL via proxy reverso |

---

## Funcionalidades Principais

1. **Interface Web:** Dashboard para controle e configuração
2. **Monitoramento:** Web scraping periódico (intervalo configurável)
3. **Detecção:** Hash-based change detection (SHA-256)
4. **Notificações:** Email via SMTP para múltiplos destinatários
5. **API REST:** 12 endpoints para integração

---

## Plataformas Compatíveis Conhecidas

### Testadas e Recomendadas
- Oracle Cloud Free Tier (VPS - Always Free)
- Render.com (com limitação de sleep)
- Railway.app (crédito mensal limitado)
- Fly.io (free tier limitado)

### Não Recomendadas
- PythonAnywhere Free (não permite background workers)
- Google Cloud Run (não ideal para processos contínuos)
- Vercel/Netlify (apenas para serverless/static)

---

## Arquivos de Deploy Fornecidos

- `requirements.txt` - Dependências Python
- `run.py` - Entry point
- `start.sh` - Script de inicialização
- `Dockerfile` - Pode ser criado facilmente
- `render.yaml` - Configuração para Render
- Procfile - Para Heroku/Railway

---

## Comandos de Inicialização

```bash
# Desenvolvimento
python3 run.py

# Produção (Gunicorn)
gunicorn --bind 0.0.0.0:5000 --workers 2 run:app

# Docker
docker build -t monitor-edital .
docker run -p 5000:5000 monitor-edital
```

---

## Health Check

**Endpoint:** `GET /api/status`

**Resposta esperada (200 OK):**
```json
{
  "running": true,
  "current_check": 42,
  "last_check": "2025-12-18 20:30:00",
  "next_check": "2025-12-18 20:40:00",
  "palavras_encontradas": ["Resultado"],
  "mudancas_detectadas": 3
}
```

---

## Variáveis de Ambiente Necessárias

Atualmente usa arquivo `config/config.json`, mas pode ser adaptado para:

```bash
FLASK_PORT=5000
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=email@example.com
SMTP_PASSWORD=senha_app
MONITOR_URL=https://site-a-monitorar.com
MONITOR_INTERVAL=10
```

---

## Limitações e Considerações

1. **Worker contínuo:** Aplicação precisa rodar 24/7, não é serverless
2. **SMTP de saída:** Plataforma deve permitir conexões SMTP (porta 587/465)
3. **HTTPS de saída:** Para web scraping do site monitorado
4. **Persistência:** Arquivos JSON precisam ser mantidos entre restarts
5. **Sleep:** Plataformas com sleep podem perder verificações agendadas

---

## Contato e Documentação

**Documentação completa:**
- `docs/ESPECIFICACOES_TECNICAS_HOSPEDAGEM.md` (detalhes técnicos completos)
- `docs/GUIA_DEPLOY_GRATUITO.md` (passo a passo para deploy)
- `docs/README.md` (documentação geral)

**Autor:** Arthur Freitas
**Versão:** 2.0
**Licença:** MIT

---

## Perguntas Frequentes (FAQ)

**P: A aplicação pode rodar em plataforma serverless?**
R: Não é ideal. Precisa de um processo contínuo (daemon), não apenas request-driven.

**P: Precisa de banco de dados?**
R: Não. Usa arquivos JSON no filesystem.

**P: Qual o tráfego de rede esperado?**
R: Baixo. ~50-200 KB a cada intervalo de verificação (padrão: 10 min). Emails adicionam ~10-50 KB cada.

**P: Pode escalar horizontalmente?**
R: Não foi projetado para isso. Uma única instância é suficiente. Escala vertical se necessário.

**P: Requer configuração de firewall específica?**
R: Sim. Permitir entrada na porta da aplicação (5000) e saída para HTTPS (443) e SMTP (587/465).

**P: Qual o tempo de uptime esperado?**
R: Idealmente 99%+. Pode tolerar pequenas interrupções (sleep de plataforma free tier), mas verificações agendadas durante sleep serão perdidas.

---

**Documento gerado em:** 18/12/2025
**Válido para versão:** 2.0
