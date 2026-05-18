import requests
from bs4 import BeautifulSoup
import re

print("🔍 Testando sites alternativos...")

# Site 1: WebMotors (tentativa com API)
try:
    url = "https://www.webmotors.com.br/api/search/vehicles?query=Honda+Civic&page=1&pageSize=10"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.webmotors.com.br/'
    }
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"WebMotors API: Status {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Dados recebidos: {len(str(data))} caracteres")
except Exception as e:
    print(f"WebMotors: {e}")

# Site 2: iCarros
try:
    url = "https://www.icarros.com.br/honda/civic"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"\niCarros: Status {resp.status_code}")
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        titulos = soup.find_all(['h2', 'h3'])
        precos = soup.find_all(text=re.compile(r'R\$'))
        print(f"  Títulos: {len(titulos)}, Preços: {len(precos)}")
except Exception as e:
    print(f"iCarros: {e}")

print("\n✅ Teste concluído!")
