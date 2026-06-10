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
    "Chevrolet": ["Bel Air","Impala","Opala","Chevette","Monza","Kadett","Vectra","Omega","Astra","Corsa","Ipanema","Suprema","Camaro","Corvette","Marajo","Chevy 500","A10","A20","C10","C20","D10","D20","Bonanza","Veraneio","S10","Blazer","Silverado"],
    "Ford": ["Galaxie","Landau","Maverick","Corcel","Corcel II","Del Rey","Belina","Belina II","Escort","Versailles","Fiesta","Ka","Mondeo","Mustang","Galaxy","Explorer","Pampa","F-75","F-100","F-1000","F-250","Ranger","F-350","F-4000"],
    "Volkswagen": ["Fusca","Karmann Ghia","Brasilia","Variant","Variant II","Passat","Gol","Voyage","Parati","Fox","Santana","Quantum","Apollo","Logus","Pointer","Golf","Polo","Jetta","Corrado","Kombi","Saveiro"],
    "Fiat": ["147","Spazio","Panorama","Premio","Elba","Uno","Tempra","Tipo","Marea","Brava","Bravo","Palio","Siena","Palio Weekend","Punto","Fiat Coupe","Fiorino","Ducato"],
    "Mercedes-Benz": ["190","C180","C220","C280","E230","E280","E320","S320","S420","S500","SLK 230","CLK 230","CLK 320","ML 320","A160","A190","Sprinter"],
    "Toyota": ["Corona","Corolla","Camry","Celica","MR2","RAV4","Bandeirante","Land Cruiser","Hilux","SW4","Prado"],
    "Honda": ["Civic","Accord","Prelude","CR-V","City","Legend","NSX"],
    "Nissan": ["Sentra","Pathfinder","Frontier","Pickup D21","Maxima","200SX","Bluebird"],
    "Mitsubishi": ["Lancer","Galant","Eclipse","Pajero Full","Pajero Sport","Pajero TR4","L200","Space Wagon","3000GT"],
    "Subaru": ["Legacy","Impreza","Forester","Outback"],
    "Mazda": ["323","626","MX-5 Miata","RX-7"],
    "Renault": ["R-4","R-8","R-10","R-12","R-18","R-19","Clio","Megane","Laguna","Scenic","Trafic","Master"],
    "Peugeot": ["404","504","106","205","206","306","405","406","605","Partner"],
    "Citroen": ["AX","BX","ZX","Saxo","Xsara","Xantia","Berlingo","Jumper"],
    "BMW": ["318i","320i","323i","328i","M3","520i","528i","540i","730i","740i","750iL","Z3"],
    "Hyundai": ["Accent","Elantra","Sonata","Galloper","Tucson"],
    "Kia": ["Sephia","Sportage","Carnival"],
    "Daewoo": ["Lanos","Nubira","Leganza","Espero","Tico"],
    "Volvo": ["240","440","460","850","S40","S70","S80","V40","V70","C70","XC70"],
    "Saab": ["900","9000","9-3","9-5"],
    "Land Rover": ["Defender","Discovery","Freelander","Range Rover"],
    "Jaguar": ["XJ6","XJ8","XJR","XK8","XJS"],
    "Audi": ["80","90","100","200","A3","A4","A6","A8","S4","S6","Cabriolet","Coupe"],
    "Porsche": ["911 Carrera","911 Turbo","Boxster","928","944","968"],
    "Alfa Romeo": ["145","146","155","156","164","GTV","Spider"],
    "Gurgel": ["X-12","X-15","Tocantins","Carajas","BR-800","E-400"],
    "Puma": ["GTB","GTC","GTS","AMV"],
    "Chrysler": ["Dart","Charger","Polara","Magnum","LeBaron","Caravan"],
    "Dodge": ["Dart","Charger","Polara","Magnum","Dakota","Ram"],
    "Plymouth": ["Valiant","Belvedere","Fury","Satellite","Barracuda","Duster"],
    "Willys": ["Jeep","Pickup","Rural","Interlagos","Itamaraty"],
}

