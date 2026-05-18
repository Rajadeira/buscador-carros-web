from flask import Flask, render_template_string, request
import cloudscraper
from bs4 import BeautifulSoup
import re
import urllib.parse
import json
from datetime import datetime

app = Flask(__name__)
scraper = cloudscraper.create_scraper()

MARCAS_CLASSICAS = {
    "Ford": ["Corcel", "Belina", "Del Rey", "Maverick", "Galaxie", "Landau", "F-1000", "Pampa", "Escort", "Verona", "Ka", "Fiesta"],
    "Chevrolet": ["Opala", "Chevette", "Monza", "Caravan", "Kadett", "Ipanema", "Diplomata", "Comodoro", "Brasilia", "C10", "D20", "S10", "Blazer"],
    "Volkswagen": ["Fusca", "Kombi", "Brasília", "SP2", "Gol", "Passat", "Santana", "Quantum", "Voyage", "Parati", "Saveiro", "Apollo"],
    "Fiat": ["Uno", "Mille", "Elba", "Premio", "Oggi", "Panorama", "Tempra", "Tipo", "Bravo", "Marea", "Ducato"],
    "Chrysler": ["Dart", "Charger", "Polara", "Magnum", "LeBaron", "Caravan", "Town & Country"],
    "Dodge": ["Dart", "Charger", "Polara", "Magnum", "LeBaron", "Dakota", "Ram"],
    "Plymouth": ["Valiant", "Belvedere", "Fury", "Satellite", "Barracuda", "Duster"],
    "Willys": ["Jeep", "Pickup", "Rural", "Interlagos", "Itamaraty"],
    "Toyota": ["Corolla", "Hilux", "Bandeirante", "Supra", "Celica"],
    "Mercedes-Benz": ["280S", "450SEL", "500SEC", "190E", "300E", "SL500"],
    "Citroën": ["2CV", "Dyane", "Ami", "GS", "CX", "BX", "XM", "ZX"],
    "Peugeot": ["504", "505", "205", "306", "406"],
    "Renault": ["Dauphine", "Gordini", "12", "19", "21", "Laguna"],
    "Alfa Romeo": ["Giulia", "Spider", "164", "156"],
    "BMW": ["2002", "320i", "325i", "528i", "635CSi", "M3 E30", "M5 E28", "Z1", "840Ci", "850i"],
    "Jaguar": ["XJ6", "XJS", "E-Type", "Mark 2"],
    "Mitsubishi": ["Eclipse", "3000GT", "Pajero", "L200"],
    "Nissan": ["300ZX", "Silvia", "Skyline", "Pathfinder"],
    "Subaru": ["Impreza", "Legacy", "Forester", "SVX"],
    "Volvo": ["240", "740", "760", "850", "960", "P1800"],
}

# (funções auxiliares permanecem idênticas)

def extrair_precos_da_listagem(soup):
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and '__INITIAL_STATE__' in script.string:
            try:
                json_str = script.string.split('__INITIAL_STATE__=')[1].split(';\n')[0]
                data = json.loads(json_str)
                ads = data.get('listingProps', {}).get('adList', [])
                if not ads: ads = data.get('ads', [])
                if not ads: ads = data.get('results', [])
                precos = {}
                for ad in ads:
                    url = ad.get('url') or ad.get('permalink')
                    price = ad.get('price') or ad.get('priceValue')
                    if url and price:
                        precos[url] = float(price)
                return precos
            except: pass
    return {}

def extrair_preco_card(parent, texto):
    for classe in ['price', 'preco', 'ad__price', 'actual-price', 'olx-text--heading-2', 'm7nrfa-', 'sc-ifAKCX']:
        elem = parent.find(['span', 'div', 'h2', 'h3'], class_=re.compile(classe, re.IGNORECASE))
        if elem:
            match = re.search(r'R\$\s*([\d.]+)', elem.get_text(strip=True))
            if match:
                try:
                    val = float(match.group(1).replace('.', ''))
                    if 1000 <= val <= 5000000: return val
                except: pass
    match = re.search(r'R\$\s*([\d.]+)', texto)
    if match:
        try:
            val = float(match.group(1).replace('.', ''))
            if 1000 <= val <= 5000000: return val
        except: pass
    for attr in ['aria-label', 'data-price', 'content']:
        val = parent.get(attr)
        if val:
            match = re.search(r'(\d{1,3}(?:\.\d{3})+)', val)
            if match:
                try:
                    val = float(match.group(1).replace('.', ''))
                    if 1000 <= val <= 5000000: return val
                except: pass
    return 0

