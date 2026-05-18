import requests
import re
import json
from bs4 import BeautifulSoup

print("=" * 60)
print("🔍 TESTANDO SITES DE CARROS QUE PERMITEM SCRAPING")
print("=" * 60)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

sites = [
    {
        'nome': 'AutoList',
        'url': 'https://www.autolist.com.br/busca?q=Honda+Civic&preco_max=100000'
    },
    {
        'nome': 'AnunciosBR',
        'url': 'https://www.anunciosbr.com.br/carros/honda-civic'
    },
    {
        'nome': 'Classificados Brasil',
        'url': 'https://www.classificadosbrasil.com.br/carros/honda/civic'
    },
    {
        'nome': 'CarroSP',
        'url': 'https://www.carrosp.com.br/busca/honda+civic'
    },
    {
        'nome': 'WebMotors (página simples)',
        'url': 'https://www.webmotors.com.br/carros/honda/civic?page=1'
    }
]

resultados = []

for site in sites:
    print(f"\n📌 {site['nome']}")
    print(f"   URL: {site['url']}")
    
    try:
        resp = requests.get(site['url'], headers=headers, timeout=15, allow_redirects=True)
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 200:
            # Contar elementos relevantes
            precos = re.findall(r'R\$\s*([\d.]+[,\d]*)', resp.text)
            titulos_h2 = re.findall(r'<h2[^>]*>([^<]+)</h2>', resp.text)
            titulos_h3 = re.findall(r'<h3[^>]*>([^<]+)</h3>', resp.text)
            links = re.findall(r'href="([^"]*-(?:carro|veiculo|auto|anuncio)[^"]*)"', resp.text, re.IGNORECASE)
            
            print(f"   ✅ Preços: {len(precos)} | Títulos: {len(titulos_h2 + titulos_h3)} | Links: {len(links)}")
            
            # Mostrar alguns preços
            if precos:
                print(f"   💰 Exemplos: R$ {precos[0]}, R$ {precos[1] if len(precos) > 1 else ''}")
            
            resultados.append({
                'nome': site['nome'],
                'status': resp.status_code,
                'precos': len(precos),
                'links': len(links)
            })
        else:
            print(f"   ❌ Status: {resp.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)[:80]}")

print("\n" + "=" * 60)
print("📊 RESUMO")
print("=" * 60)
for r in resultados:
    print(f"{'✅' if r['status'] == 200 else '❌'} {r['nome']}: Status {r['status']} | {r['precos']} preços | {r['links']} links")

print("\n🔍 OUTRA OPÇÃO: Usar o site da OLX de outro país (Portugal)")
print("=" * 60)
try:
    url = "https://www.olx.pt/carros-motos-e-barcos/carros/?search%5Bfilter_float_price%3Ato%5D=10000&search%5Bdescription%5D=1&q=Honda+Civic"
    resp = requests.get(url, headers=headers, timeout=15)
    print(f"Status OLX Portugal: {resp.status_code}")
    if resp.status_code == 200:
        links = re.findall(r'href="(/anuncio/[^"]*)"', resp.text)
        print(f"Links encontrados: {len(links)}")
except Exception as e:
    print(f"Erro: {e}")

print("\n✅ Testes concluídos!")
