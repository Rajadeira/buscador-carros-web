import cloudscraper
from bs4 import BeautifulSoup
import json
import re

scraper = cloudscraper.create_scraper()
url = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Fusca&o=1'
resp = scraper.get(url, timeout=40)
soup = BeautifulSoup(resp.text, 'html.parser')

scripts = soup.find_all('script')
for script in scripts:
    if script.string and '__INITIAL_STATE__' in script.string:
        try:
            json_str = script.string.split('__INITIAL_STATE__=')[1].split(';\n')[0]
            data = json.loads(json_str)
            print('✅ JSON raiz encontrado. Chaves principais:')
            for key in data.keys():
                val = data[key]
                if isinstance(val, dict):
                    print(f'   {key}: dict com {len(val)} chaves -> {list(val.keys())[:10]}')
                elif isinstance(val, list):
                    print(f'   {key}: list com {len(val)} itens')
                    if len(val) > 0:
                        print(f'      primeiro item: {type(val[0])} -> {list(val[0].keys()) if isinstance(val[0], dict) else val[0]}')
                else:
                    print(f'   {key}: {type(val).__name__} = {str(val)[:100]}')
            break
        except:
            pass
