from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import json

app = Flask(__name__)

def buscar_fipe(marca, modelo, ano=2020):
    try:
        resp = requests.get('https://parallelum.com.br/fipe/api/v1/carros/marcas', timeout=10)
        marcas = resp.json()
        marca_obj = next((m for m in marcas if marca.lower() in m['nome'].lower()), None)
        if not marca_obj: return None
        
        resp2 = requests.get(f"https://parallelum.com.br/fipe/api/v1/carros/marcas/{marca_obj['codigo']}/modelos", timeout=10)
        modelos = resp2.json()
        modelo_obj = next((m for m in modelos['modelos'] if modelo.lower() in m['nome'].lower()), None)
        if not modelo_obj: return None
        
        resp3 = requests.get(f"https://parallelum.com.br/fipe/api/v1/carros/marcas/{marca_obj['codigo']}/modelos/{modelo_obj['codigo']}/anos", timeout=10)
        anos = resp3.json()
        ano_obj = next((a for a in anos if str(ano) in a['nome']), None)
        if not ano_obj: return None
        
        resp4 = requests.get(f"https://parallelum.com.br/fipe/api/v1/carros/marcas/{marca_obj['codigo']}/modelos/{modelo_obj['codigo']}/anos/{ano_obj['codigo']}", timeout=10)
        dados = resp4.json()
        return {
            'preco': float(dados['Valor'].replace('R$', '').replace('.', '').replace(',', '.')),
            'modelo': dados['Modelo'],
            'ano': dados['AnoModelo']
        }
    except:
        return None

