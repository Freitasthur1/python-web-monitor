#!/usr/bin/env python3
"""
Módulo de Notificação por Email
Envia alertas quando mudanças são detectadas
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

# Timezone de Brasília
BRASILIA_TZ = ZoneInfo("America/Sao_Paulo")

def get_brasilia_time():
    """Retorna o datetime atual no horário de Brasília"""
    return datetime.now(BRASILIA_TZ)


class EmailNotifier:
    """Classe para envio de notificações por email"""

    def __init__(self, smtp_config: dict):
        """
        Inicializa o notificador de email

        Args:
            smtp_config: Dicionário com configurações SMTP
                {
                    'enabled': bool,
                    'smtp_server': str,
                    'smtp_port': int,
                    'smtp_user': str,
                    'smtp_password': str,
                    'from_email': str,
                    'to_email': str,
                    'use_tls': bool
                }
        """
        self.enabled = smtp_config.get('enabled', False)
        self.smtp_server = smtp_config.get('smtp_server', '')
        self.smtp_port = smtp_config.get('smtp_port', 587)
        self.smtp_user = smtp_config.get('smtp_user', '')
        self.smtp_password = smtp_config.get('smtp_password', '')
        self.from_email = smtp_config.get('from_email', '')
        self.to_email = smtp_config.get('to_email', '')
        self.use_tls = smtp_config.get('use_tls', True)

    def enviar_alerta(
        self,
        url: str,
        palavras_encontradas: List[str],
        mudanca_conteudo: bool,
        destinatarios: Optional[List[str]] = None
    ) -> bool:
        """
        Envia email de alerta

        Args:
            url: URL do edital
            palavras_encontradas: Lista de palavras-chave encontradas
            mudanca_conteudo: Se houve mudança no conteúdo
            destinatarios: Lista opcional de emails destinatários (se None, usa to_email)

        Returns:
            True se enviou com sucesso, False caso contrário
        """
        if not self.enabled:
            return False

        # Usa lista de destinatários ou email padrão
        emails_destino = destinatarios if destinatarios else [self.to_email]

        if not emails_destino:
            return False

        try:
            # Envia para cada destinatário
            enviados = 0
            for email_destino in emails_destino:
                if not email_destino or '@' not in email_destino:
                    continue

                # Cria mensagem
                msg = MIMEMultipart('alternative')
                msg['Subject'] = f'[Monitor de Editais] Alerta Detectado - {get_brasilia_time().strftime("%d/%m/%Y %H:%M")}'
                msg['From'] = self.from_email
                msg['To'] = email_destino

                # Corpo do email
                texto = self._criar_corpo_texto(url, palavras_encontradas, mudanca_conteudo)
                html = self._criar_corpo_html(url, palavras_encontradas, mudanca_conteudo)

                parte_texto = MIMEText(texto, 'plain', 'utf-8')
                parte_html = MIMEText(html, 'html', 'utf-8')

                msg.attach(parte_texto)
                msg.attach(parte_html)

                # Envia email
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.use_tls:
                        server.starttls()

                    if self.smtp_user and self.smtp_password:
                        server.login(self.smtp_user, self.smtp_password)

                    server.send_message(msg)
                    enviados += 1

            return enviados > 0

        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")
            return False

    def _criar_corpo_texto(
        self,
        url: str,
        palavras_encontradas: List[str],
        mudanca_conteudo: bool
    ) -> str:
        """Cria corpo de texto simples do email"""
        linhas = [
            "ALERTA DO MONITOR DE EDITAIS",
            "=" * 50,
            "",
            f"Data/Hora: {get_brasilia_time().strftime('%d/%m/%Y %H:%M:%S')}",
            f"URL: {url}",
            ""
        ]

        if palavras_encontradas:
            linhas.append("Palavras-chave detectadas:")
            for palavra in palavras_encontradas:
                linhas.append(f"  - {palavra}")
            linhas.append("")

        if mudanca_conteudo:
            linhas.append("MUDANÇA NO CONTEÚDO DA PÁGINA DETECTADA!")
            linhas.append("")

        linhas.extend([
            "Acesse a URL acima para verificar as alterações.",
            "",
            "---",
            "Monitor de Editais Públicos",
            "Sistema automatizado de monitoramento"
        ])

        return "\n".join(linhas)

    def _criar_corpo_html(
        self,
        url: str,
        palavras_encontradas: List[str],
        mudanca_conteudo: bool
    ) -> str:
        """Cria corpo HTML do email"""
        palavras_html = ""
        if palavras_encontradas:
            palavras_html = "<ul>"
            for palavra in palavras_encontradas:
                palavras_html += f"<li><strong>{palavra}</strong></li>"
            palavras_html += "</ul>"

        mudanca_html = ""
        if mudanca_conteudo:
            mudanca_html = """
            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 15px 0;">
                <strong>MUDANÇA NO CONTEÚDO DA PÁGINA DETECTADA!</strong>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px; }}
                .info-box {{ background: white; padding: 15px; margin: 15px 0; border-radius: 6px; border-left: 4px solid #3498db; }}
                .button {{ display: inline-block; background: #27ae60; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 15px 0; }}
                .footer {{ text-align: center; color: #7f8c8d; padding: 20px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Alerta do Monitor de Editais</h1>
                    <p>{get_brasilia_time().strftime('%d/%m/%Y às %H:%M:%S')}</p>
                </div>
                <div class="content">
                    {mudanca_html}

                    {f'<div class="info-box"><h3>Palavras-chave Detectadas:</h3>{palavras_html}</div>' if palavras_encontradas else ''}

                    <div class="info-box">
                        <h3>URL Monitorada:</h3>
                        <p><a href="{url}" style="color: #3498db; word-break: break-all;">{url}</a></p>
                    </div>

                    <center>
                        <a href="{url}" class="button">Acessar Página do Edital</a>
                    </center>
                </div>
                <div class="footer">
                    <p>Monitor de Editais Públicos</p>
                    <p>Sistema automatizado de monitoramento</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def testar_conexao(self) -> tuple:
        """
        Testa conexão SMTP

        Returns:
            Tupla (sucesso: bool, mensagem: str)
        """
        if not self.enabled:
            return False, "Notificações por email desabilitadas"

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()

                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

            return True, "Conexão SMTP bem-sucedida"

        except Exception as e:
            return False, f"Erro na conexão SMTP: {str(e)}"
