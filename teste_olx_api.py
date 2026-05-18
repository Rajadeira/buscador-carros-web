import requests
import json
import re

print("=" * 60)
print("🔍 TESTE - API DA OLX (DADOS REAIS)")
print("=" * 60)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

# Tentar a API de busca da OLX
urls = [
    "https://www.olx.com.br/api/v1/ads?q=Honda%20Civic&limite=10&pe=100000",
    "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Honda+Civic&o=1&sf=1",
]

for url in urls:
    print(f"\n📌 URL: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            content_type = resp.headers.get('Content-Type', '')
            print(f"Content-Type: {content_type}")
            print(f"Tamanho: {len(resp.text)} caracteres")
            
            # Ver se é JSON
            if 'json' in content_type:
                try:
                    data = resp.json()
                    print(f"Dados JSON: {json.dumps(data, indent=2)[:500]}")
                except:
                    print("Nao e JSON valido")
            
            # Procurar links de anuncios
            links = re.findall(r'href="(/[^"]*-\d{9,}[^"]*)"', resp.text)
            print(f"Links de anuncios encontrados: {len(links)}")
            for link in links[:5]:
                print(f"  - https://www.olx.com.br{link}")
            
    except Exception as e:
        print(f"Erro: {e}")

print("\n✅ Teste concluido!")
