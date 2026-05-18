import requests
from bs4 import BeautifulSoup
import re
import json

print("=" * 60)
print("🔍 TESTANDO SITES ACESSÍVEIS")
print("=" * 60)

# Teste 1: AutoList (site de classificados)
print("\n📌 Teste 1: Autolist.com.br")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Tentar buscar Honda Civic
    url = "https://www.autolist.com.br/busca?q=Honda+Civic"
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        print(f"Conteúdo: {len(resp.text)} caracteres")
        # Procurar por preços
        precos = re.findall(r'R\$\s*[\d.]+', resp.text)
        print(f"Preços encontrados: {len(precos)}")
except Exception as e:
    print(f"Erro: {e}")

# Teste 2: Buscar no Google (resultados de carros)
print("\n📌 Teste 2: Busca Google (Honda Civic OLX)")
try:
    url = "https://www.google.com/search?q=Honda+Civic+site:olx.com.br+2020&tbm=shop"
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
except Exception as e:
    print(f"Erro: {e}")

# Teste 3: Usar a API do Brasil API (dados FIPE)
print("\n📌 Teste 3: Brasil API - Tabela FIPE")
try:
    # Buscar código da marca Honda
    url_marcas = "https://parallelum.com.br/fipe/api/v1/carros/marcas"
    resp = requests.get(url_marcas, headers=headers, timeout=10)
    if resp.status_code == 200:
        marcas = resp.json()
        honda = next((m for m in marcas if 'Honda' in m['nome']), None)
        if honda:
            print(f"Honda encontrada: {honda['nome']} (código: {honda['codigo']})")
            
            # Buscar modelos
            url_modelos = f"https://parallelum.com.br/fipe/api/v1/carros/marcas/{honda['codigo']}/modelos"
            resp2 = requests.get(url_modelos, headers=headers, timeout=10)
            if resp2.status_code == 200:
                modelos = resp2.json()
                civics = [m for m in modelos['modelos'] if 'Civic' in m['nome']]
                print(f"Modelos Civic: {len(civics)} encontrados")
                for c in civics[:3]:
                    print(f"  - {c['nome']}")
except Exception as e:
    print(f"Erro: {e}")

print("\n✅ Testes concluídos!")
