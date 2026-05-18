import cloudscraper
from bs4 import BeautifulSoup
import re

scraper = cloudscraper.create_scraper()

# Teste 1: busca por "Volkswagen"
url_vw = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Volkswagen&o=1'
resp = scraper.get(url_vw, timeout=20)
soup = BeautifulSoup(resp.text, 'html.parser')
links_vw = soup.find_all('a', href=re.compile(r'-\d{9,}'))
print(f'🔍 "Volkswagen": {len(links_vw)} links encontrados')

# Teste 2: busca por "Fusca"
url_fusca = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Fusca&o=1'
resp = scraper.get(url_fusca, timeout=20)
soup = BeautifulSoup(resp.text, 'html.parser')
links_fusca = soup.find_all('a', href=re.compile(r'-\d{9,}'))
print(f'🔍 "Fusca": {len(links_fusca)} links encontrados')

# Teste 3: busca por "Gol"
url_gol = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Gol&o=1'
resp = scraper.get(url_gol, timeout=20)
soup = BeautifulSoup(resp.text, 'html.parser')
links_gol = soup.find_all('a', href=re.compile(r'-\d{9,}'))
print(f'🔍 "Gol": {len(links_gol)} links encontrados')
