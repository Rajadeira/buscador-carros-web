import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

class CarroAnuncio:
    def __init__(self):
        self.titulo = ""
        self.preco = 0.0
        self.ano = 0
        self.quilometragem = 0
        self.cidade = ""
        self.estado = ""
        self.url = ""
        self.fonte = ""
        self.data_coleta = ""

def buscar_olx_pelo_google(marca, modelo, preco_max=100000, estado="CE"):
    """Busca anúncios da OLX usando Google como intermediário"""
    
    carros = []
    
    # Construir busca no Google
    query = f"{marca} {modelo} {2020} site:olx.com.br"
    if estado:
        query += f" {estado}"
    
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=20"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'pt-BR,pt;q=0.9'
    }
    
    print(f"🔍 Buscando no Google: {query}")
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status Google: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Encontrar todos os links de resultados
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                
                # Filtrar links da OLX
                if 'olx.com.br' in href and ('/anuncio/' in href or re.search(r'-\d{9,}', href)):
                    
                    # Limpar URL (remover prefixo do Google)
                    if href.startswith('/url?q='):
                        href = href.split('/url?q=')[1].split('&')[0]
                    
                    carro = CarroAnuncio()
                    carro.url = href
                    carro.fonte = "OLX"
                    carro.data_coleta = datetime.now().isoformat()
                    
                    # Tentar extrair informações do snippet
                    parent = link.find_parent(['div', 'span'])
                    if parent:
                        texto = parent.get_text(separator=' ', strip=True)
                        
                        # Título
                        h3 = parent.find('h3')
                        if h3:
                            carro.titulo = h3.get_text(strip=True)[:200]
                        
                        # Preço
                        preco_match = re.search(r'R\$\s*([\d.]+)', texto)
                        if preco_match:
                            try:
                                carro.preco = float(preco_match.group(1).replace('.', ''))
                            except:
                                pass
                        
                        # Ano
                        ano_match = re.search(r'\b(20[0-2][0-9])\b', texto)
                        if ano_match:
                            carro.ano = int(ano_match.group(1))
                        
                        # KM
                        km_match = re.search(r'(\d{1,3}(?:\.\d{3})*)\s*km', texto, re.IGNORECASE)
                        if km_match:
                            carro.quilometragem = int(km_match.group(1).replace('.', ''))
                    
                    if carro.url and 'olx.com.br' in carro.url:
                        carros.append(carro)
            
            print(f"✅ Google encontrou {len(carros)} links da OLX")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return carros


# Teste
if __name__ == '__main__':
    print("=" * 60)
    print("🔍 BUSCADOR VIA GOOGLE")
    print("=" * 60)
    
    resultados = buscar_olx_pelo_google("Honda", "Civic", preco_max=100000, estado="CE")
    
    print(f"\n📊 Total: {len(resultados)} anúncios")
    for i, c in enumerate(resultados[:5]):
        print(f"\n#{i+1}")
        print(f"   Título: {c.titulo[:100] if c.titulo else 'N/A'}")
        print(f"   Preço: R$ {c.preco:,.2f}" if c.preco > 0 else "   Preço: N/A")
        print(f"   URL: {c.url[:120]}")
