import requests
import urllib.parse
import re

marca = 'Honda'
modelo = 'Civic'
query = f'{marca} {modelo} 2020 site:olx.com.br'
url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f'🔍 DuckDuckGo: {url}')
resp = requests.get(url, headers=headers, timeout=15)
print(f'Status: {resp.status_code}')

if resp.status_code == 200:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('a', class_='result__a')
    print(f'Links encontrados: {len(links)}')
    
    anuncios = []
    for link in links:
        href = link.get('href', '')
        if 'olx.com.br' in href and re.search(r'-\d{9,}', href):
            anuncios.append(href)
    
    print(f'Anúncios OLX: {len(anuncios)}')
    for a in anuncios[:5]:
        print(f'  {a}')
else:
    print(f'❌ Falhou')