def extrair_preco_pagina(url_anuncio):
    try:
        resp = scraper.get(url_anuncio, timeout=6)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            meta = soup.find('meta', itemprop='price') or soup.find('meta', property='product:price:amount')
            if meta and meta.get('content'):
                try: return float(meta['content'])
                except: pass
            for classe in ['price', 'preco', 'ad__price', 'actual-price', 'olx-text--heading-2']:
                elem = soup.find(['span', 'div', 'h2', 'h3'], class_=re.compile(classe, re.IGNORECASE))
                if elem:
                    match = re.search(r'R\$\s*([\d.]+)', elem.get_text(strip=True))
                    if match:
                        try:
                            val = float(match.group(1).replace('.', ''))
                            if 1000 <= val <= 5000000: return val
                        except: pass
            textos = soup.find_all(string=re.compile(r'R\$\s*[\d.]+'))
            precos = []
            for t in textos:
                texto = t.strip()
                if re.search(r'\d+x\s*R\$', texto): continue
                match = re.search(r'R\$\s*([\d.]+)', texto)
                if match:
                    try:
                        val = float(match.group(1).replace('.', ''))
                        if 1000 <= val <= 5000000: precos.append(val)
                    except: pass
            if precos: return max(precos)
    except: pass
    return 0

def buscar_olx(marca, modelo, preco_max=999999, ano_min=1940, ano_max=2000, km_min=0, km_max=999999, uf='', pagina=1):
    carros = []
    query_parts = []
    if marca: query_parts.append(marca)
    if modelo: query_parts.append(modelo)
    query = ' '.join(query_parts).strip()
    if not query: return []
    
    url = f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q={urllib.parse.quote(query)}&o={pagina}'
    if uf:
        url += f'&sf=1&state={uf}'
    
    # Se um modelo específico foi escolhido, usamos só ele. Senão, usamos TODOS os modelos clássicos da marca.
    if modelo:
        modelos_filtro = [modelo]
    else:
        # Se a marca está no dicionário, aplica filtro pelos modelos; senão, sem filtro (caso "Todas" marcas)
        modelos_filtro = MARCAS_CLASSICAS.get(marca, [])
    
    print(f'🔍 Buscando: {url}')
    try:
        resp = scraper.get(url, timeout=20)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            precos_json = extrair_precos_da_listagem(soup)
            print(f'   Preços JSON: {len(precos_json)}')
            
            links = soup.find_all('a', href=re.compile(r'-\d{9,}'))
            urls_vistas = set()
            for link in links:
                href = link.get('href', '')
                if href.startswith('/'): href = 'https://www.olx.com.br' + href
                if href not in urls_vistas and 'olx.com.br' in href:
                    urls_vistas.add(href)
                    parent = link.find_parent(['li', 'div', 'section'])
                    texto = parent.get_text(' ', strip=True) if parent else link.get_text(strip=True)
                    titulo = link.get_text(strip=True) or texto[:150]
                    
                    # Filtro por modelos (se houver lista)
                    if modelos_filtro:
                        padrao_modelos = '|'.join(re.escape(m) for m in modelos_filtro)
                        if not re.search(padrao_modelos, titulo, re.IGNORECASE):
                            continue
                    
                    ano = 0
                    ano_match = re.search(r'\b(19[4-9][0-9]|20[0-2][0-9])\b', titulo)
                    if not ano_match:
                        ano_match = re.search(r'\b(19[4-9][0-9]|20[0-2][0-9])\b', texto)
                    if ano_match:
                        ano = int(ano_match.group(1))
                    
                    if ano > 2000:
                        continue
                    if 0 < ano < ano_min or (ano_max < 2000 and ano > ano_max):
                        continue
                    
                    # Se ano não detectado e não estamos filtrando por modelo, rejeitar fortes indícios de moderno
                    if ano == 0 and not modelos_filtro:
                        termos_modernos = ['flex', '1.0', '1.4', '1.5', '1.6', '1.8', '2.0', '16v', 'vvt', 'multimídia', 'multimidia', 'digital', 'turbo', 'câmbio automático', 'automático', 'aut.', 'start-stop']
                        if any(termo in titulo.lower() for termo in termos_modernos):
                            continue
                    
                    preco = precos_json.get(href, 0)
                    if preco == 0:
                        preco = extrair_preco_card(parent, texto)
                    
                    km = 0
                    km_match = re.search(r'(\d{1,3}(?:\.\d{3})*)\s*km', texto, re.IGNORECASE)
                    if km_match: km = int(km_match.group(1).replace('.', ''))
                    
                    if km > 0:
                        if km < km_min: continue
                        if km_max < 999999 and km > km_max: continue
                    
                    cambio = ''
                    if re.search(r'aut[oá]m[áa]tic[oa]', texto, re.IGNORECASE): cambio = 'Automático'
                    elif re.search(r'manual', texto, re.IGNORECASE): cambio = 'Manual'
                    
                    combustivel = ''
                    for tipo in ['Flex','Gasolina','Diesel','Elétrico','Híbrido']:
                        if re.search(tipo.lower(), texto, re.IGNORECASE): combustivel = tipo; break
                    
                    cidade = estado = ''
                    loc_match = re.search(r'https?://([a-z]{2})\.olx\.com\.br/([^/]+)/', href)
                    if loc_match:
                        estado = loc_match.group(1).upper()
                        cidade = loc_match.group(2).replace('-', ' ').title()
                    
                    carros.append({
                        'titulo': titulo[:150], 'preco': preco, 'ano': ano, 'km': km,
                        'cambio': cambio, 'combustivel': combustivel,
                        'cidade': cidade, 'estado': estado, 'url': href
                    })
            
            if uf:
                carros = [c for c in carros if c['estado'].upper() == uf]
            
            sem_preco = [c for c in carros if c['preco'] == 0]
            if sem_preco:
                print(f'📋 {len(carros)} listados, {len(sem_preco)} sem preço. Extraindo páginas individuais...')
                for i, carro in enumerate(sem_preco):
                    print(f'   {i+1}/{len(sem_preco)}: {carro["titulo"][:60]}...')
                    carro['preco'] = extrair_preco_pagina(carro['url'])
            
            carros = [c for c in carros if not (c['preco'] > 0 and c['preco'] > preco_max)]
            carros.sort(key=lambda x: (0 if x['preco'] > 0 else 1, x['preco']))
            print(f'✅ Final: {len(carros)} anúncios (preço máx R$ {preco_max})')
    except Exception as e:
        print(f'Erro: {e}')
    return carros

