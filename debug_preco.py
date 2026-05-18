import cloudscraper
from bs4 import BeautifulSoup
import re

scraper = cloudscraper.create_scraper()
url = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Honda+Civic&ps=100000'
resp = scraper.get(url, timeout=20)
soup = BeautifulSoup(resp.text, 'html.parser')

# Encontrar o primeiro card que contenha um link de anúncio
link = soup.find('a', href=re.compile(r'-\d{9,}'))
if link:
    parent = link.find_parent(['li', 'div', 'section'])
    if parent:
        # Salvar o HTML do card em um arquivo
        with open('card_olx.html', 'w', encoding='utf-8') as f:
            f.write(str(parent))
        print("✅ HTML do card salvo em card_olx.html")
        
        # Mostrar todos os textos do card
        print("\n📋 Textos encontrados no card:")
        for elem in parent.find_all(text=True):
            texto = elem.strip()
            if texto:
                print(f"  - {texto[:100]}")
        
        # Mostrar elementos que contêm "R$"
        print("\n💰 Elementos com 'R$':")
        for elem in parent.find_all(string=re.compile(r'R\$')):
            print(f"  Tag: {elem.parent.name}, Classes: {elem.parent.get('class')}, Texto: {elem.strip()[:100]}")
    else:
        print("❌ Não encontrou parent")
else:
    print("❌ Nenhum link de anúncio encontrado")
