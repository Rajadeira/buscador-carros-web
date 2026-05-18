import cloudscraper
from bs4 import BeautifulSoup
import re

scraper = cloudscraper.create_scraper()
url = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Fusca&o=1'
resp = scraper.get(url, timeout=40)
soup = BeautifulSoup(resp.text, 'html.parser')

# Encontrar o primeiro link de anúncio
link = soup.find('a', href=re.compile(r'-\d{9,}'))
if link:
    parent = link.find_parent(['li', 'div', 'section'])
    if parent:
        with open('card_imagem.html', 'w', encoding='utf-8') as f:
            f.write(str(parent))
        print('✅ Card salvo em card_imagem.html')
        
        # Listar todas as tags img
        imgs = parent.find_all('img')
        print(f'\n🖼️ {len(imgs)} tags <img> encontradas:')
        for i, img in enumerate(imgs):
            print(f'   {i+1}. src={img.get("src", "")[:100]}')
            print(f'      data-src={img.get("data-src", "")[:100]}')
            print(f'      srcset={img.get("srcset", "")[:100]}')
        
        # Listar todos os atributos que contenham 'http' em qualquer tag
        print('\n🔗 Atributos com URL de imagem:')
        for tag in parent.find_all():
            for attr, val in tag.attrs.items():
                if isinstance(val, str) and ('http' in val and ('img' in val.lower() or 'image' in val.lower() or '.jpg' in val or '.png' in val)):
                    print(f'   <{tag.name}> {attr}: {val[:150]}')
    else:
        print('❌ Parent não encontrado')
else:
    print('❌ Link de anúncio não encontrado')