def buscar_fipe(marca, modelo, ano=1980):
    try:
        resp = scraper.get('https://parallelum.com.br/fipe/api/v1/carros/marcas', timeout=10)
        marcas = resp.json()
        marca_obj = next((m for m in marcas if marca.lower() in m['nome'].lower()), None)
        if not marca_obj: return None
        resp2 = scraper.get(f"https://parallelum.com.br/fipe/api/v1/carros/marcas/{marca_obj['codigo']}/modelos", timeout=10)
        modelos = resp2.json()
        modelo_obj = next((m for m in modelos['modelos'] if modelo.lower() in m['nome'].lower()), None)
        if not modelo_obj: return None
        resp3 = scraper.get(f"https://parallelum.com.br/fipe/api/v1/carros/marcas/{marca_obj['codigo']}/modelos/{modelo_obj['codigo']}/anos", timeout=10)
        anos = resp3.json()
        ano_str = next((a for a in anos if str(ano) in a['nome']), None)
        if not ano_str: ano_str = next((a for a in anos if '199' in a['nome']), None)
        if not ano_str: return None
        resp4 = scraper.get(f"https://parallelum.com.br/fipe/api/v1/carros/marcas/{marca_obj['codigo']}/modelos/{modelo_obj['codigo']}/anos/{ano_str['codigo']}", timeout=10)
        dados = resp4.json()
        return float(dados['Valor'].replace('R$', '').replace('.', '').replace(',', '.'))
    except: return None

