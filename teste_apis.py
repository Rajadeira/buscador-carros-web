import requests
import json

print("=" * 60)
print("🔍 TESTANDO APIs PÚBLICAS DE CARROS")
print("=" * 60)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Teste 1: Brasil API - Preços FIPE (FUNCIONOU!)
print("\n✅ 1. Brasil API (FIPE) - Já testado e funcionando!")

# Teste 2: Tabela FIPE API direta
print("\n📌 2. FIPE API HTTP - Testando...")
try:
    url = "https://fipeapi.appspot.com/api/1/carros/marcas.json"
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        marcas = resp.json()
        print(f"   Marcas: {len(marcas)} encontradas")
except Exception as e:
    print(f"   Erro: {e}")

# Teste 3: AutoEsporte (portal de notícias de carros)
print("\n📌 3. AutoEsporte - Testando...")
try:
    url = "https://autoesporte.globo.com/api/v1/materias/"
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"   Status: {resp.status_code}")
except Exception as e:
    print(f"   Erro: {e}")

# Teste 4: Kavak (site de compra/venda)
print("\n📌 4. Kavak - Testando...")
try:
    url = "https://www.kavak.com/br/comprar/honda/civic"
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        # Contar quantos carros aparecem
        import re
        precos = re.findall(r'R\$\s*[\d.]+', resp.text)
        print(f"   Preços na página: {len(precos)}")
except Exception as e:
    print(f"   Erro: {e}")

# Teste 5: iCarros
print("\n📌 5. iCarros - Testando...")
try:
    url = "https://www.icarros.com.br/honda/civic"
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        # Contar menções de preço
        import re
        precos = re.findall(r'R\$\s*[\d.]+', resp.text)
        print(f"   Preços na página: {len(precos)}")
except Exception as e:
    print(f"   Erro: {e}")

# Teste 6: AutoList (classificados)
print("\n📌 6. AutoList - Testando...")
try:
    url = "https://www.autolist.com.br/honda/civic"
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        import re
        precos = re.findall(r'R\$\s*[\d.]+', resp.text)
        print(f"   Preços na página: {len(precos)}")
except Exception as e:
    print(f"   Erro: {e}")

print("\n✅ Testes concluídos!")
