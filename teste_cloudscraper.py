import cloudscraper
from bs4 import BeautifulSoup
import re

scraper = cloudscraper.create_scraper()

url = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Honda+Civic&ps=100000'
print(f'🔍 Tentando com cloudscraper...')
resp = scraper.get(url, timeout=15)
print(f'Status: {resp.status_code}')

if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Procurar links de anúncios
    links = soup.find_all('a', href=re.compile(r'-\d{9,}'))
    print(f'Links encontrados: {len(links)}')
    
    for link in links[:10]:
        href = link.get('href', '')
        if href.startswith('/'):
            href = 'https://www.olx.com.br' + href
        
        # Tentar pegar título
        titulo = link.get_text(strip=True)
        if not titulo or len(titulo) < 10:
            parent = link.find_parent(['li', 'div'])
            if parent:
                titulo = parent.get_text(strip=True)[:150]
        
        print(f'\n📋 {titulo[:100] if titulo else "Sem título"}')
        print(f'🔗 {href[:150]}')
else:
    print(f'❌ Status: {resp.status_code}')