# (HTML permanece o mesmo)
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Rajadeira Clássicos</title>
    <style>
        body { font-family: 'Segoe UI', Arial; max-width: 900px; margin: 20px auto; padding: 0 15px; background: #f0f2f5; }
        .header { background: #e94560; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
        .card { background: white; border-radius: 0 0 10px 10px; padding: 20px; }
        .form-row { display: flex; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
        .form-group { flex: 1; min-width: 120px; }
        label { font-weight: 600; font-size: 0.85em; color: #555; display: block; margin-bottom: 3px; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #e94560; color: white; border: none; border-radius: 5px; font-size: 16px; font-weight: 700; cursor: pointer; margin-top: 10px; }
        button:hover { background: #c23152; }
        .fipe-box { background: #fff3e0; border-left: 4px solid #ff9800; padding: 12px; margin: 15px 0; border-radius: 5px; }
        .result { border: 1px solid #e0e0e0; padding: 15px; margin: 10px 0; border-radius: 8px; background: #fafafa; }
        .preco { color: #2e7d32; font-size: 1.3em; font-weight: bold; }
        .abaixo-fipe { background: #e8f5e9; color: #2e7d32; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
        .detalhes { color: #888; font-size: 0.9em; }
        a { color: #1565c0; text-decoration: none; }
        .classic-badge { background: #8B4513; color: #FFD700; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 8px; }
        .no-price { color: #999; }
        #loading { display: none; text-align: center; padding: 40px; }
        .spinner { border: 4px solid rgba(0,0,0,0.1); border-left-color: #e94560; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 15px; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="header"><h1>🏆 Rajadeira Clássicos</h1><p>Carros antigos de 1940 a 2000</p></div>
    <div class="card">
        <form method="GET" action="/buscar" onsubmit="return showLoading()">
            <div class="form-row">
                <div class="form-group">
                    <label>🏭 Marca</label>
                    <select name="marca" id="marca" onchange="atualizarModelos()">
                        <option value="">Todas</option>
                        {% for marca in marcas_lista %}
                        <option value="{{ marca }}" {% if marca_selecionada==marca %}selected{% endif %}>{{ marca }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label>🚙 Modelo</label>
                    <select name="modelo" id="modelo">
                        <option value="">Todos</option>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>💰 Preço máximo</label>
                    <select name="preco_max">
                        <option value="999999">Sem limite</option>
                        {% for preco in precos_lista %}
                        <option value="{{ preco }}" {% if preco_max_str==preco|string %}selected{% endif %}>R$ {{ "{:,.0f}".format(preco).replace(",", "X").replace(".", ",").replace("X", ".") }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label>📍 Estado</label>
                    <select name="uf">
                        <option value="">Todos</option>
                        {% for sigla, nome in estados %}
                        <option value="{{ sigla }}" {% if uf==sigla %}selected{% endif %}>{{ nome }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label>🏁 Quilometragem</label>
                    <select name="km_filtro">
                        <option value="">Todos</option>
                        {% for km_val in km_opcoes %}
                        <option value="{{ km_val }}" {% if km_selecionado==km_val|string %}selected{% endif %}>{{ "{:,.0f}".format(km_val).replace(",", "X").replace(".", ",").replace("X", ".") }} km</option>
                        {% endfor %}
                        <option value="above_100000" {% if km_selecionado=='above_100000' %}selected{% endif %}>Acima de 100.000 km</option>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>📅 Ano inicial</label>
                    <select name="ano_min">
                        <option value="">Todos</option>
                        {% for ano in anos_lista %}
                        <option value="{{ ano }}" {% if ano_min_str==ano|string %}selected{% endif %}>{{ ano }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label>📅 Ano final</label>
                    <select name="ano_max">
                        <option value="">Todos</option>
                        {% for ano in anos_lista %}
                        <option value="{{ ano }}" {% if ano_max_str==ano|string %}selected{% endif %}>{{ ano }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>⚙️ Câmbio</label>
                    <select name="cambio"><option value="">Todos</option><option value="Automático" {% if cambio=='Automático' %}selected{% endif %}>Automático</option><option value="Manual" {% if cambio=='Manual' %}selected{% endif %}>Manual</option></select>
                </div>
                <div class="form-group">
                    <label>⛽ Combustível</label>
                    <select name="combustivel"><option value="">Todos</option>{% for tipo in ['Gasolina','Diesel'] %}<option value="{{tipo}}" {% if combustivel==tipo %}selected{% endif %}>{{tipo}}</option>{% endfor %}</select>
                </div>
                <div class="form-group">
                    <label>📊 Ordenar</label>
                    <select name="ordem">
                        <option value="preco_asc" {% if ordem=='preco_asc' %}selected{% endif %}>Menor Preço</option>
                        <option value="preco_desc" {% if ordem=='preco_desc' %}selected{% endif %}>Maior Preço</option>
                        <option value="ano_desc" {% if ordem=='ano_desc' %}selected{% endif %}>Mais Novo</option>
                        <option value="ano_asc" {% if ordem=='ano_asc' %}selected{% endif %}>Mais Antigo</option>
                    </select>
                </div>
            </div>
            <button type="submit">🔍 BUSCAR CLÁSSICOS</button>
        </form>
        <div id="loading">
            <div class="spinner"></div>
            <p>🔍 Pesquisando anúncios na OLX...</p>
            <p style="font-size:0.9em; color:#888;">Isso pode levar alguns segundos</p>
        </div>
        <div id="resultados">
        {% if carros is defined %}
        <br>
        {% if fipe %}<div class="fipe-box">💰 FIPE (ref. 1980): R$ {{ "{:,.2f}".format(fipe).replace(",", "X").replace(".", ",").replace("X", ".") }}</div>{% endif %}
        <p><b>{{ carros|length }} clássicos encontrados</b></p>
        {% for c in carros %}
        <div class="result">
            <a href="{{ c.url }}" target="_blank"><b>{{ c.titulo[:120] }}</b></a><span class="classic-badge">CLÁSSICO</span>
            <br>
            <span class="detalhes">
                📅 {{ c.ano if c.ano else 'N/D' }} • 🏁 {{ "{:,.0f}".format(c.km).replace(",", "X").replace(".", ",").replace("X", ".") if c.km else 'N/D' }} km
                {% if c.cambio %} • ⚙️ {{ c.cambio }}{% endif %}
                {% if c.combustivel %} • ⛽ {{ c.combustivel }}{% endif %}
                {% if c.cidade %} • 📍 {{ c.cidade }}/{{ c.estado }}{% endif %}
            </span>
            <span style="float:right; text-align:right;">
                {% if c.preco > 0 %}
                <span class="preco">R$ {{ "{:,.2f}".format(c.preco).replace(",", "X").replace(".", ",").replace("X", ".") }}</span>
                {% if fipe and c.preco < fipe %}<span class="abaixo-fipe">⬇️ FIPE</span>{% endif %}
                {% else %}
                <span class="no-price">Preço não extraído</span>
                {% endif %}
            </span>
        </div>
        {% endfor %}
        {% endif %}
        </div>
    </div>

    <script>
        const MODELOS = {{ modelos_json | safe }};

        function atualizarModelos() {
            const marca = document.getElementById('marca').value;
            const modeloSelect = document.getElementById('modelo');
            modeloSelect.innerHTML = '<option value="">Todos</option>';
            
            if (marca && MODELOS[marca]) {
                MODELOS[marca].forEach(function(modelo) {
                    const option = document.createElement('option');
                    option.value = modelo;
                    option.textContent = modelo;
                    modeloSelect.appendChild(option);
                });
            }
        }

        window.addEventListener('load', function() {
            atualizarModelos();
            const modeloSelecionado = "{{ modelo_selecionado }}";
            if (modeloSelecionado) {
                const modeloSelect = document.getElementById('modelo');
                for (let i = 0; i < modeloSelect.options.length; i++) {
                    if (modeloSelect.options[i].value === modeloSelecionado) {
                        modeloSelect.selectedIndex = i;
                        break;
                    }
                }
            }
        });

        function showLoading() {
            document.getElementById('resultados').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
            return true;
        }
    </script>
</body>
</html>
"""

ESTADOS = [
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
    ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
    ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"), ("SC", "Santa Catarina"),
    ("SP", "São Paulo"), ("SE", "Sergipe"), ("TO", "Tocantins")
]

ANOS_LISTA = list(range(1940, 2001))
KM_OPCOES = [5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000,
             55000, 60000, 65000, 70000, 75000, 80000, 85000, 90000, 95000, 100000]
PRECOS_LISTA = [5000, 10000, 15000, 20000, 25000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000,
                120000, 150000, 180000, 200000, 250000, 300000, 400000, 500000]

@app.route('/')
def index():
    return render_template_string(HTML,
        marcas_lista=sorted(MARCAS_CLASSICAS.keys()),
        marca_selecionada='',
        modelo_selecionado='',
        preco_max_str='999999',
        ano_min_str='', ano_max_str='', km_selecionado='',
        uf='', cambio='', combustivel='', ordem='preco_asc',
        fipe=None, carros=[], estados=ESTADOS,
        anos_lista=ANOS_LISTA, km_opcoes=KM_OPCOES, precos_lista=PRECOS_LISTA,
        modelos_json=json.dumps(MARCAS_CLASSICAS)
    )

@app.route('/buscar')
def buscar():
    marca = request.args.get('marca', '')
    modelo = request.args.get('modelo', '')
    preco_max_str = request.args.get('preco_max', '999999')
    preco_max = float(preco_max_str) if preco_max_str else 999999
    ano_min_str = request.args.get('ano_min', '')
    ano_max_str = request.args.get('ano_max', '')
    km_filtro = request.args.get('km_filtro', '')
    uf = request.args.get('uf', '').upper()
    cambio = request.args.get('cambio', '')
    combustivel = request.args.get('combustivel', '')
    ordem = request.args.get('ordem', 'preco_asc')
    
    ano_min = int(ano_min_str) if ano_min_str else 1940
    ano_max = int(ano_max_str) if ano_max_str else 2000
    
    km_min = 0
    km_max = 999999
    if km_filtro == 'above_100000':
        km_min = 100001
        km_max = 999999
    elif km_filtro:
        km_max = int(km_filtro)
    
    search_marca = marca if marca else ''
    search_modelo = modelo if modelo else ''
    
    carros = []
    if search_marca or search_modelo:
        carros = buscar_olx(search_marca, search_modelo, preco_max, ano_min, ano_max, km_min, km_max, uf, pagina=1)
    
    if cambio: carros = [c for c in carros if c['cambio'].lower() == cambio.lower()]
    if combustivel: carros = [c for c in carros if c['combustivel'].lower() == combustivel.lower()]
    
    if ordem == 'preco_asc': carros.sort(key=lambda x: (0 if x['preco'] > 0 else 1, x['preco']))
    elif ordem == 'preco_desc': carros.sort(key=lambda x: x['preco'] if x['preco'] > 0 else 0, reverse=True)
    elif ordem == 'ano_desc': carros.sort(key=lambda x: x['ano'], reverse=True)
    elif ordem == 'ano_asc': carros.sort(key=lambda x: x['ano'])
    
    fipe = None
    if search_marca and search_modelo:
        fipe = buscar_fipe(search_marca, search_modelo, 1980)
    
    return render_template_string(HTML,
        marcas_lista=sorted(MARCAS_CLASSICAS.keys()),
        marca_selecionada=search_marca,
        modelo_selecionado=search_modelo,
        preco_max_str=preco_max_str,
        ano_min_str=ano_min_str, ano_max_str=ano_max_str,
        km_selecionado=km_filtro,
        uf=uf, cambio=cambio, combustivel=combustivel, ordem=ordem,
        fipe=fipe, carros=carros[:50], estados=ESTADOS,
        anos_lista=ANOS_LISTA, km_opcoes=KM_OPCOES, precos_lista=PRECOS_LISTA,
        modelos_json=json.dumps(MARCAS_CLASSICAS)
    )

if __name__ == '__main__':
    print('='*50)
    print('🏆 RAJADEIRA CLÁSSICOS')
    print('🌐 http://localhost:5000')
    print('='*50)
    app.run(debug=False, host='0.0.0.0', port=5000)