ESTADOS = [("","Todos"),("SP","SP"),("RJ","RJ"),("MG","MG"),("RS","RS"),("PR","PR"),("SC","SC"),("BA","BA"),("PE","PE"),("CE","CE"),("DF","DF"),("GO","GO")]
ANOS = list(range(1940,2001))
KMS = [5000,10000,15000,20000,25000,30000,35000,40000,45000,50000,60000,70000,80000,90000,100000]
PRECOS = [5000,10000,15000,20000,25000,30000,40000,50000,60000,70000,80000,90000,100000,120000,150000,200000,999999]
CORES = ["Branco","Preto","Prata","Cinza","Vermelho","Azul","Verde","Amarelo","Marrom","Bege"]
TIPOS = ["Sedã","Hatch","SUV","Pickup","Coupé","Conversível","Perua","Van","Utilitário"]
PORTA_OPCOES = [2,4]

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
                try:
                    resp = scraper.get(url, timeout=30)
                    if resp.status_code == 200:
                        for ad in extrair_dados_json(resp.text):
                            titulo = ad.get('title') or ad.get('subject', '')
                            if not titulo or len(titulo) < 5: continue
                            if marca and marca.lower() not in titulo.lower(): continue
                            preco_str = ad.get('priceValue', '0')
                            preco_clean = preco_str.replace('R$','').replace('.','').replace(',','.').strip()
                            try: preco = float(preco_clean)
                            except: continue
                            if preco > preco_max: continue
                            ano = 0; km = 0; cambio = ''; combustivel = ''; cor = ''; portas = 0; tipo = ''
                            for p in ad.get('properties', []):
                                if p.get('name') == 'regdate':
                                    try: ano = int(re.search(r'\d{4}', str(p.get('value','0'))).group())
                                    except: pass
                                if p.get('name') == 'mileage': km = int(re.sub(r'\D','',p.get('value','0')))
                                if p.get('name') == 'gearbox': cambio = p.get('value','')
                                if p.get('name') == 'fuel': combustivel = p.get('value','')
                                if p.get('name') == 'carcolor': cor = p.get('value','')
                                if p.get('name') == 'doors': 
                                    try: portas = int(re.sub(r'\D','',p.get('value','0')))
                                    except: pass
                                if p.get('name') == 'cartype': tipo = p.get('value','')
                            if ano > 2000: continue
                            if 0 < ano < ano_min or (ano_max < 2000 and ano > ano_max): continue
                            loc = ad.get('locationDetails', {})
                            images = ad.get('images', [])
                            foto = images[0].get('original','') if images else ''
                            carros.append({
                                'titulo': titulo[:150], 'preco': preco, 'ano': ano, 'km': km,
                                'cambio': cambio, 'combustivel': combustivel,
                                'cor': cor, 'portas': portas, 'tipo': tipo,
                                'cidade': loc.get('municipality',''), 'estado': loc.get('uf',''),
                                'url': ad.get('url') or ad.get('friendlyUrl',''), 'foto': foto
                            })
                except: pass
            urls = set()
            unicos = []
            for c in carros:
                if c['url'] not in urls:
                    urls.add(c['url'])
                    unicos.append(c)
            return unicos
    query = f'{marca} {modelo}' if modelo else marca
    url = f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q={urllib.parse.quote(query)}'
    if uf: url += f'&sf=1&state={uf}'
    try:
        resp = scraper.get(url, timeout=40)
        if resp.status_code == 200:
            for ad in extrair_dados_json(resp.text):
                titulo = ad.get('title') or ad.get('subject', '')
                if not titulo or len(titulo) < 5: continue
                if marca and marca.lower() not in titulo.lower(): continue
                preco_str = ad.get('priceValue', '0')
                preco_clean = preco_str.replace('R$','').replace('.','').replace(',','.').strip()
                try: preco = float(preco_clean)
                except: continue
                if preco > preco_max: continue
                ano = 0; km = 0; cambio = ''; combustivel = ''; cor = ''; portas = 0; tipo = ''
                for p in ad.get('properties', []):
                    if p.get('name') == 'regdate':
                        try: ano = int(re.search(r'\d{4}', str(p.get('value','0'))).group())
                        except: pass
                    if p.get('name') == 'mileage': km = int(re.sub(r'\D','',p.get('value','0')))
                    if p.get('name') == 'gearbox': cambio = p.get('value','')
                    if p.get('name') == 'fuel': combustivel = p.get('value','')
                    if p.get('name') == 'carcolor': cor = p.get('value','')
                    if p.get('name') == 'doors': 
                        try: portas = int(re.sub(r'\D','',p.get('value','0')))
                        except: pass
                    if p.get('name') == 'cartype': tipo = p.get('value','')
                if ano > 2000: continue
                if 0 < ano < ano_min or (ano_max < 2000 and ano > ano_max): continue
                loc = ad.get('locationDetails', {})
                images = ad.get('images', [])
                foto = images[0].get('original','') if images else ''
                carros.append({
                    'titulo': titulo[:150], 'preco': preco, 'ano': ano, 'km': km,
                    'cambio': cambio, 'combustivel': combustivel,
                    'cor': cor, 'portas': portas, 'tipo': tipo,
                    'cidade': loc.get('municipality',''), 'estado': loc.get('uf',''),
                    'url': ad.get('url') or ad.get('friendlyUrl',''), 'foto': foto
                })
    except: pass
    return carros

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Rajadeira Classicos</title>
    <style>
        body { font-family: Arial; max-width: 950px; margin: 20px auto; padding: 15px; background: #f0f2f5; }
        .header { background: #e94560; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
        .card { background: white; border-radius: 0 0 10px 10px; padding: 20px; }
        select { padding: 8px; border: 1px solid #ddd; border-radius: 5px; width: 100%; margin: 3px 0; font-size: 13px; }
        button { background: #e94560; color: white; padding: 12px; border: none; border-radius: 5px; width: 100%; font-size: 16px; cursor: pointer; margin-top: 10px; }
        .result { border: 1px solid #ddd; padding: 12px; margin: 10px 0; border-radius: 8px; display: flex; gap: 15px; align-items: center; }
        .result-img { width: 120px; height: 90px; object-fit: cover; border-radius: 6px; background: #eee; }
        .preco { color: green; font-size: 1.3em; font-weight: bold; }
        .detalhes { color: #888; font-size: 0.85em; }
        a { color: #1565c0; text-decoration: none; }
        .classic-badge { background: #8B4513; color: gold; padding: 2px 8px; border-radius: 4px; font-size: 0.7em; }
        .filtro-row { display: flex; gap: 8px; flex-wrap: wrap; }
        .filtro-item { flex: 1; min-width: 100px; }
        label { font-weight: bold; font-size: 0.8em; color: #555; }
        .spinner { border: 4px solid #eee; border-top: 4px solid #e94560; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .sem-resultados { text-align: center; padding: 30px; color: #888; }
    </style>
</head>
<body>
    <div class="header"><h1>Rajadeira Classicos</h1><p>31 marcas • 1940 a 2000</p></div>
    <div class="card">
        <form method="GET" action="/buscar" onsubmit="document.getElementById('loading').style.display='block'; document.getElementById('resultados').style.display='none';">
            <div class="filtro-row">
                <div class="filtro-item">
                    <label>Marca</label>
                    <select name="marca" id="marca" onchange="atualizarModelos()">
                        <option value="">Todas</option>
                        {% for m in marcas %}<option value="{{ m }}" {% if marca_sel==m %}selected{% endif %}>{{ m }}</option>{% endfor %}
                    </select>
                </div>
                <div class="filtro-item">
                    <label>Modelo</label>
                    <select name="modelo" id="modelo"><option value="">Todos</option></select>
                </div>
            </div>
            <div class="filtro-row">
                <div class="filtro-item"><label>Preço máx</label><select name="preco_max">{% for p in precos %}<option value="{{ p }}" {% if preco_sel==p|string %}selected{% endif %}>R$ {{ "{:,.0f}".format(p) }}</option>{% endfor %}</select></div>
                <div class="filtro-item"><label>Estado</label><select name="uf">{% for s,n in estados %}<option value="{{ s }}" {% if uf_sel==s %}selected{% endif %}>{{ n }}</option>{% endfor %}</select></div>
                <div class="filtro-item"><label>KM máx</label><select name="km_max"><option value="">Todos</option>{% for k in kms %}<option value="{{ k }}" {% if km_sel==k|string %}selected{% endif %}>{{ "{:,.0f}".format(k) }} km</option>{% endfor %}</select></div>
            </div>
            <div class="filtro-row">
                <div class="filtro-item"><label>Ano inicial</label><select name="ano_min">{% for a in anos %}<option value="{{ a }}" {% if ano_min_sel==a|string %}selected{% endif %}>{{ a }}</option>{% endfor %}</select></div>
                <div class="filtro-item"><label>Ano final</label><select name="ano_max">{% for a in anos %}<option value="{{ a }}" {% if ano_max_sel==a|string %}selected{% endif %}>{{ a }}</option>{% endfor %}</select></div>
            </div>
            <div class="filtro-row">
                <div class="filtro-item"><label>Câmbio</label><select name="cambio"><option value="">Todos</option><option value="Automático" {% if cambio_sel=='Automático' %}selected{% endif %}>Automático</option><option value="Manual" {% if cambio_sel=='Manual' %}selected{% endif %}>Manual</option></select></div>
                <div class="filtro-item"><label>Combustível</label><select name="combustivel"><option value="">Todos</option>{% for c in ['Gasolina','Flex','Diesel','Híbrido','Elétrico'] %}<option value="{{ c }}" {% if comb_sel==c %}selected{% endif %}>{{ c }}</option>{% endfor %}</select></div>
                <div class="filtro-item"><label>Cor</label><select name="cor"><option value="">Todas</option>{% for c in cores %}<option value="{{ c }}" {% if cor_sel==c %}selected{% endif %}>{{ c }}</option>{% endfor %}</select></div>
            </div>
            <div class="filtro-row">
                <div class="filtro-item"><label>Tipo</label><select name="tipo"><option value="">Todos</option>{% for t in tipos %}<option value="{{ t }}" {% if tipo_sel==t %}selected{% endif %}>{{ t }}</option>{% endfor %}</select></div>
                <div class="filtro-item"><label>Portas</label><select name="portas"><option value="">Todas</option>{% for p in portas_opcoes %}<option value="{{ p }}" {% if portas_sel==p|string %}selected{% endif %}>{{ p }} portas</option>{% endfor %}</select></div>
                <div class="filtro-item"><label>Ordenar</label><select name="ordem"><option value="preco_asc" {% if ordem_sel=='preco_asc' %}selected{% endif %}>Menor Preço</option><option value="preco_desc" {% if ordem_sel=='preco_desc' %}selected{% endif %}>Maior Preço</option><option value="ano_desc" {% if ordem_sel=='ano_desc' %}selected{% endif %}>Mais Novo</option><option value="ano_asc" {% if ordem_sel=='ano_asc' %}selected{% endif %}>Mais Antigo</option><option value="km_asc" {% if ordem_sel=='km_asc' %}selected{% endif %}>Menor KM</option></select></div>
            </div>
            <button type="submit">BUSCAR CLASSICOS</button>
        </form>
        <div id="loading" style="display:none;"><div class="spinner"></div><p>Pesquisando...</p></div>
        <div id="resultados">
        {% if carros is defined and carros|length > 0 %}
        <p><b>{{ carros|length }} classicos encontrados</b></p>
        {% for c in carros %}
        <div class="result">
            {% if c.foto %}<img src="{{ c.foto }}" class="result-img" loading="lazy" referrerpolicy="no-referrer" crossorigin="anonymous">{% else %}<div class="result-img" style="display:flex; align-items:center; justify-content:center; font-size:2em;">🚗</div>{% endif %}
            <div style="flex:1;">
                <a href="{{ c.url }}" target="_blank"><b>{{ c.titulo[:120] }}</b></a><span class="classic-badge">CLASSICO</span>
                <br><span class="detalhes">
                    {{ c.ano if c.ano else 'N/D' }} | {{ c.km if c.km else 'N/D' }} km
                    {% if c.cambio %} | {{ c.cambio }}{% endif %}
                    {% if c.combustivel %} | {{ c.combustivel }}{% endif %}
                    {% if c.cor %} | {{ c.cor }}{% endif %}
                    {% if c.tipo %} | {{ c.tipo }}{% endif %}
                    {% if c.portas %} | {{ c.portas }}p{% endif %}
                    {% if c.cidade %} | {{ c.cidade }}/{{ c.estado }}{% endif %}
                </span>
            </div>
            <div><span class="preco">R$ {{ "{:,.2f}".format(c.preco) }}</span></div>
        </div>
        {% endfor %}
        {% elif carros is defined and carros|length == 0 %}
        <div class="sem-resultados">
            <p>😕 Nenhum classico encontrado com esses filtros.</p>
            <p>Tente ampliar a busca (remover filtros ou aumentar limites).</p>
        </div>
        {% endif %}
        </div>
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
    return render_template_string(HTML, marcas=sorted(MARCAS_CLASSICAS.keys()), carros=None, precos=PRECOS, estados=ESTADOS, anos=ANOS, kms=KMS, cores=CORES, tipos=TIPOS, portas_opcoes=PORTA_OPCOES, modelos_json=json.dumps(MARCAS_CLASSICAS), marca_sel='', preco_sel='999999', uf_sel='', km_sel='', ano_min_sel='1940', ano_max_sel='2000', cambio_sel='', comb_sel='', cor_sel='', tipo_sel='', portas_sel='', ordem_sel='preco_asc')

@app.route('/buscar')
def buscar():
    marca = request.args.get('marca', '')
    modelo = request.args.get('modelo', '')
    preco_max = float(request.args.get('preco_max', 999999) or 999999)
    ano_min = int(request.args.get('ano_min', 1940) or 1940)
    ano_max = int(request.args.get('ano_max', 2000) or 2000)
    uf = request.args.get('uf', '').upper()
    km_max = request.args.get('km_max', '')
    cambio = request.args.get('cambio', '')
    combustivel = request.args.get('combustivel', '')
    cor = request.args.get('cor', '')
    tipo = request.args.get('tipo', '')
    portas = request.args.get('portas', '')
    ordem = request.args.get('ordem', 'preco_asc')
    
    carros = buscar_olx(marca, modelo, preco_max, ano_min, ano_max, uf)
    
    if km_max:
        km = int(km_max)
        carros = [c for c in carros if c.get('km', 0) and c['km'] <= km]
    if cambio: carros = [c for c in carros if c.get('cambio', '').lower() == cambio.lower()]
    if combustivel: carros = [c for c in carros if c.get('combustivel', '').lower() == combustivel.lower()]
    if cor: carros = [c for c in carros if c.get('cor', '').lower() == cor.lower()]
    if tipo: carros = [c for c in carros if c.get('tipo', '').lower() == tipo.lower()]
    if portas: carros = [c for c in carros if c.get('portas', 0) == int(portas)]
    
    if ordem == 'preco_asc': carros.sort(key=lambda x: x['preco'])
    elif ordem == 'preco_desc': carros.sort(key=lambda x: x['preco'], reverse=True)
    elif ordem == 'ano_desc': carros.sort(key=lambda x: x['ano'], reverse=True)
    elif ordem == 'ano_asc': carros.sort(key=lambda x: x['ano'])
    elif ordem == 'km_asc': carros.sort(key=lambda x: x.get('km', 999999) if x.get('km', 0) > 0 else 999999)
    
    carros = carros[:500]
    
    return render_template_string(HTML, marcas=sorted(MARCAS_CLASSICAS.keys()), carros=carros, precos=PRECOS, estados=ESTADOS, anos=ANOS, kms=KMS, cores=CORES, tipos=TIPOS, portas_opcoes=PORTA_OPCOES, modelos_json=json.dumps(MARCAS_CLASSICAS), marca_sel=marca, preco_sel=str(int(preco_max)), uf_sel=uf, km_sel=km_max, ano_min_sel=str(ano_min), ano_max_sel=str(ano_max), cambio_sel=cambio, comb_sel=combustivel, cor_sel=cor, tipo_sel=tipo, portas_sel=portas, ordem_sel=ordem)

if __name__ == '__main__':
    print('='*50)
    print('RAJADEIRA CLASSICOS - FILTROS MANTIDOS')
    print('http://localhost:5000')
    print('='*50)
    app.run(debug=False, host='0.0.0.0', port=5000)
