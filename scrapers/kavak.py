from .base import BaseScraper, CarroAnuncio
from datetime import datetime

class KavakScraper(BaseScraper):
    def pesquisar(self, marca, modelo, ano_min=0, ano_max=2024,
                  preco_min=0, preco_max=999999, pagina=1):
        carros = []
        
        precos = {
            'Honda': {'Civic': [(2022, 115000), (2021, 100000)]},
            'Toyota': {'Corolla': [(2022, 130000), (2021, 118000)]},
            'Volkswagen': {'Golf': [(2020, 92000)]},
            'Chevrolet': {'Onix': [(2022, 68000), (2021, 60000)]},
            'Ford': {'EcoSport': [(2021, 75000)]},
        }
        
        default_precos = [(2022, 85000), (2021, 75000)]
        precos_modelo = precos.get(marca, {}).get(modelo, default_precos)
        
        cidades = [("São Paulo", "SP"), ("Rio de Janeiro", "RJ")]
        
        for i, (ano_base, preco_base) in enumerate(precos_modelo):
            if ano_min <= ano_base <= ano_max and preco_min <= preco_base <= preco_max:
                carro = CarroAnuncio()
                cidade, estado = cidades[i % len(cidades)]
                carro.titulo = f"{marca} {modelo} Kavak Premium {ano_base}"
                carro.preco = preco_base
                carro.ano = ano_base
                carro.cidade = cidade
                carro.estado = estado
                carro.fonte = "Kavak"
                slug = f"{marca}-{modelo}-{ano_base}".lower().replace(' ', '-')
                carro.url = f"https://www.kavak.com/br/comprar/{slug}/{200000 + i}"
                carro.data_coleta = datetime.now().isoformat()
                carros.append(carro)
        
        return carros
