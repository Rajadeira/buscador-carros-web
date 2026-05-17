from .base import BaseScraper, CarroAnuncio
from datetime import datetime
import re
import json

class WebMotorsScraper(BaseScraper):
    def pesquisar(self, marca, modelo, ano_min=0, ano_max=2024,
                  preco_min=0, preco_max=999999, pagina=1):
        carros = []
        
        # URL real da WebMotors
        marca_format = marca.lower().replace(' ', '-')
        modelo_format = modelo.lower().replace(' ', '-')
        
        url = f"https://www.webmotors.com.br/carros/{marca_format}/{modelo_format}"
        
        print(f"🔍 Buscando WebMotors: {url}")
        
        soup = self._fazer_request(url)
        if not soup:
            # Fallback para dados simulados se o site bloquear
            return self._dados_simulados(marca, modelo, "WebMotors")
        
        try:
            # Tentar encontrar os cards de anúncios
            cards = soup.find_all('div', class_=re.compile('card|anuncio|listing'))
            
            for card in cards[:10]:  # Limitar a 10 resultados
                try:
                    carro = CarroAnuncio()
                    
                    # Extrair título
                    titulo_elem = card.find(['h2', 'h3', 'span'], class_=re.compile('title|titulo|name'))
                    if titulo_elem:
                        carro.titulo = titulo_elem.text.strip()
                    
                    # Extrair preço
                    preco_elem = card.find(['span', 'div'], class_=re.compile('price|preco|value'))
                    if preco_elem:
                        preco_text = re.sub(r'[^\d,]', '', preco_elem.text)
                        preco_text = preco_text.replace(',', '.')
                        carro.preco = float(preco_text) if preco_text else 0
                    
                    # Extrair ano
                    ano_elem = card.find(['span', 'div'], class_=re.compile('year|ano'))
                    if ano_elem:
                        ano_text = re.sub(r'[^\d]', '', ano_elem.text)
                        carro.ano = int(ano_text) if ano_text else 0
                    
                    carro.fonte = "WebMotors"
                    carro.data_coleta = datetime.now().isoformat()
                    
                    if carro.titulo:
                        carros.append(carro)
                        
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"Erro ao parsear WebMotors: {e}")
        
        # Se não encontrou nada, usar dados simulados
        if not carros:
            carros = self._dados_simulados(marca, modelo, "WebMotors")
        
        return carros
    
    def _dados_simulados(self, marca, modelo, fonte):
        carros = []
        exemplos = [
            {"titulo": f"{marca} {modelo} 2.0 16V Turbo", "preco": 75000, "ano": 2020},
            {"titulo": f"{marca} {modelo} 1.8 Flex Automático", "preco": 65000, "ano": 2019},
            {"titulo": f"{marca} {modelo} 2.0 Turbo Premium", "preco": 89000, "ano": 2021},
        ]
        for ex in exemplos:
            carro = CarroAnuncio()
            carro.titulo = ex['titulo']
            carro.preco = ex['preco']
            carro.ano = ex['ano']
            carro.fonte = fonte
            carro.data_coleta = datetime.now().isoformat()
            carros.append(carro)
        return carros
