import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Honda+Civic&ps=100000'

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'pt-BR,pt;q=0.9'
}

print(f'🔍 OLX Mobile: {url}')
resp = requests.get(url, headers=headers, timeout=15)
print(f'Status: {resp.status_code}')

if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('a', href=re.compile(r'-\d{9,}'))
    print(f'Links de anúncios: {len(links)}')
    for link in links[:5]:
        print(f'  {link.get("href")}')
else:
    print('❌ Bloqueado até no mobile')
