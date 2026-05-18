from bs4 import BeautifulSoup
import json
import re

with open('pagina_fusca.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')

for i, script in enumerate(scripts):
    if script.string and 'adListExtendedFeatures' in script.string:
        # Extrair o JSON completo do __NEXT_DATA__
        match = re.search(r'__NEXT_DATA__\s*=\s*({.*?});\s*module', script.string, re.DOTALL)
        if match:
            json_str = match.group(1)
            data = json.loads(json_str)
            print('✅ JSON extraído com sucesso')
            
            # Navegar pela estrutura procurando listas de anúncios
            def find_ads(obj, path=''):
                if isinstance(obj, dict):
                    for key, val in obj.items():
                        new_path = f'{path}.{key}'
                        if key in ['adList', 'ads', 'listings', 'adListItems']:
                            print(f'\n🎯 Encontrada chave "{key}" em {new_path}')
                            if isinstance(val, list):
                                print(f'   Itens: {len(val)}')
                                if len(val) > 0:
                                    print(f'   Chaves do 1º item: {list(val[0].keys()) if isinstance(val[0], dict) else "não é dict"}')
                                    # Procurar imagens no primeiro item
                                    if isinstance(val[0], dict):
                                        for k in val[0].keys():
                                            if any(term in k.lower() for term in ['image', 'photo', 'thumb', 'picture']):
                                                print(f'   🖼️ {k}: {val[0][k]}')
                            return True
                        if find_ads(val, new_path):
                            return True
                elif isinstance(obj, list):
                    for idx, item in enumerate(obj):
                        if find_ads(item, f'{path}[{idx}]'):
                            return True
                return False
            
            if not find_ads(data):
                print('\n❌ Nenhuma lista de anúncios encontrada no JSON')
                print('Chaves do nível raiz:')
                for key in data.keys():
                    print(f'   {key}: {type(data[key]).__name__}', end='')
                    if isinstance(data[key], dict):
                        print(f' -> {list(data[key].keys())[:10]}')
                    else:
                        print()
        else:
            print('Não foi possível extrair o JSON')
        break
