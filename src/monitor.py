#!/usr/bin/env python3
"""
Módulo de Monitoramento de Editais
Contém a lógica principal de monitoramento
"""

import requests
from bs4 import BeautifulSoup
import hashlib
from typing import Optional, Set, List
from datetime import datetime


class MonitorEdital:
    """Classe para monitoramento de editais públicos"""

    def __init__(self, url: str, palavras_chave: List[str], intervalo_minutos: int = 10):
        """
        Inicializa o monitor de edital

        Args:
            url: URL da página do edital a ser monitorada
            palavras_chave: Lista de palavras-chave para buscar
            intervalo_minutos: Intervalo entre checagens em minutos
        """
        self.url = url
        self.palavras_chave = [palavra.lower() for palavra in palavras_chave]
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

    def calcular_hash(self, conteudo: str) -> str:
        """Calcula hash SHA-256 do conteúdo"""
        return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()

    def buscar_pagina(self) -> Optional[BeautifulSoup]:
        """
        Busca o conteúdo da página

        Returns:
            Objeto BeautifulSoup com o conteúdo ou None em caso de erro
        """
        try:
            response = requests.get(self.url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao buscar página: {str(e)}")

    def extrair_conteudo_relevante(self, soup: BeautifulSoup) -> str:
        """Extrai conteúdo relevante da página"""
        seletores = [
            'div.content', 'div.edital', 'div.resultado',
            'div.main-content', 'table', 'section.content',
            'article', 'div[class*="content"]', 'div[id*="content"]'
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

    def verificar_palavras_chave(self, conteudo: str) -> List[str]:
        """Verifica palavras-chave no conteúdo"""
        conteudo_lower = conteudo.lower()
        palavras_encontradas = []

        for palavra in self.palavras_chave:
            if palavra in conteudo_lower:
                palavras_encontradas.append(palavra)

        return palavras_encontradas

    def verificar_mudancas(self, conteudo: str) -> tuple:
        """
        Verifica se houve mudanças no conteúdo

        Returns:
            Tupla (mudanca_detectada: bool, hash_atual: str)
        """
        hash_atual = self.calcular_hash(conteudo)
        mudanca = False

        if self.hash_anterior is not None and hash_atual != self.hash_anterior:
            mudanca = True

        self.hash_anterior = hash_atual
        return mudanca, hash_atual
