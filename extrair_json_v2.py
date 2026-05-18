import json
import re
from bs4 import BeautifulSoup

with open('pagina_fusca.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')

for script in scripts:
    if script.string and 'adListExtendedFeatures' in script.string:
        texto = script.string
        # Encontrar todas as ocorrências de JSON objects no script
        # Vamos pegar a partir de '__NEXT_DATA__ ='
        start = texto.find('__NEXT_DATA__')
        if start != -1:
            # Encontrar o primeiro '{' após o sinal de igual
            eq = texto.find('=', start)
            bracket = texto.find('{', eq)
            if bracket != -1:
                # Contador de chaves para encontrar o fim do JSON
                count = 0
                end = bracket
                for i, ch in enumerate(texto[bracket:], start=bracket):
                    if ch == '{': count += 1
                    elif ch == '}': 
                        count -= 1
                        if count == 0:
                            end = i + 1
                            break
                json_str = texto[bracket:end]
                try:
                    data = json.loads(json_str)
                    print('✅ JSON extraído com sucesso!')
                    
                    # Função para procurar lista de anúncios e imagens
                    def explore(obj, depth=0):
                        if depth > 10: return
                        if isinstance(obj, dict):
                            for key, val in obj.items():
                                if key in ['adList', 'ads', 'listings', 'adListItems', 'items'] and isinstance(val, list) and len(val) > 0:
                                    print(f'\n🎯 Lista de anúncios encontrada em "{key}" com {len(val)} itens')
                                    first = val[0]
                                    if isinstance(first, dict):
                                        print(f'   Chaves do anúncio: {list(first.keys())[:20]}')
                                        # Procurar campos de imagem
                                        for k in first.keys():
                                            if any(t in k.lower() for t in ['image', 'photo', 'thumb', 'picture', 'img']):
                                                print(f'   🖼️ {k}: {first[k]}')
                                    return
                                explore(val, depth+1)
                        elif isinstance(obj, list):
                            for item in obj:
                                explore(item, depth+1)
                    
                    # Explorar a partir da raiz
                    print('Chaves raiz:', list(data.keys()))
                    # Primeiro tenta props.pageProps.ads ou similar
                    if 'props' in data:
                        explore(data['props'])
                    elif 'pageProps' in data:
                        explore(data['pageProps'])
                    else:
                        explore(data)
                    
                except json.JSONDecodeError as e:
                    print(f'JSON inválido: {e}')
                    print('Trecho:', json_str[:200])
        break
