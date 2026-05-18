import cloudscraper
from bs4 import BeautifulSoup
import re

scraper = cloudscraper.create_scraper()

# URL de um anúncio real (o primeiro que encontramos antes)
url_anuncio = 'https://sp.olx.com.br/sao-paulo-e-regiao/autos-e-pecas/carros-vans-e-utilitarios/honda-civic-sedan-ex-2-0-flex-16v-aut-4p-2018-1501809534'

resp = scraper.get(url_anuncio, timeout=20)
soup = BeautifulSoup(resp.text, 'html.parser')

print(f"Status: {resp.status_code}")

# 1. Procurar meta tags de preço (muito comuns em sites de classificados)
meta_preco = soup.find('meta', itemprop='price') or soup.find('meta', property='product:price:amount')
if meta_preco:
    print(f"✅ Meta preço: {meta_preco.get('content')}")

# 2. Procurar spans/divs com classes típicas de preço
for classe in ['price', 'preco', 'olx-text--heading-2', 'sc-ifAKCX', 'ad__price', 'actual-price']:
    elem = soup.find(['span', 'div', 'h2'], class_=re.compile(classe, re.IGNORECASE))
    if elem:
        texto = elem.get_text(strip=True)
        print(f"✅ Elemento com classe '{classe}': {texto}")

# 3. Procurar qualquer texto "R$" na página e mostrar o contexto
textos_r = soup.find_all(string=re.compile(r'R\$\s*[\d.]+'))
print(f"\n💰 Trechos com 'R$' encontrados: {len(textos_r)}")
for t in textos_r[:5]:
    print(f"   {t.strip()[:100]}")

# 4. Salvar HTML para análise
with open('anuncio_olx.html', 'w', encoding='utf-8') as f:
    f.write(resp.text)
print("\n✅ HTML do anúncio salvo em anuncio_olx.html")
