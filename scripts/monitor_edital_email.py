#!/usr/bin/env python3
"""
Monitor de Edital com Notificação por E-mail
Versão estendida com suporte a alertas por e-mail
"""

import requests
from bs4 import BeautifulSoup
import time
import hashlib
import sys
from datetime import datetime
from typing import Optional, Set
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class MonitorEditalComEmail:
    """Monitor de edital com notificação por e-mail"""
    
    def __init__(self, url: str, palavras_chave: Set[str], 
                 intervalo_minutos: int = 10,
                 email_config: Optional[dict] = None):
        """
        Inicializa o monitor com suporte a e-mail
        
        Args:
            url: URL da página do edital
            palavras_chave: Conjunto de palavras-chave
            intervalo_minutos: Intervalo entre checagens
            email_config: Configuração de e-mail (opcional)
        """
        self.url = url
        self.palavras_chave = {palavra.lower() for palavra in palavras_chave}
        self.intervalo_segundos = intervalo_minutos * 60
        self.hash_anterior: Optional[str] = None
        self.email_config = email_config
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
    
    def log_mensagem(self, mensagem: str, tipo: str = "INFO"):
        """Registra mensagem com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cores = {
            "INFO": "\033[94m", "ALERTA": "\033[93m",
            "ERRO": "\033[91m", "SUCESSO": "\033[92m", "RESET": "\033[0m"
        }
        cor = cores.get(tipo, cores["RESET"])
        print(f"{cor}[{timestamp}] [{tipo}] {mensagem}{cores['RESET']}")
    
    def enviar_email(self, assunto: str, corpo: str) -> bool:
        """
        Envia notificação por e-mail
        
        Args:
            assunto: Assunto do e-mail
            corpo: Corpo do e-mail
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.email_config:
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = self.email_config['remetente']
            msg['To'] = self.email_config['destinatario']
            
            # Versão HTML do e-mail
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif;">
                <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px;">
                  <h2 style="color: #d32f2f;">Alerta de Monitoramento de Edital</h2>
                  <hr style="border: 1px solid #ddd;">
                  <div style="background-color: white; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    {corpo}
                  </div>
                  <hr style="border: 1px solid #ddd; margin-top: 20px;">
                  <p style="color: #666; font-size: 12px;">
                    <strong>URL:</strong> <a href="{self.url}">{self.url}</a><br>
                    <strong>Data/Hora:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                  </p>
                </div>
              </body>
            </html>
            """
            
            parte_html = MIMEText(html, 'html')
            msg.attach(parte_html)
            
            # Conecta ao servidor SMTP
            with smtplib.SMTP(self.email_config['smtp_servidor'], 
                            self.email_config['smtp_porta']) as server:
                server.starttls()
                server.login(self.email_config['remetente'], 
                           self.email_config['senha'])
                server.send_message(msg)
            
            self.log_mensagem("E-mail de notificação enviado com sucesso", "SUCESSO")
            return True
            
        except Exception as e:
            self.log_mensagem(f"Erro ao enviar e-mail: {str(e)}", "ERRO")
            return False
    
    def calcular_hash(self, conteudo: str) -> str:
        """Calcula hash SHA-256 do conteúdo"""
        return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()
    
    def buscar_pagina(self) -> Optional[BeautifulSoup]:
        """Busca o conteúdo da página"""
        try:
            self.log_mensagem(f"Buscando página: {self.url}")
            response = requests.get(self.url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            self.log_mensagem(f"Erro ao buscar página: {str(e)}", "ERRO")
            return None
    
    def extrair_conteudo_relevante(self, soup: BeautifulSoup) -> str:
        """Extrai conteúdo relevante da página"""
        seletores = [
            'div.content', 'div.edital', 'div.resultado',
            'div.main-content', 'table', 'section.content',
            'article', 'div[class*="content"]', 'div[id*="content"]',
        ]
        
        conteudo_total = []
        for seletor in seletores:
            elementos = soup.select(seletor)
            for elemento in elementos:
                conteudo_total.append(elemento.get_text(strip=True))
        
        if not conteudo_total:
            body = soup.find('body')
            if body:
                conteudo_total.append(body.get_text(strip=True))
        
        return ' '.join(conteudo_total)
    
    def verificar_palavras_chave(self, conteudo: str) -> Set[str]:
        """Verifica palavras-chave no conteúdo"""
        conteudo_lower = conteudo.lower()
        return {palavra for palavra in self.palavras_chave if palavra in conteudo_lower}
    
    def exibir_alerta(self, palavras_encontradas: Set[str], mudanca_conteudo: bool):
        """Exibe alertas e envia e-mail se configurado"""
        print("\n" + "=" * 80)
        print("ALERTA " * 20)
        print("=" * 80)
        
        mensagens = []
        
        if palavras_encontradas:
            msg = f"PALAVRAS-CHAVE DETECTADAS: {', '.join(palavras_encontradas)}"
            self.log_mensagem(msg, "ALERTA")
            mensagens.append(f"<p><strong>Palavras-chave encontradas:</strong> {', '.join(palavras_encontradas)}</p>")
        
        if mudanca_conteudo:
            msg = "MUDANÇA NO CONTEÚDO DA PÁGINA DETECTADA!"
            self.log_mensagem(msg, "ALERTA")
            mensagens.append("<p><strong>Mudança detectada</strong> no conteúdo da página</p>")
        
        self.log_mensagem(f"Acesse: {self.url}", "SUCESSO")
        
        print("=" * 80)
        print("ALERTA " * 20)
        print("=" * 80 + "\n")
        
        # Emite beeps
        for _ in range(5):
            print('\a', end='', flush=True)
            time.sleep(0.3)
        
        # Envia e-mail se configurado
        if self.email_config and mensagens:
            assunto = "Alerta: Atualização no Edital"
            corpo = ''.join(mensagens)
            self.enviar_email(assunto, corpo)
    
    def monitorar(self):
        """Loop principal de monitoramento"""
        self.log_mensagem("Iniciando monitoramento de edital", "SUCESSO")
        self.log_mensagem(f"URL: {self.url}")
        self.log_mensagem(f"Palavras-chave: {', '.join(self.palavras_chave)}")
        self.log_mensagem(f"Intervalo: {self.intervalo_segundos // 60} minutos")
        
        if self.email_config:
            self.log_mensagem(f"Notificações por e-mail: ATIVADAS", "SUCESSO")
            self.log_mensagem(f"   Destinatário: {self.email_config['destinatario']}")
        else:
            self.log_mensagem("Notificações por e-mail: DESATIVADAS")
        
        print("\n" + "-" * 80 + "\n")
        
        iteracao = 0
        
        while True:
            try:
                iteracao += 1
                self.log_mensagem(f"Verificação #{iteracao}")
                
                soup = self.buscar_pagina()
                
                if soup is None:
                    self.log_mensagem(
                        "Falha ao buscar página. Tentando novamente no próximo ciclo...",
                        "ERRO"
                    )
                    time.sleep(self.intervalo_segundos)
                    continue
                
                conteudo = self.extrair_conteudo_relevante(soup)
                hash_atual = self.calcular_hash(conteudo)
                palavras_encontradas = self.verificar_palavras_chave(conteudo)
                
                mudanca_conteudo = False
                if self.hash_anterior is not None and hash_atual != self.hash_anterior:
                    mudanca_conteudo = True
                
                if palavras_encontradas or mudanca_conteudo:
                    self.exibir_alerta(palavras_encontradas, mudanca_conteudo)
                else:
                    self.log_mensagem("Nenhuma mudança detectada")
                
                self.hash_anterior = hash_atual
                
                proxima_checagem = datetime.now().timestamp() + self.intervalo_segundos
                proxima_checagem_str = datetime.fromtimestamp(proxima_checagem).strftime("%H:%M:%S")
                self.log_mensagem(f"Próxima verificação às {proxima_checagem_str}")
                print("-" * 80 + "\n")
                
                time.sleep(self.intervalo_segundos)
                
            except KeyboardInterrupt:
                print("\n")
                self.log_mensagem("Monitoramento interrompido pelo usuário", "ALERTA")
                sys.exit(0)
                
            except Exception as e:
                self.log_mensagem(f"Erro inesperado: {str(e)}", "ERRO")
                self.log_mensagem("Continuando monitoramento...", "INFO")
                time.sleep(self.intervalo_segundos)


def main():
    """Função principal"""
    
    # ========================================================================
    # CONFIGURAÇÕES BÁSICAS
    # ========================================================================
    
    URL_EDITAL = "https://fgduque.org.br/edital/projeto-asas-para-todos-ufersa-fgd-anac-edital-18-2024-1718822792"
    
    PALAVRAS_CHAVE = {
        "Resultado",
        "Resultado Final",
        "Resultado Preliminar",
        "Homologação",
        "Classificados",
        "Notas",
        "Segunda Etapa",
        "Convocação",
        "CMA",
    }
    
    INTERVALO_MINUTOS = 5
    
    # ========================================================================
    # CONFIGURAÇÕES DE E-MAIL (OPCIONAL)
    # ========================================================================
    # Para ativar notificações por e-mail, preencha as informações abaixo
    # e descomente o bloco EMAIL_CONFIG
    
    # EMAIL_CONFIG = {
    #     'remetente': 'seu_email@gmail.com',
    #     'senha': 'sua_senha_ou_app_password',  # Use App Password para Gmail
    #     'destinatario': 'destinatario@email.com',
    #     'smtp_servidor': 'smtp.gmail.com',
    #     'smtp_porta': 587
    # }
    
    EMAIL_CONFIG = None  # Deixe None para desativar e-mail
    
    # ========================================================================
    
    monitor = MonitorEditalComEmail(
        url=URL_EDITAL,
        palavras_chave=PALAVRAS_CHAVE,
        intervalo_minutos=INTERVALO_MINUTOS,
        email_config=EMAIL_CONFIG
    )
    
    monitor.monitorar()


if __name__ == "__main__":
    main()
