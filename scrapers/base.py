from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from typing import List, Optional

class CarroAnuncio:
    def __init__(self):
        self.titulo = ""
        self.preco = 0.0
        self.ano = 0
        self.quilometragem = 0
        self.cambio = ""
        self.cidade = ""
        self.estado = ""
        self.url = ""
        self.fonte = ""
        self.data_coleta = ""

class BaseScraper(ABC):
    def __init__(self, delay=2.0):
        self.session = requests.Session()
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    @abstractmethod
    def pesquisar(self, marca, modelo, ano_min=0, ano_max=2024,
                  preco_min=0, preco_max=999999, pagina=1) -> List[CarroAnuncio]:
        pass
    
    def _fazer_request(self, url):
        try:
            time.sleep(self.delay)
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")
            return None
