import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

print("=" * 60)
print("🔍 TESTE: GOOGLE -> OLX")
print("=" * 60)

query = 'Honda Civic 2020 2021 site:olx.com.br'
url = f'https://www.google.com/search?q={urllib.parse.quote(query)}&num=20&hl=pt-BR'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html',
    'Accept-Language': 'pt-BR,pt;q=0.9'
}

print(f"URL: {url}")

try:
    resp = requests.get(url, headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Extrair todos os links
        links_olx = set()
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            if 'olx.com.br' in href:
                # Limpar URL do Google
                if '/url?q=' in href:
                    href = href.split('/url?q=')[1].split('&')[0]
                href = urllib.parse.unquote(href)
                
                # Pegar apenas links de anuncios
                if re.search(r'-\d{9,}', href):
                    links_olx.add(href)
        
        links_olx = list(links_olx)
        print(f"\n🔗 Links de anuncios OLX: {len(links_olx)}")
        
        for i, link in enumerate(links_olx[:10]):
            print(f"\n{i+1}. {link}")
            
            # Tentar extrair titulo do snippet
            parent = a.find_parent(['div', 'h3'])
            if parent:
                texto = parent.get_text(strip=True)[:150]
                print(f"   📋 {texto}")
        
        if len(links_olx) == 0:
            print("\n⚠️ Nenhum link encontrado. Tentando metodo alternativo...")
            # Salvar HTML para debug
            with open('google_resposta.html', 'w', encoding='utf-8') as f:
                f.write(resp.text)
            print("   HTML salvo em google_resposta.html para analise")
            
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Teste concluido!")