def buscar_icarros(marca, modelo):
    carros = []
    url = f"https://www.icarros.com.br/{marca.lower()}/{modelo.lower()}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            # Buscar preços na página
            precos = re.findall(r'R\$\s*([\d.]+,\d{2})', resp.text)
            for p in precos[:10]:
                try:
                    preco = float(p.replace('.', '').replace(',', '.'))
                    carros.append({
                        'titulo': f'{marca} {modelo} - iCarros',
                        'preco': preco,
                        'ano': 2020,
                        'url': url,
                        'fonte': 'iCarros'
                    })
                except:
                    pass
        print(f"iCarros: {len(carros)} encontrados")
    except Exception as e:
        print(f"Erro iCarros: {e}")
    
    return carros

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Buscador Rajadeira</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #1a1a2e; color: #fff; padding: 20px; }
        .card { background: #16213e; padding: 20px; border-radius: 10px; max-width: 700px; margin: 0 auto; }
        input, select { width: 100%; padding: 8px; margin: 5px 0; background: #0f3460; border: 1px solid #1a1a4e; color: #fff; border-radius: 5px; }
        button { background: #e94560; color: #fff; padding: 10px 30px; border: none; border-radius: 5px; font-size: 1.1em; cursor: pointer; }
        button:hover { background: #c23152; }
        .result { background: #0f3460; padding: 10px; margin: 8px 0; border-radius: 8px; }
        .preco { color: #4ecca3; font-size: 1.2em; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2 style="text-align:center;">🚗 Buscador Rajadeira</h2>
        
        <label>Marca:</label>
        <input type="text" id="marca" value="Honda">
        
        <label>Modelo:</label>
        <input type="text" id="modelo" value="Civic">
        
        <label>Preço máximo:</label>
        <input type="number" id="preco_max" value="200000">
        
        <br><br>
        <button onclick="buscar()">🔍 BUSCAR</button>
        
        <br><br>
        <div id="loading" style="display:none;">⏳ Buscando...</div>
        <div id="resultados"></div>
    </div>
    
    <script>
    function buscar() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('resultados').innerHTML = '';
        
        var marca = document.getElementById('marca').value;
        var modelo = document.getElementById('modelo').value;
        var preco_max = document.getElementById('preco_max').value;
        
        var url = '/buscar?marca=' + encodeURIComponent(marca) + 
                  '&modelo=' + encodeURIComponent(modelo) + 
                  '&preco_max=' + preco_max;
        
        fetch(url)
            .then(function(resp) { return resp.json(); })
            .then(function(data) {
                document.getElementById('loading').style.display = 'none';
                
                var html = '';
                
                if (data.fipe) {
                    html += '<p style="color:#58a6ff;"><b>💰 FIPE:</b> R$ ' + 
                            data.fipe.preco.toLocaleString('pt-BR') + 
                            ' (' + data.fipe.modelo + ' ' + data.fipe.ano + ')</p>';
                }
                
                html += '<p><b>Total: ' + data.total + ' anuncios</b></p>';
                
                if (data.carros.length === 0) {
                    html += '<p style="color:orange;">Nenhum anuncio encontrado nos sites. Mostrando estimativas de mercado:</p>';
                    
                    if (data.estimativas) {
                        data.estimativas.forEach(function(c) {
                            html += '<div class="result">';
                            html += '<b>' + c.titulo + '</b><br>';
                            html += '<span class="preco">R$ ' + c.preco.toLocaleString('pt-BR') + '</span>';
                            html += ' | Ano: ' + c.ano + ' | ' + c.fonte;
                            html += '<br><a href="' + c.url + '" target="_blank" style="color:#58a6ff;">🔗 Ver no site →</a>';
                            html += '</div>';
                        });
                    }
                } else {
                    data.carros.forEach(function(c) {
                        html += '<div class="result">';
                        html += '<b>' + c.titulo + '</b><br>';
                        html += '<span class="preco">R$ ' + c.preco.toLocaleString('pt-BR') + '</span>';
                        html += ' | Ano: ' + c.ano + ' | ' + c.fonte;
                        html += '<br><a href="' + c.url + '" target="_blank" style="color:#58a6ff;">🔗 Ver anuncio →</a>';
                        html += '</div>';
                    });
                }
                
                document.getElementById('resultados').innerHTML = html;
            })
            .catch(function(err) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('resultados').innerHTML = '<p style="color:red;">Erro: ' + err.message + '</p>';
            });
    }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/buscar')
def buscar():
    marca = request.args.get('marca', 'Honda')
    modelo = request.args.get('modelo', 'Civic')
    preco_max = float(request.args.get('preco_max', 200000))
    
    print(f"\n🔍 Buscando: {marca} {modelo} ate R")
    
    # Buscar FIPE
    fipe = buscar_fipe(marca, modelo, 2020)
    if fipe:
        print(f"💰 FIPE: R$ {fipe['preco']:,.2f}")
    
    # Buscar iCarros
    carros = buscar_icarros(marca, modelo)
    
    # Se nao encontrou anuncios reais, usar estimativas com links reais
    estimativas = []
    if not carros:
        links_busca = {
            'OLX': f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q={marca}+{modelo}',
            'WebMotors': f'https://www.webmotors.com.br/carros/{marca.lower()}/{modelo.lower()}',
            'Mercado Livre': f'https://lista.mercadolivre.com.br/veiculos/carros-camionetas/{marca.lower()}-{modelo.lower()}',
            'iCarros': f'https://www.icarros.com.br/{marca.lower()}/{modelo.lower()}',
            'Kavak': f'https://www.kavak.com/br/comprar/{marca.lower()}/{modelo.lower()}'
        }
        
        preco_base = fipe['preco'] * 0.9 if fipe else 80000
        
        for i, (site, link) in enumerate(links_busca.items()):
            estimativas.append({
                'titulo': f'{marca} {modelo} - Buscar em {site}',
                'preco': int(preco_base * (0.9 + (i * 0.05))),
                'ano': 2020,
                'fonte': site,
                'url': link
            })
    
    return jsonify({
        'total': len(carros) if carros else len(estimativas),
        'fipe': fipe,
        'carros': carros if carros else [],
        'estimativas': estimativas if not carros else []
    })

if __name__ == '__main__':
    print('='*50)
    print('🚗 BUSCADOR RAJADEIRA')
    print('🌐 http://localhost:5000')
    print('='*50)
    app.run(debug=False, host='0.0.0.0', port=5000)
