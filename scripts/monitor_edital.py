#!/usr/bin/env python3
"""
Script de Monitoramento de Editais Públicos
Autor: Arthur
Descrição: Monitora página web de editais em busca de novos resultados
"""

import requests
from bs4 import BeautifulSoup
import time
import hashlib
import sys
import os
from datetime import datetime
from typing import Optional, Set


class MonitorEdital:
    """Classe para monitoramento de editais públicos"""
    
    def __init__(self, url: str, palavras_chave: Set[str], intervalo_minutos: int = 10):
        """
        Inicializa o monitor de edital
        
        Args:
            url: URL da página do edital a ser monitorada
            palavras_chave: Conjunto de palavras-chave para buscar
            intervalo_minutos: Intervalo entre checagens em minutos
        """
        self.url = url
        self.palavras_chave = {palavra.lower() for palavra in palavras_chave}
        self.intervalo_segundos = intervalo_minutos * 60
        self.hash_anterior: Optional[str] = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
    
    def beep_system(self, quantidade: int = 3):
        """
        Emite beep do sistema
        
        Args:
            quantidade: Número de beeps a emitir
        """
        for _ in range(quantidade):
            # Beep do sistema (funciona em Linux/Unix/Mac)
            print('\a', end='', flush=True)
            time.sleep(0.3)
    
    def log_mensagem(self, mensagem: str, tipo: str = "INFO"):
        """
        Registra mensagem com timestamp
        
        Args:
            mensagem: Mensagem a ser registrada
            tipo: Tipo da mensagem (INFO, ALERTA, ERRO)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Cores ANSI para terminal
        cores = {
            "INFO": "\033[94m",      # Azul
            "ALERTA": "\033[93m",    # Amarelo
            "ERRO": "\033[91m",      # Vermelho
            "SUCESSO": "\033[92m",   # Verde
            "RESET": "\033[0m"
        }
        
        cor = cores.get(tipo, cores["RESET"])
        print(f"{cor}[{timestamp}] [{tipo}] {mensagem}{cores['RESET']}")
    
    def calcular_hash(self, conteudo: str) -> str:
        """
        Calcula hash SHA-256 do conteúdo
        
        Args:
            conteudo: Conteúdo para calcular hash
            
        Returns:
            Hash SHA-256 em hexadecimal
        """
        return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()
    
    def buscar_pagina(self) -> Optional[BeautifulSoup]:
        """
        Busca o conteúdo da página
        
        Returns:
            Objeto BeautifulSoup com o conteúdo ou None em caso de erro
        """
        try:
            self.log_mensagem(f"Buscando página: {self.url}")
            
            response = requests.get(
                self.url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.exceptions.RequestException as e:
            self.log_mensagem(f"Erro ao buscar página: {str(e)}", "ERRO")
            return None
    
    def extrair_conteudo_relevante(self, soup: BeautifulSoup) -> str:
        """
        Extrai conteúdo relevante da página (divs, tables, sections)
        
        Args:
            soup: Objeto BeautifulSoup
            
        Returns:
            Texto do conteúdo relevante
        """
        # Seletores comuns para conteúdo de editais
        seletores = [
            'div.content',
            'div.edital',
            'div.resultado',
            'div.main-content',
            'table',
            'section.content',
            'article',
            'div[class*="content"]',
            'div[id*="content"]',
        ]
        
        conteudo_total = []
        
        # Tenta diferentes seletores
        for seletor in seletores:
            elementos = soup.select(seletor)
            for elemento in elementos:
                conteudo_total.append(elemento.get_text(strip=True))
        
        # Se não encontrou nada com seletores específicos, usa o body
        if not conteudo_total:
            body = soup.find('body')
            if body:
                conteudo_total.append(body.get_text(strip=True))
        
        return ' '.join(conteudo_total)
    
    def verificar_palavras_chave(self, conteudo: str) -> Set[str]:
        """
        Verifica se palavras-chave estão presentes no conteúdo
        
        Args:
            conteudo: Conteúdo a ser verificado
            
        Returns:
            Conjunto de palavras-chave encontradas
        """
        conteudo_lower = conteudo.lower()
        palavras_encontradas = set()
        
        for palavra in self.palavras_chave:
            if palavra in conteudo_lower:
                palavras_encontradas.add(palavra)
        
        return palavras_encontradas
    
    def exibir_alerta(self, palavras_encontradas: Set[str], mudanca_conteudo: bool):
        """
        Exibe alerta visual quando mudanças são detectadas
        
        Args:
            palavras_encontradas: Palavras-chave encontradas
            mudanca_conteudo: Se houve mudança no conteúdo
        """
        print("\n" + "=" * 80)
        print("[ALERTA] " * 8)
        print("=" * 80)
        
        if palavras_encontradas:
            self.log_mensagem(
                f"PALAVRAS-CHAVE DETECTADAS: {', '.join(palavras_encontradas)}",
                "ALERTA"
            )
        
        if mudanca_conteudo:
            self.log_mensagem("MUDANÇA NO CONTEÚDO DA PÁGINA DETECTADA!", "ALERTA")
        
        self.log_mensagem(f"Acesse: {self.url}", "SUCESSO")
        
        print("=" * 80)
        print("[ALERTA] " * 8)
        print("=" * 80 + "\n")
        
        # Emite beeps
        self.beep_system(5)
    
    def monitorar(self):
        """
        Loop principal de monitoramento
        """
        self.log_mensagem("Iniciando monitoramento de edital", "SUCESSO")
        self.log_mensagem(f"URL: {self.url}")
        self.log_mensagem(f"Palavras-chave: {', '.join(self.palavras_chave)}")
        self.log_mensagem(f"Intervalo: {self.intervalo_segundos // 60} minutos")
        print("\n" + "-" * 80 + "\n")
        
        iteracao = 0
        
        while True:
            try:
                iteracao += 1
                self.log_mensagem(f"Verificação #{iteracao}")
                
                # Busca a página
                soup = self.buscar_pagina()
                
                if soup is None:
                    self.log_mensagem(
                        "Falha ao buscar página. Tentando novamente no próximo ciclo...",
                        "ERRO"
                    )
                    time.sleep(self.intervalo_segundos)
                    continue
                
                # Extrai conteúdo relevante
                conteudo = self.extrair_conteudo_relevante(soup)
                
                # Calcula hash do conteúdo
                hash_atual = self.calcular_hash(conteudo)
                
                # Verifica palavras-chave
                palavras_encontradas = self.verificar_palavras_chave(conteudo)
                
                # Verifica mudanças
                mudanca_conteudo = False
                if self.hash_anterior is not None and hash_atual != self.hash_anterior:
                    mudanca_conteudo = True
                
                # Emite alerta se necessário
                if palavras_encontradas or mudanca_conteudo:
                    self.exibir_alerta(palavras_encontradas, mudanca_conteudo)
                else:
                    self.log_mensagem("Nenhuma mudança detectada")
                
                # Atualiza hash anterior
                self.hash_anterior = hash_atual
                
                # Aguarda próximo ciclo
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
    # CONFIGURAÇÕES - PERSONALIZE AQUI
    # ========================================================================
    
    # URL do edital a ser monitorado
    URL_EDITAL = "https://fgduque.org.br/edital/projeto-asas-para-todos-ufersa-fgd-anac-edital-18-2024-1718822792"
    
    # Palavras-chave a serem monitoradas (não diferencia maiúsculas/minúsculas)
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
    
    # Intervalo entre verificações (em minutos)
    INTERVALO_MINUTOS = 10
    
    # ========================================================================
    
    # Cria e inicia o monitor
    monitor = MonitorEdital(
        url=URL_EDITAL,
        palavras_chave=PALAVRAS_CHAVE,
        intervalo_minutos=INTERVALO_MINUTOS
    )
    
    monitor.monitorar()


if __name__ == "__main__":
    main()
