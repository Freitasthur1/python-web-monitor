#!/usr/bin/env python3
"""
Script de Teste Rápido - Monitor de Edital
Executa uma única verificação para testar a configuração
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime


def testar_conexao(url: str):
    """Testa a conexão com a URL do edital"""
    
    print("=" * 80)
    print("TESTE DE CONEXÃO E EXTRAÇÃO DE CONTEÚDO")
    print("=" * 80)
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Testando URL: {url}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                     '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        print("Enviando requisição HTTP...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        print(f"Conexão bem-sucedida! Status: {response.status_code}")
        print(f"Tamanho da resposta: {len(response.content)} bytes\n")

        print("Analisando HTML...")
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extrai títulos
        print("\nTÍTULOS ENCONTRADOS:")
        print("-" * 80)
        titulos = soup.find_all(['h1', 'h2', 'h3'])
        for i, titulo in enumerate(titulos[:5], 1):
            print(f"{i}. {titulo.get_text(strip=True)}")
        
        # Extrai todo o texto da página
        body = soup.find('body')
        if body:
            texto_completo = body.get_text(strip=True, separator=' ')
            
            print(f"\nCOMPRIMENTO DO TEXTO: {len(texto_completo)} caracteres")
            print("\nAMOSTRA DO CONTEÚDO (primeiros 500 caracteres):")
            print("-" * 80)
            print(texto_completo[:500])
            print("-" * 80)
            
            # Testa palavras-chave
            palavras_teste = [
                "resultado", "homologação", "classificados", 
                "notas", "convocação", "edital"
            ]
            
            print("\nTESTE DE PALAVRAS-CHAVE:")
            print("-" * 80)
            texto_lower = texto_completo.lower()
            
            encontradas = []
            for palavra in palavras_teste:
                if palavra in texto_lower:
                    encontradas.append(palavra)
                    print(f"[OK] '{palavra}' - ENCONTRADA")
                else:
                    print(f"[--] '{palavra}' - NÃO ENCONTRADA")
            
            print("\n" + "=" * 80)
            if encontradas:
                print(f"TESTE CONCLUÍDO: {len(encontradas)} palavra(s)-chave detectada(s)")
                print(f"   Palavras encontradas: {', '.join(encontradas)}")
            else:
                print("TESTE CONCLUÍDO: Nenhuma palavra-chave detectada")
                print("   Ajuste as palavras-chave no script principal se necessário")
            print("=" * 80)

        else:
            print("Não foi possível extrair o conteúdo da página")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("ERRO: Não foi possível conectar ao servidor")
        print("   Verifique sua conexão com a internet")
        return False

    except requests.exceptions.Timeout:
        print("ERRO: Timeout - o servidor demorou muito para responder")
        print("   Tente novamente mais tarde")
        return False

    except requests.exceptions.HTTPError as e:
        print(f"ERRO HTTP: {e}")
        print("   Verifique se a URL está correta")
        return False

    except Exception as e:
        print(f"ERRO INESPERADO: {str(e)}")
        return False


if __name__ == "__main__":
    # URL do edital para testar
    URL_TESTE = "https://fgduque.org.br/edital/projeto-asas-para-todos-ufersa-fgd-anac-edital-18-2024-1718822792"
    
    print("\n")
    sucesso = testar_conexao(URL_TESTE)
    print("\n")
    
    if sucesso:
        print("Teste concluído com sucesso!")
        print("Você pode executar o monitor completo com: python monitor_edital.py")
    else:
        print("Teste falhou. Corrija os erros antes de executar o monitor.")
    
    print("\n")
