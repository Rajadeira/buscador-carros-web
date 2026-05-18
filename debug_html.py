import cloudscraper
from bs4 import BeautifulSoup
import re

scraper = cloudscraper.create_scraper()
url = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Fusca&o=1'
resp = scraper.get(url, timeout=40)

with open('pagina_fusca.html', 'w', encoding='utf-8') as f:
    f.write(resp.text)
print('✅ HTML salvo em pagina_fusca.html')

soup = BeautifulSoup(resp.text, 'html.parser')
scripts = soup.find_all('script')
print(f'🔍 {len(scripts)} scripts encontrados')
for i, script in enumerate(scripts):
    if script.string and ('window.__' in script.string or 'window.__INITIAL' in script.string):
        print(f'\nScript {i}: contém window.__')
        print(script.string[:500])
        print('...')
