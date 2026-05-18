import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

print("=" * 60)
print("🔍 TESTE iCARROS - EXTRAINDO DADOS REAIS")
print("=" * 60)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'pt-BR,pt;q=0.9'
}

marca = "Honda"
modelo = "Civic"
url = f"https://www.icarros.com.br/{marca.lower()}/{modelo.lower()}"

print(f"🔍 URL: {url}")

try:
    resp = requests.get(url, headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Encontrar TODOS os elementos com preços
        precos_rx = re.findall(r'R\$\s*([\d.]+,\d{2})', resp.text)
        print(f"\n💰 Preços encontrados: {len(precos_rx)}")
        for i, p in enumerate(precos_rx[:10]):
            print(f"   {i+1}. R$ {p}")
        
        # Encontrar links
        links = soup.find_all('a', href=True)
        links_carros = []
        for link in links:
            href = link.get('href', '')
            if '/detalhe/' in href or '/comprar/' in href:
                texto = link.get_text(strip=True)
                if texto and len(texto) > 5:
                    links_carros.append({'url': href, 'texto': texto})
        
        print(f"\n🔗 Links de carros: {len(links_carros)}")
        for i, l in enumerate(links_carros[:10]):
            print(f"   {i+1}. {l['texto'][:80]}")
            print(f"      {l['url'][:100]}")
        
        # Buscar títulos de anúncios
        titulos = soup.find_all(['h2', 'h3'])
        print(f"\n📋 Títulos encontrados: {len(titulos)}")
        for i, t in enumerate(titulos[:10]):
            texto = t.get_text(strip=True)
            if len(texto) > 10:
                print(f"   {i+1}. {texto[:100]}")
        
        # Tentar encontrar dados estruturados (JSON-LD)
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'Car':
                            print(f"\n🚗 Dados estruturados encontrados!")
                            print(json.dumps(item, indent=2, ensure_ascii=False)[:500])
            except:
                pass
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Teste concluído!")
