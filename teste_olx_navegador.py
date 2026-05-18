import requests
import re
from bs4 import BeautifulSoup

print("=" * 60)
print("🔍 TESTE OLX - SIMULANDO NAVEGADOR REAL")
print("=" * 60)

session = requests.Session()

# Primeiro, visitar a pagina inicial (pegar cookies)
session.get("https://www.olx.com.br", headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# Depois, buscar Honda Civic
url = "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Honda+Civic&ps=100000"
print(f"\nURL: {url}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.olx.com.br/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
}

resp = session.get(url, headers=headers, timeout=15)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Procurar por __NEXT_DATA__ ou __INITIAL_STATE__
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string:
            # Procurar dados JSON
            if '__NEXT_DATA__' in script.string:
                print("\n✅ Encontrado __NEXT_DATA__!")
                try:
                    import json
                    data = json.loads(script.string.split('__NEXT_DATA__ = ')[1].split(';</script>')[0])
                    print(f"Estrutura: {list(data.keys())}")
                except:
                    print("JSON parcial")
            
            if 'window.__INITIAL_STATE__' in script.string:
                print("\n✅ Encontrado __INITIAL_STATE__!")
    
    # Procurar links de anuncios pelo padrao
    links = re.findall(r'https?://[^"\']*olx\.com\.br/[^"\']*-\d{9,}[^"\']*', resp.text)
    print(f"\n📊 Links de anuncios: {len(links)}")
    for link in links[:10]:
        print(f"  {link[:150]}")
    
    # Procurar titulos
    titulos = re.findall(r'<h2[^>]*>([^<]+)</h2>', resp.text)
    print(f"\n📋 Titulos: {len(titulos)}")
    for t in titulos[:10]:
        if len(t) > 10:
            print(f"  - {t.strip()[:100]}")
    
else:
    print(f"❌ Bloqueado! Status: {resp.status_code}")

print("\n✅ Teste concluido!")
