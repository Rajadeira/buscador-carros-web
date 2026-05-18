import requests
from bs4 import BeautifulSoup
import re

print("=" * 60)
print("🔍 TESTE: WEBMOTORS RSS FEED")
print("=" * 60)

headers = {'User-Agent': 'Mozilla/5.0'}

# Tentar o feed/sitemap da WebMotors
urls_teste = [
    "https://www.webmotors.com.br/sitemap.xml",
    "https://www.webmotors.com.br/robots.txt",
]

for url in urls_teste:
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"\n{url}")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Conteúdo: {resp.text[:300]}")
    except Exception as e:
        print(f"Erro: {e}")

print("\n" + "=" * 60)
print("🔍 TESTE: GOOGLE CUSTOM SEARCH (alternativa)")
print("=" * 60)
print("Se nada funcionar, podemos usar:")
print("1. Tabela FIPE oficial (já funciona)")
print("2. Dados manuais de mercado")
print("3. CSV/planilhas públicas de preços")
