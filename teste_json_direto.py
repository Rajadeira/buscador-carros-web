import cloudscraper
from bs4 import BeautifulSoup
import json, re

scraper = cloudscraper.create_scraper()
url = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Fusca&o=1'
resp = scraper.get(url, timeout=40)
soup = BeautifulSoup(resp.text, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__')
if script:
    data = json.loads(script.string)
    ads = data.get('props', {}).get('pageProps', {}).get('ads', [])
    if ads:
        ad = ads[0]
        props = ad.get('properties', [])
        ano = 0
        for p in props:
            if p.get('name') == 'regdate':
                ano_str = p.get('value', '')
                ano = int(re.search(r'\d{4}', str(ano_str)).group()) if re.search(r'\d{4}', str(ano_str)) else 0
                break
        images = ad.get('images', [])
        foto = images[0].get('original') if images else ''
        print(f"Título: {ad.get('title')}")
        print(f"Preço: {ad.get('priceValue')}")
        print(f"Ano extraído: {ano}")
        print(f"Foto: {foto}")
    else:
        print("Nenhum anúncio encontrado no JSON")
else:
    print("Script __NEXT_DATA__ não encontrado")
