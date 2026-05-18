from bs4 import BeautifulSoup
import re

with open('card_fusca.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

for tag in soup.find_all():
    for attr, val in tag.attrs.items():
        if isinstance(val, str):
            nums = re.findall(r'\b(\d{1,3}(?:\.\d{3})+)\b', val)
            if nums:
                print(f'Tag: <{tag.name}> Atributo: {attr}  Valores: {nums}')
            if 'R$' in val:
                print(f'Tag: <{tag.name}> Atributo: {attr} contém R$: {val[:150]}')

texto = soup.get_text(' ', strip=True)
print('\n📋 Texto completo do card:')
print(texto[:500])
