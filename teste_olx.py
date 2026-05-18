import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup

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

class OLXScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'pt-BR,pt;q=0.9',
        }
    
    def pesquisar(self, marca, modelo, ano_min=0, ano_max=2024, preco_min=0, preco_max=999999, estado="", pagina=1):
        carros = []
        
        termo = f"{marca} {modelo}".replace(' ', '%20')
        url = f"https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q={termo}&o={pagina}"
        
        if preco_max < 999999:
            url += f"&ps={preco_max}"
        if preco_min > 0:
            url += f"&pe={preco_min}"
        if estado:
            url += f"&sf=1&state={estado}"
        
        print(f"🔍 URL: {url}")
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=15)
            print(f"Status HTTP: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Método 1: Encontrar todas as tags 'a' com links de anúncios
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href', '')
                    
                    # Verificar se o link parece ser um anúncio OLX
                    # Padrão: contém números no final ou '/anuncio/'
                    if re.search(r'/(anuncio|ad|item)/', href) or re.search(r'-\d{9,}', href):
                        
                        # Construir URL completa
                        if href.startswith('http'):
                            url_completa = href
                        elif href.startswith('/'):
                            url_completa = f"https://www.olx.com.br{href}"
                        else:
                            continue
                        
                        # Encontrar o container do anúncio
                        container = link.find_parent(['li', 'div', 'article'])
                        if not container:
                            container = link
                        
                        texto_completo = container.get_text(separator=' ', strip=True)
                        
                        # Extrair título
                        titulo = ""
                        h2 = container.find('h2')
                        if h2:
                            titulo = h2.get_text(strip=True)
                        else:
                            # Pegar primeira linha significativa
                            linhas = texto_completo.split('.')
                            for linha in linhas:
                                if len(linha) > 20 and 'R$' not in linha:
                                    titulo = linha.strip()[:200]
                                    break
                        
                        # Extrair preço
                        preco = 0.0
                        preco_match = re.search(r'R\$\s*([\d.]+)', texto_completo)
                        if preco_match:
                            try:
                                preco = float(preco_match.group(1).replace('.', ''))
                            except:
                                pass
                        
                        # Só adicionar se tiver título e preço
                        if titulo and preco > 1000:
                            carro = CarroAnuncio()
                            carro.titulo = titulo[:200]
                            carro.preco = preco
                            carro.url = url_completa
                            carro.fonte = "OLX"
                            carro.data_coleta = datetime.now().isoformat()
                            
                            # Extrair ano
                            ano_match = re.search(r'\b(20[0-2][0-9])\b', texto_completo)
                            if ano_match:
                                carro.ano = int(ano_match.group(1))
                            
                            # Extrair KM
                            km_match = re.search(r'(\d{1,3}(?:\.\d{3})*)\s*km', texto_completo, re.IGNORECASE)
                            if km_match:
                                carro.quilometragem = int(km_match.group(1).replace('.', ''))
                            
                            # Extrair localização
                            loc_match = re.search(r'(Fortaleza|São Paulo|Rio de Janeiro|Belo Horizonte|Curitiba|Porto Alegre|Salvador|Brasília|Recife|Manaus|Goiânia|Florianópolis|Vitória|Natal|João Pessoa|Maceió|Teresina|São Luís|Belém|Campo Grande|Cuiabá|Aracaju|Porto Velho|Boa Vista|Macapá|Rio Branco|Palmas)', texto_completo, re.IGNORECASE)
                            if loc_match:
                                carro.cidade = loc_match.group(1)
                            
                            # Verificar se já existe
                            if not any(c.url == carro.url for c in carros):
                                carros.append(carro)
                
                print(f"✅ Encontrados: {len(carros)} anúncios reais")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
        
        return carros


if __name__ == '__main__':
    print("=" * 60)
    print("🔍 TESTE - BUSCADOR OLX (ANÚNCIOS REAIS)")
    print("=" * 60)
    
    scraper = OLXScraper()
    resultados = scraper.pesquisar("Honda", "Civic", ano_min=2015, preco_max=100000, estado="CE", pagina=1)
    
    print(f"\n📊 TOTAL: {len(resultados)} anúncios encontrados")
    print("-" * 60)
    
    for i, c in enumerate(resultados[:10]):
        print(f"\n#{i+1} {c.titulo[:100]}")
        print(f"   💰 R$ {c.preco:,.2f} | 📅 {c.ano} | 🏁 {c.quilometragem} km")
        print(f"   📍 {c.cidade}/{c.estado}")
        print(f"   🔗 {c.url[:120]}")
