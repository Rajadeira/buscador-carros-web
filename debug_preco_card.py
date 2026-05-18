import cloudscraper
from bs4 import BeautifulSoup
import re

scraper = cloudscraper.create_scraper()
url = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Fusca&o=1'
resp = scraper.get(url, timeout=20)
soup = BeautifulSoup(resp.text, 'html.parser')

# Encontrar o primeiro card com link de anúncio
link = soup.find('a', href=re.compile(r'-\d{9,}'))
if link:
    parent = link.find_parent(['li', 'div', 'section'])
    if parent:
        with open('card_fusca.html', 'w', encoding='utf-8') as f:
            f.write(str(parent))
        print('✅ Card salvo em card_fusca.html')

        # Mostrar todos os elementos que contenham "R$" e suas tags/classes
        print('\n🔍 Elementos com "R$" no card:')
        for elem in parent.find_all(string=re.compile(r'R\$')):
            print(f'  Tag: {elem.parent.name} | Classes: {elem.parent.get("class")} | Texto: {elem.strip()[:100]}')
        
        # Mostrar também atributos que possam conter preço
        for tag in parent.find_all():
            for attr, val in tag.attrs.items():
                if 'price' in attr.lower() or 'preco' in attr.lower() or (isinstance(val, str) and 'R$' in val):
                    print(f'  Atributo {attr} em <{tag.name}>: {val[:150]}')
    else:
        print('❌ Parent não encontrado')
else:
    print('❌ Nenhum link de anúncio encontrado')
