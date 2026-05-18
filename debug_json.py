import cloudscraper
from bs4 import BeautifulSoup
import json
import re

scraper = cloudscraper.create_scraper()
url = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Fusca&o=1'
resp = scraper.get(url, timeout=40)
soup = BeautifulSoup(resp.text, 'html.parser')

scripts = soup.find_all('script')
json_data = None
for script in scripts:
    if script.string and '__INITIAL_STATE__' in script.string:
        try:
            json_str = script.string.split('__INITIAL_STATE__=')[1].split(';\n')[0]
            data = json.loads(json_str)
            # Salvar apenas a parte de anúncios
            ads = data.get('listingProps', {}).get('adList', [])
            if ads:
                json_data = ads
            else:
                # Tentar outros caminhos
                for key in data.keys():
                    if 'ad' in key.lower() or 'list' in key.lower():
                        print(f'Chave candidata: {key}')
        except:
            pass

if json_data:
    with open('json_ads.json', 'w', encoding='utf-8') as f:
        json.dump(json_data[:5], f, indent=2, ensure_ascii=False)  # primeiros 5 anúncios
    print(f'✅ JSON salvo em json_ads.json com {len(json_data)} anúncios')
    
    # Mostrar as chaves do primeiro anúncio
    if json_data:
        print('\n📋 Chaves do primeiro anúncio:')
        for key in json_data[0].keys():
            print(f'   {key}: {type(json_data[0][key])}')
        
        # Procurar por chaves que contenham 'image' ou 'photo' ou 'picture'
        ad = json_data[0]
        for key in ad.keys():
            if 'image' in key.lower() or 'photo' in key.lower() or 'picture' in key.lower() or 'thumb' in key.lower():
                print(f'\n🖼️ Chave de imagem: {key} = {ad[key]}')
else:
    print('❌ Não foi possível extrair JSON de anúncios')
