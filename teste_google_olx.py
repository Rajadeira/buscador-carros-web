import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

print("=" * 60)
print("🔍 BUSCANDO ANÚNCIOS REAIS VIA GOOGLE")
print("=" * 60)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'pt-BR,pt;q=0.9'
}

# Buscar Honda Civic no Google
query = 'Honda Civic 2020 site:olx.com.br Ceará'
url = f'https://www.google.com/search?q={urllib.parse.quote(query)}&num=20&hl=pt-BR'

print(f"URL: {url}")

try:
    resp = requests.get(url, headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Método 1: Procurar por elementos h3 (títulos dos resultados)
        titulos = soup.find_all('h3')
        print(f"\n📋 Resultados encontrados: {len(titulos)}")
        
        for i, titulo in enumerate(titulos[:10]):
            texto = titulo.get_text(strip=True)
            # Encontrar o link pai
            link_elem = titulo.find_parent('a')
            href = link_elem.get('href', '') if link_elem else ''
            
            # Limpar URL do Google
            if '/url?q=' in href:
                href = href.split('/url?q=')[1].split('&')[0]
            
            print(f"\n{i+1}. {texto[:100]}")
            if href:
                print(f"   🔗 {urllib.parse.unquote(href)[:120]}")
        
        # Método 2: Procurar por todos os links
        todos_links = soup.find_all('a', href=True)
        links_olx = []
        for link in todos_links:
            href = link.get('href', '')
            if 'olx.com.br' in href and not 'google.com' in href:
                if '/url?q=' in href:
                    href = href.split('/url?q=')[1].split('&')[0]
                links_olx.append(urllib.parse.unquote(href))
        
        links_olx = list(set(links_olx))  # Remover duplicatas
        print(f"\n🔗 Links da OLX encontrados: {len(links_olx)}")
        for i, link in enumerate(links_olx[:10]):
            print(f"{i+1}. {link[:150]}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n✅ Teste concluído!")
