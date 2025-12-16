# Monitor de Editais Públicos v2.0

Sistema de monitoramento automatizado de páginas web de editais públicos, com interface web, notificações por email e detecção inteligente de mudanças.

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Características Principais

- Interface web moderna e responsiva com sidebar
- Dashboard em tempo real com métricas visuais
- Sistema de notificações por email (Gmail, Outlook, etc.)
- Detecção inteligente por palavras-chave
- Monitoramento contínuo com hash SHA-256
- API REST completa para integração
- Logs em tempo real com código de cores
- Arquitetura modular e organizada
- Pronto para deploy em produção

## Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/monitoramento-ufersa.git
cd monitoramento-ufersa

# 2. Instale as dependências
pip3 install -r requirements.txt

# 3. Inicie o servidor
./start.sh
```

Acesse: **http://localhost:5000**

## Estrutura do Projeto

```
monitoramento-ufersa/
├── src/                      # Código fonte
│   ├── app.py               # Aplicação Flask principal
│   ├── monitor.py           # Lógica de monitoramento
│   └── email_notifier.py    # Sistema de email
├── templates/               # Templates HTML
├── static/                  # CSS, JavaScript, imagens
├── config/                  # Arquivos de configuração
├── scripts/                 # Scripts utilitários
├── docs/                    # Documentação completa
├── logs/                    # Logs da aplicação
├── tests/                   # Testes automatizados
├── run.py                   # Entry point
├── start.sh                 # Script de inicialização
└── requirements.txt         # Dependências

```

## Funcionalidades

### Interface Web
- **Dashboard**: Métricas em tempo real, status do sistema
- **Controles**: Iniciar/parar monitoramento
- **Configurações**: URL, palavras-chave, intervalo
- **Email**: Configuração completa de notificações SMTP
- **Logs**: Visualização em tempo real com cores

### Notificações por Email
- Suporte para Gmail, Outlook e outros provedores SMTP
- Templates HTML profissionais
- Envio automático quando mudanças são detectadas
- Sistema de teste de configuração

### API REST
- `GET /api/status` - Status do monitoramento
- `GET /api/logs` - Logs recentes
- `GET /api/config` - Configuração atual
- `POST /api/config` - Atualizar configuração
- `POST /api/start` - Iniciar monitoramento
- `POST /api/stop` - Parar monitoramento
- `POST /api/test-email` - Testar email

## Documentação Completa

Para documentação completa, consulte:

- **[INSTALL.md](docs/INSTALL.md)** - Guia completo de instalação
- **[README.md](docs/README.md)** - Documentação técnica detalhada
- **[GUIA_RAPIDO.txt](docs/GUIA_RAPIDO.txt)** - Guia rápido de uso

## Uso Básico

### 1. Configurar via Interface Web

1. Acesse http://localhost:5000
2. Vá em "Configurações"
3. Digite a URL do edital
4. Adicione palavras-chave (uma por linha)
5. Defina o intervalo de verificação
6. Clique em "Salvar Configurações"

### 2. Configurar Notificações por Email

1. Vá em "Notificações Email"
2. Marque "Ativar notificações por email"
3. Preencha os dados SMTP
4. Clique em "Enviar Email de Teste"
5. Salve as configurações

### 3. Iniciar Monitoramento

1. Vá em "Controles"
2. Clique em "Iniciar Monitoramento"
3. Acompanhe os logs em tempo real

## Deploy em Produção

### Como Servidor (24/7)

```bash
# Usando systemd (recomendado)
sudo cp scripts/monitor-edital.service /etc/systemd/system/
sudo systemctl enable monitor-edital
sudo systemctl start monitor-edital
```

### Com Gunicorn

```bash
pip3 install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

## Tecnologias Utilizadas

- **Backend**: Python 3.7+, Flask, BeautifulSoup4
- **Frontend**: HTML5, CSS3 (Grid/Flexbox), Vanilla JavaScript
- **Email**: SMTP, MIME
- **Parsing**: lxml, requests

## Segurança

- Firewall configurável
- Suporte para HTTPS via proxy reverso
- Senhas SMTP criptografadas
- Validação de entrada
- Rate limiting recomendado

## Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja [LICENSE](docs/LICENSE) para mais detalhes.

## Autor

**Arthur Freitas**
Residente de Criptografia aplicada às tecnologias Blockchain - CPqD

## Suporte

- Documentação: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/seu-usuario/monitoramento-ufersa/issues)

---

**Versão 2.0** - Dezembro 2025
