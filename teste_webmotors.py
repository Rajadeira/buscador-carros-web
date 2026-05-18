import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import xml.etree.ElementTree as ET

print("=" * 60)
print("🔍 TESTE WEBMOTORS - VIA SITEMAP")
print("=" * 60)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Primeiro, ver o sitemap principal
url = "https://www.webmotors.com.br/sitemap.xml"

try:
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        # Parsear XML
        root = ET.fromstring(resp.content)
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        urls = root.findall('.//ns:loc', namespaces)
        print(f"URLs no sitemap: {len(urls)}")
        
        # Mostrar algumas URLs
        for i, url_elem in enumerate(urls[:20]):
            print(f"   {url_elem.text}")
        
        # Buscar sitemaps específicos de veículos
        sitemaps_veiculos = [u.text for u in urls if 'veiculo' in u.text.lower() or 'carro' in u.text.lower()]
        print(f"\n🚗 Sitemaps de veículos: {len(sitemaps_veiculos)}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

# Testar página de busca
print("\n" + "=" * 60)
print("🔍 TESTE PÁGINA DE BUSCA WEBMOTORS")
print("=" * 60)

url_busca = "https://www.webmotors.com.br/carros/honda/civic"

try:
    resp = requests.get(url_busca, headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Procurar dados JSON embutidos
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'window.__INITIAL_STATE__' in (script.string or ''):
                print("✅ Encontrado __INITIAL_STATE__")
                # Extrair parte do JSON
                texto = script.string
                inicio = texto.find('{')
                fim = texto.rfind('}') + 1
                if inicio >= 0 and fim > inicio:
                    try:
                        dados = json.loads(texto[inicio:fim])
                        print(f"Dados extraídos com sucesso!")
                    except:
                        print("JSON parcial encontrado")
                break
        
        # Contar elementos
        precos = re.findall(r'R\$\s*[\d.]+', resp.text)
        print(f"Preços na página: {len(precos)}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n✅ Testes concluídos!")
