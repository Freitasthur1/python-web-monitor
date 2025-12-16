# Monitor de Editais Públicos

Sistema profissional de monitoramento automatizado de páginas web de editais públicos, com interface web elegante, detecção de mudanças e sistema de alertas em tempo real.

## Características

- Monitoramento contínuo e automatizado de páginas web
- Interface web responsiva e elegante para gerenciamento
- Detecção por palavras-chave configuráveis
- Detecção de mudanças no conteúdo (hash SHA-256)
- API REST para integração com outros sistemas
- Logs em tempo real com interface visual
- Configuração via interface web
- Suporte para execução como servidor
- Anti-bloqueio com User-Agent de navegador
- Tratamento robusto de erros

## Tecnologias Utilizadas

- **Backend:** Python 3.7+, Flask
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Parsing:** BeautifulSoup4, lxml
- **HTTP:** Requests

## Instalação

### Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)
- Conexão com a internet

### Passo a Passo

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/monitoramento-ufersa.git
cd monitoramento-ufersa
```

2. **Instale as dependências**

```bash
pip3 install -r requirements.txt
```

3. **Configure o sistema**

Copie o arquivo de exemplo e edite suas configurações:

```bash
cp config.json.example config.json
nano config.json
```

4. **Inicie o servidor**

```bash
./start_server.sh
```

Ou manualmente:

```bash
python3 app.py
```

## Configuração

Edite o arquivo `config.json` com suas configurações:

```json
{
    "url": "https://exemplo.com/edital",
    "palavras_chave": [
        "Resultado",
        "Homologação",
        "Classificados"
    ],
    "intervalo_minutos": 10,
    "servidor_host": "0.0.0.0",
    "servidor_porta": 5000
}
```

### Parâmetros

| Parâmetro | Descrição | Exemplo |
|-----------|-----------|---------|
| `url` | URL da página a ser monitorada | `"https://exemplo.com/edital"` |
| `palavras_chave` | Lista de palavras para buscar | `["Resultado", "Aprovados"]` |
| `intervalo_minutos` | Tempo entre verificações | `10` |
| `servidor_host` | IP do servidor | `"0.0.0.0"` para acesso externo |
| `servidor_porta` | Porta do servidor | `5000` |

## Uso

### Interface Web

Após iniciar o servidor, acesse:

- Local: `http://localhost:5000`
- Rede local: `http://SEU_IP:5000`
- Externo: Configure port forwarding no roteador

### Funcionalidades da Interface

1. **Dashboard:** Visualize status do monitoramento em tempo real
2. **Controles:** Iniciar/parar monitoramento
3. **Configurações:** Altere URL, palavras-chave e intervalo
4. **Logs:** Acompanhe todas as verificações e alertas
5. **Alertas:** Notificações visuais quando mudanças são detectadas

### Modo Terminal (Legado)

Para usar o monitor em modo terminal:

```bash
python3 monitor_edital.py
```

## Deploy como Servidor

### Execução em Segundo Plano

```bash
nohup python3 app.py > server.log 2>&1 &
```

### Usando systemd (Linux)

1. Crie o arquivo de serviço:

```bash
sudo nano /etc/systemd/system/monitor-edital.service
```

2. Cole o conteúdo:

```ini
[Unit]
Description=Monitor de Editais
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/caminho/para/monitoramento-ufersa
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Ative e inicie o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable monitor-edital
sudo systemctl start monitor-edital
```

4. Verifique o status:

```bash
sudo systemctl status monitor-edital
```

### Configuração de Firewall

Para permitir acesso externo à porta 5000:

```bash
sudo ufw allow 5000/tcp
```

### Acesso pela Internet

Para acessar de qualquer lugar:

1. Configure port forwarding no seu roteador (porta 5000)
2. Use um serviço de DNS dinâmico (DuckDNS, No-IP)
3. Ou use um túnel reverso (ngrok, localtunnel)

Exemplo com ngrok:

```bash
ngrok http 5000
```

## API REST

O sistema expõe endpoints REST para integração:

### GET /api/status

Retorna status atual do monitoramento.

```json
{
    "running": true,
    "current_check": 42,
    "last_check": "2024-12-16 10:30:00",
    "next_check": "2024-12-16 10:40:00",
    "palavras_encontradas": ["Resultado"],
    "mudancas_detectadas": 3
}
```

### GET /api/logs?limit=50

Retorna logs recentes.

### GET /api/config

Retorna configuração atual.

### POST /api/config

Atualiza configuração.

### POST /api/start

Inicia o monitoramento.

### POST /api/stop

Para o monitoramento.

### POST /api/clear-logs

Limpa os logs.

## Estrutura do Projeto

```
monitoramento-ufersa/
├── app.py                    # Aplicação Flask principal
├── monitor_edital.py         # Monitor em modo terminal (legado)
├── testar_monitor.py         # Script de teste
├── config.json               # Configurações (não versionado)
├── config.json.example       # Exemplo de configuração
├── requirements.txt          # Dependências Python
├── start_server.sh          # Script de inicialização
├── templates/
│   └── index.html           # Interface web
├── static/
│   ├── css/
│   │   └── style.css        # Estilos
│   └── js/
│       └── app.js           # JavaScript da interface
└── README.md                # Esta documentação
```

## Segurança

### Recomendações

1. **Firewall:** Sempre use firewall para controlar acesso
2. **HTTPS:** Use proxy reverso (nginx) com SSL em produção
3. **Autenticação:** Adicione autenticação básica se expor na internet
4. **Rate Limiting:** Configure intervalo mínimo de 5 minutos
5. **Logs:** Monitore logs para detectar acessos suspeitos

### Configurar HTTPS com nginx

1. Instale nginx e certbot:

```bash
sudo apt install nginx certbot python3-certbot-nginx
```

2. Configure nginx como proxy reverso:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Obtenha certificado SSL:

```bash
sudo certbot --nginx -d seu-dominio.com
```

## Solução de Problemas

### Erro: porta 5000 já em uso

Altere a porta em `config.json` ou mate o processo:

```bash
lsof -ti:5000 | xargs kill -9
```

### Monitor não detecta mudanças

1. Verifique se a URL está acessível
2. Inspecione o HTML da página para confirmar seletores
3. Verifique logs para erros de conexão

### Erro ao instalar dependências

Use ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Avisos Importantes

1. **Uso Ético:** Use apenas para fins legítimos e éticos
2. **Respeite Servidores:** Não use intervalos muito curtos (mínimo 5 minutos)
3. **Conectividade:** Requer conexão estável com a internet
4. **Privacidade:** Não compartilhe URLs ou dados sensíveis

## Autor

**Arthur Freitas**
Estudante de Criptografia e Blockchain
Residência Tecnológica - CPqD

## Suporte

Para reportar bugs ou solicitar features, abra uma issue no GitHub.

---

**Última atualização:** Dezembro 2024
