# Guia de Instalação Rápida

## Instalação Local

### 1. Instale as dependências do sistema

```bash
sudo apt update
sudo apt install python3 python3-pip git
```

### 2. Clone o repositório

```bash
git clone https://github.com/seu-usuario/monitoramento-ufersa.git
cd monitoramento-ufersa
```

### 3. Instale as dependências Python

```bash
pip3 install -r requirements.txt
```

### 4. Configure o sistema

```bash
cp config.json.example config.json
nano config.json
```

Edite a URL do edital e as palavras-chave conforme necessário.

### 5. Inicie o servidor

```bash
./start_server.sh
```

Ou:

```bash
python3 app.py
```

### 6. Acesse a interface

Abra seu navegador em: http://localhost:5000

## Deploy como Servidor (24/7)

### Opção 1: Execução em Background

```bash
nohup python3 app.py > server.log 2>&1 &
```

Para verificar se está rodando:

```bash
ps aux | grep app.py
```

Para parar:

```bash
pkill -f app.py
```

### Opção 2: Serviço Systemd (Recomendado)

1. Crie o arquivo de serviço:

```bash
sudo nano /etc/systemd/system/monitor-edital.service
```

2. Cole o conteúdo (ajuste os caminhos):

```ini
[Unit]
Description=Monitor de Editais
After=network.target

[Service]
Type=simple
User=SEU_USUARIO
WorkingDirectory=/caminho/completo/para/monitoramento-ufersa
ExecStart=/usr/bin/python3 /caminho/completo/para/monitoramento-ufersa/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Ative e inicie:

```bash
sudo systemctl daemon-reload
sudo systemctl enable monitor-edital
sudo systemctl start monitor-edital
```

4. Verifique status:

```bash
sudo systemctl status monitor-edital
```

5. Ver logs:

```bash
sudo journalctl -u monitor-edital -f
```

## Acesso Externo

### Configurar Firewall

```bash
sudo ufw allow 5000/tcp
```

### Encontrar seu IP local

```bash
hostname -I
```

Acesse de outros dispositivos na rede: http://SEU_IP:5000

### Acesso pela Internet

#### Opção 1: Port Forwarding no Roteador

1. Acesse as configurações do seu roteador (geralmente 192.168.1.1)
2. Configure port forwarding da porta 5000 para o IP local da máquina
3. Use seu IP público para acessar (descubra em: https://meuip.com.br)

#### Opção 2: Túnel Reverso com ngrok

```bash
# Instale ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Execute
ngrok http 5000
```

O ngrok fornecerá uma URL pública temporária.

## Solução de Problemas

### Porta 5000 já em uso

```bash
# Descubra o processo
lsof -i :5000

# Mate o processo
kill -9 PID
```

### Permissão negada ao executar start_server.sh

```bash
chmod +x start_server.sh
```

### Dependências não instalam

```bash
# Use ambiente virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuração Adicional

### Executar na inicialização do sistema

Já configurado se usar systemd.

### Alterar porta do servidor

Edite `config.json`:

```json
{
    "servidor_porta": 8080
}
```

### Logs

Logs são exibidos na interface web em tempo real e também no terminal/systemd.

## Próximos Passos

1. Acesse a interface web
2. Configure URL e palavras-chave via interface
3. Clique em "Iniciar Monitoramento"
4. Acompanhe os logs em tempo real

## Segurança

Para produção, recomenda-se:

1. Usar HTTPS (nginx com SSL)
2. Adicionar autenticação
3. Configurar firewall adequadamente
4. Usar domínio próprio

Veja o README.md para instruções detalhadas de segurança.
