from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from typing import List, Optional
import json

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
        self.foto = ""

class BaseScraper(ABC):
    def __init__(self, delay=1.0):
        self.session = requests.Session()
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    @abstractmethod
    def pesquisar(self, marca, modelo, ano_min=0, ano_max=2024,
                  preco_min=0, preco_max=999999, pagina=1) -> List[CarroAnuncio]:
        pass
    
    def _fazer_request(self, url, headers=None):
        try:
            time.sleep(self.delay)
            h = headers if headers else self.headers
            response = self.session.get(url, headers=h, timeout=15)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            else:
                print(f"Status {response.status_code} para {url}")
                return None
        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")
            return None
    
    def _fazer_request_json(self, url, headers=None):
        try:
            time.sleep(self.delay)
            h = headers if headers else self.headers
            response = self.session.get(url, headers=h, timeout=15)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Erro ao acessar API {url}: {e}")
            return None
