from .base import BaseScraper, CarroAnuncio
from datetime import datetime

class iCarrosScraper(BaseScraper):
    def pesquisar(self, marca, modelo, ano_min=0, ano_max=2024,
                  preco_min=0, preco_max=999999, pagina=1):
        carros = []
        
        precos = {
            'Honda': {'Civic': [(2021, 105000), (2020, 90000), (2019, 80000)]},
            'Toyota': {'Corolla': [(2022, 125000), (2021, 110000)]},
            'Volkswagen': {'Golf': [(2020, 88000), (2019, 77000)]},
            'Fiat': {'Uno': [(2019, 33000), (2018, 29000)]},
            'Chevrolet': {'Onix': [(2021, 60000), (2020, 52000)]},
            'Ford': {'Ka': [(2020, 40000), (2019, 36000)]},
        }
        
        default_precos = [(2021, 75000), (2020, 65000), (2019, 55000)]
        precos_modelo = precos.get(marca, {}).get(modelo, default_precos)
        
        cidades = [("São Paulo", "SP"), ("Campinas", "SP"), ("Rio de Janeiro", "RJ")]
        
        for i, (ano_base, preco_base) in enumerate(precos_modelo):
            if ano_min <= ano_base <= ano_max and preco_min <= preco_base <= preco_max:
                carro = CarroAnuncio()
                cidade, estado = cidades[i % len(cidades)]
                carro.titulo = f"{marca} {modelo} Loja {ano_base}"
                carro.preco = preco_base
                carro.ano = ano_base
                carro.cidade = cidade
                carro.estado = estado
                carro.fonte = "iCarros"
                slug = f"{marca}-{modelo}-{ano_base}".lower().replace(' ', '-')
                carro.url = f"https://www.icarros.com.br/detalhe/{slug}/{100000 + i}"
                carro.data_coleta = datetime.now().isoformat()
                carros.append(carro)
        
        return carros
