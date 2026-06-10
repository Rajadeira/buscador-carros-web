# -*- coding: utf-8 -*-
from flask import Flask, render_template_string, request
import cloudscraper
from bs4 import BeautifulSoup
import re
import urllib.parse
import json

app = Flask(__name__)
scraper = cloudscraper.create_scraper()

MARCAS_CLASSICAS = {
    "Chevrolet": ["Opala","Chevette","Monza","Kadett","Vectra","Omega","Astra","Corsa","S10","Blazer"],
    "Ford": ["Corcel","Maverick","Galaxie","Landau","Escort","Fiesta","Ka","F-1000","Ranger"],
    "Volkswagen": ["Fusca","Kombi","Brasilia","Gol","Passat","Santana","Quantum","Voyage","Parati","Saveiro"],
    "Fiat": ["Uno","147","Spazio","Premio","Elba","Tempra","Tipo","Marea","Palio","Siena"],
    "Alfa Romeo": ["145","146","155","156","164","GTV","Spider"],
    "Audi": ["80","90","100","200","A3","A4","A6","A8"],
    "BMW": ["318i","320i","323i","328i","M3","520i","528i","540i"],
    "Honda": ["Civic","Accord","Prelude","CR-V","City"],
    "Toyota": ["Corolla","Camry","Celica","Hilux","SW4","Bandeirante"],
    "Mercedes": ["190","C180","C220","C280","E230","E280","E320"],
}

ESTADOS = [("","Todos"),("SP","SP"),("RJ","RJ"),("MG","MG"),("RS","RS"),("PR","PR"),("SC","SC"),("BA","BA")]
ANOS = list(range(1940,2001))
PRECOS = [5000,10000,15000,20000,25000,30000,40000,50000,60000,70000,80000,90000,100000,120000,150000,200000,999999]

def extrair_dados_json(html):
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.find('script', id='__NEXT_DATA__', type='application/json')
    if not script: return []
    try:
        data = json.loads(script.string)
        return data.get('props', {}).get('pageProps', {}).get('ads', [])
    except: return []

def buscar_olx(marca, modelo, preco_max=999999, ano_min=1940, ano_max=2000, uf=''):
    carros = []
    
    if marca and not modelo:
        modelos = MARCAS_CLASSICAS.get(marca, [])
        if modelos:
            for mod in modelos:
                query = f"{marca} {mod}"
                url = f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q={urllib.parse.quote(query)}'
                if uf: url += f'&sf=1&state={uf}'
                print(f'Busca: {marca} {mod}')
                try:
                    resp = scraper.get(url, timeout=30)
                    if resp.status_code == 200:
                        for ad in extrair_dados_json(resp.text):
                            titulo = ad.get('title') or ad.get('subject', '')
                            if not titulo or len(titulo) < 5: continue
                            preco_str = ad.get('priceValue', '0')
                            preco_clean = preco_str.replace('R$','').replace('.','').replace(',','.').strip()
                            try: preco = float(preco_clean)
                            except: continue
                            if preco > preco_max: continue
                            ano = 0
                            for p in ad.get('properties', []):
                                if p.get('name') == 'regdate':
                                    try: ano = int(re.search(r'\d{4}', str(p.get('value','0'))).group())
                                    except: pass
                            if ano > 2000: continue
                            if 0 < ano < ano_min or (ano_max < 2000 and ano > ano_max): continue
                            km = 0
                            for p in ad.get('properties', []):
                                if p.get('name') == 'mileage': km = int(re.sub(r'\D','',p.get('value','0')))
                            loc = ad.get('locationDetails', {})
                            images = ad.get('images', [])
                            foto = images[0].get('original','') if images else ''
                            carros.append({
                                'titulo': titulo[:150], 'preco': preco, 'ano': ano, 'km': km,
                                'cidade': loc.get('municipality',''), 'estado': loc.get('uf',''),
                                'url': ad.get('url') or ad.get('friendlyUrl',''), 'foto': foto
                            })
                except Exception as e:
                    print(f'Erro: {e}')
            
            urls = set()
            unicos = []
            for c in carros:
                if c['url'] not in urls:
                    urls.add(c['url'])
                    unicos.append(c)
            unicos.sort(key=lambda x: x['preco'])
            return unicos
    
    query = f'{marca} {modelo}' if modelo else marca
    url = f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q={urllib.parse.quote(query)}'
    if uf: url += f'&sf=1&state={uf}'
    print(f'Busca: {url}')
    try:
        resp = scraper.get(url, timeout=40)
        if resp.status_code == 200:
            for ad in extrair_dados_json(resp.text):
                titulo = ad.get('title') or ad.get('subject', '')
                if not titulo or len(titulo) < 5: continue
                preco_str = ad.get('priceValue', '0')
                preco_clean = preco_str.replace('R$','').replace('.','').replace(',','.').strip()
                try: preco = float(preco_clean)
                except: continue
                if preco > preco_max: continue
                ano = 0
                for p in ad.get('properties', []):
                    if p.get('name') == 'regdate':
                        try: ano = int(re.search(r'\d{4}', str(p.get('value','0'))).group())
                        except: pass
                if ano > 2000: continue
                if 0 < ano < ano_min or (ano_max < 2000 and ano > ano_max): continue
                km = 0
                for p in ad.get('properties', []):
                    if p.get('name') == 'mileage': km = int(re.sub(r'\D','',p.get('value','0')))
                loc = ad.get('locationDetails', {})
                images = ad.get('images', [])
                foto = images[0].get('original','') if images else ''
                carros.append({
                    'titulo': titulo[:150], 'preco': preco, 'ano': ano, 'km': km,
                    'cidade': loc.get('municipality',''), 'estado': loc.get('uf',''),
                    'url': ad.get('url') or ad.get('friendlyUrl',''), 'foto': foto
                })
            carros.sort(key=lambda x: x['preco'])
    except Exception as e:
        print(f'Erro: {e}')
    return carros

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Rajadeira Classicos</title>
    <style>
        body { font-family: Arial; max-width: 900px; margin: 20px auto; padding: 15px; background: #f0f2f5; }
        .header { background: #e94560; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
        .card { background: white; border-radius: 0 0 10px 10px; padding: 20px; }
        select { padding: 10px; border: 1px solid #ddd; border-radius: 5px; width: 100%; margin: 5px 0; }
        button { background: #e94560; color: white; padding: 12px; border: none; border-radius: 5px; width: 100%; font-size: 16px; cursor: pointer; margin-top: 10px; }
        .result { border: 1px solid #ddd; padding: 12px; margin: 10px 0; border-radius: 8px; display: flex; gap: 15px; align-items: center; }
        .result-img { width: 120px; height: 90px; object-fit: cover; border-radius: 6px; background: #eee; }
        .preco { color: green; font-size: 1.3em; font-weight: bold; }
        .detalhes { color: #888; font-size: 0.9em; }
        a { color: #1565c0; text-decoration: none; }
        .classic-badge { background: #8B4513; color: gold; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
        .spinner { border: 4px solid #eee; border-top: 4px solid #e94560; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="header"><h1>Rajadeira Classicos</h1><p>1940 a 2000</p></div>
    <div class="card">
        <form method="GET" action="/buscar" onsubmit="document.getElementById('loading').style.display='block'">
            <div style="display:flex; gap:10px;">
                <div style="flex:1;">
                    <label>Marca</label>
                    <select name="marca" id="marca" onchange="atualizarModelos()">
                        <option value="">Todas</option>
                        {% for m in marcas %}<option value="{{ m }}">{{ m }}</option>{% endfor %}
                    </select>
                </div>
                <div style="flex:1;">
                    <label>Modelo</label>
                    <select name="modelo" id="modelo"><option value="">Todos</option></select>
                </div>
            </div>
            <div style="display:flex; gap:10px;">
                <div style="flex:1;"><label>Preco max</label><select name="preco_max"><option value="999999">Sem limite</option>{% for p in precos %}<option value="{{ p }}">R$ {{ "{:,.0f}".format(p) }}</option>{% endfor %}</select></div>
                <div style="flex:1;"><label>Estado</label><select name="uf">{% for s,n in estados %}<option value="{{ s }}">{{ n }}</option>{% endfor %}</select></div>
            </div>
            <div style="display:flex; gap:10px;">
                <div style="flex:1;"><label>Ano inicial</label><select name="ano_min">{% for a in anos %}<option value="{{ a }}" {% if a==1940 %}selected{% endif %}>{{ a }}</option>{% endfor %}</select></div>
                <div style="flex:1;"><label>Ano final</label><select name="ano_max">{% for a in anos %}<option value="{{ a }}" {% if a==2000 %}selected{% endif %}>{{ a }}</option>{% endfor %}</select></div>
            </div>
            <button type="submit">BUSCAR CLASSICOS</button>
        </form>
        <div id="loading" style="display:none;"><div class="spinner"></div><p>Pesquisando...</p></div>
        {% if carros %}
        <p><b>{{ carros|length }} classicos encontrados</b></p>
        {% for c in carros %}
        <div class="result">
            {% if c.foto %}<img src="{{ c.foto }}" class="result-img" loading="lazy" referrerpolicy="no-referrer" crossorigin="anonymous">{% else %}<div class="result-img" style="display:flex; align-items:center; justify-content:center; font-size:2em;">🚗</div>{% endif %}
            <div style="flex:1;">
                <a href="{{ c.url }}" target="_blank"><b>{{ c.titulo[:120] }}</b></a><span class="classic-badge">CLASSICO</span>
                <br><span class="detalhes">Ano: {{ c.ano if c.ano else 'N/D' }} | {{ c.km if c.km else 'N/D' }} km{% if c.cidade %} | {{ c.cidade }}/{{ c.estado }}{% endif %}</span>
            </div>
            <div><span class="preco">R$ {{ "{:,.2f}".format(c.preco) }}</span></div>
        </div>
        {% endfor %}
        {% endif %}
    </div>
    <script>
        const MODELOS = {{ modelos_json | safe }};
        function atualizarModelos(){const m=document.getElementById('marca').value;const s=document.getElementById('modelo');s.innerHTML='<option value="">Todos</option>';if(m&&MODELOS[m]){MODELOS[m].forEach(function(x){const o=document.createElement('option');o.value=x;o.textContent=x;s.appendChild(o)})}}
        window.addEventListener('load',atualizarModelos);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, marcas=sorted(MARCAS_CLASSICAS.keys()), carros=[], precos=PRECOS, estados=ESTADOS, anos=ANOS, modelos_json=json.dumps(MARCAS_CLASSICAS))

@app.route('/buscar')
def buscar():
    marca = request.args.get('marca', '')
    modelo = request.args.get('modelo', '')
    preco_max = float(request.args.get('preco_max', 999999) or 999999)
    ano_min = int(request.args.get('ano_min', 1940) or 1940)
    ano_max = int(request.args.get('ano_max', 2000) or 2000)
    uf = request.args.get('uf', '').upper()
    
    carros = buscar_olx(marca, modelo, preco_max, ano_min, ano_max, uf)
    carros = carros[:500]
    
    return render_template_string(HTML, marcas=sorted(MARCAS_CLASSICAS.keys()), carros=carros, precos=PRECOS, estados=ESTADOS, anos=ANOS, modelos_json=json.dumps(MARCAS_CLASSICAS))

if __name__ == '__main__':
    print('='*50)
    print('RAJADEIRA CLASSICOS')
    print('http://localhost:5000')
    print('='*50)
    app.run(debug=False, host='0.0.0.0', port=5000)
