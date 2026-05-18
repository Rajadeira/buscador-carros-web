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
    "Chevrolet": ["Bel Air","Impala","Opala","Chevette","Monza","Kadett","Vectra","Omega","Astra","Corsa","Ipanema","Suprema","Camaro","Corvette","Marajó","Chevy 500","A10","A14","A20","C10","C14","C15","C20","D10","D14","D20","Bonanza","Veraneio","S10","Blazer","Silverado","Caminhão 40","Caminhão 6100","Caminhão 6500","Caminhão 7100"],
    "Ford": ["Galaxie","Landau","Maverick","Corcel","Corcel II","Del Rey","Belina","Belina II","Escort","Versailles","Fiesta","Ka","Mondeo","Mustang","Galaxy","Explorer","Pampa","F-75","F-100","F-1000","F-250","Ranger","F-350","F-4000","F-7000","F-11000","F-14000","Cargo 815","Cargo 1317","Cargo 1617","Cargo 2428","Transcontinental"],
    "Volkswagen": ["Fusca","Karmann Ghia","Brasília","Variant","Variant II","Passat","Gol","Voyage","Parati","Fox","Santana","Quantum","Apollo","Logus","Pointer","Golf","Polo","Jetta","Corrado","Kombi","Saveiro","VW 7.90","VW 8.120","VW 9.150","VW 11.130","VW 13.180","VW 15.180","VW 16.220","VW 18.310","VW 35.300"],
    "Fiat": ["147","Spazio","Panorama","Prêmio","Elba","Uno","Tempra","Tipo","Marea","Brava","Bravo","Palio","Siena","Palio Weekend","Punto","Fiat Coupé","Fiorino","Ducato"],
    "Mercedes-Benz": ["190","C180","C220","C280","C36 AMG","E230","E280","E320","S320","S420","S500","SLK 230","CLK 230","CLK 320","ML 320","A160","A190","Sprinter","L-312","L-608","L-1113","L-1313","L-1513","L-1519","L-1620","L-1720","LS-1935","LS-2635","Atego 1418","Actros 1835"],
    "Toyota": ["Corona","Corolla","Camry","Celica","MR2","RAV4","Bandeirante","Land Cruiser","Hilux","SW4","Prado"],
    "Honda": ["Civic","Accord","Prelude","CR-V","City","Legend","NSX"],
    "Nissan": ["Sentra","Pathfinder","Frontier","Pickup D21","Maxima","200SX","Bluebird"],
    "Mitsubishi": ["Lancer","Galant","Eclipse","Pajero Full","Pajero Sport","Pajero TR4","L200","Space Wagon","3000GT"],
    "Subaru": ["Legacy","Impreza","Forester","Outback"],
    "Mazda": ["323","626","MX-5 Miata","RX-7"],
    "Renault": ["R-4","R-8","R-10","R-12","R-18","R-19","Clio","Mégane","Laguna","Scenic","Trafic","Master"],
    "Peugeot": ["404","504","106","205","206","306","405","406","605","Partner"],
    "Citroën": ["AX","BX","ZX","Saxo","Xsara","Xantia","Berlingo","Jumper"],
    "BMW": ["318i","320i","323i","328i","M3","520i","528i","540i","730i","740i","750iL","Z3 1.8","Z3 2.8"],
    "Hyundai": ["Accent","Elantra","Sonata","Galloper","Tucson"],
    "Kia": ["Sephia","Sportage","Carnival"],
    "Daewoo": ["Lanos","Nubira","Leganza","Espero","Tico"],
    "Volvo": ["240","440","460","850","S40","S70","S80","V40","V70","C70","XC70","N10","N12","NL10","NL12","FM7","FM10","FM12","FH12","FH16"],
    "Saab": ["900","9000","9-3","9-5"],
    "Scania": ["L-111","L-112","L-141","R-112","R-113","R-124","R-164","T-113","T-124"],
    "Land Rover": ["Series II/III","Defender","Discovery","Freelander","Range Rover"],
    "Jaguar": ["XJ6","XJ8","XJR","XK8","XJS"],
    "Audi": ["80","90","100","200","A3","A4","A4 Avant","A6","A6 Avant","A8","S4","S6","Cabriolet","Coupé"],
    "Porsche": ["911 Carrera","911 Turbo","Boxster","928","944","968"],
    "Alfa Romeo": ["145","146","155","156","164","GTV","Spider"],
    "Gurgel": ["X-12","X-15","Tocantins","Carajás","BR-800","E-400"],
    "Puma": ["GTB","GTC","GTS","AMV"]
}

def extrair_dados_json(html):
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.find('script', id='__NEXT_DATA__', type='application/json')
    if not script: return []
    try:
        data = json.loads(script.string)
        ads = data.get('props', {}).get('pageProps', {}).get('ads', [])
        return ads
    except:
        return []

def buscar_olx(marca, modelo, preco_max=999999, ano_min=1940, ano_max=2000, km_min=0, km_max=999999, uf='', pagina=1):
    carros = []
    
    if marca and modelo:
        query = f'{marca} {modelo}'
    elif marca:
        modelos = MARCAS_CLASSICAS.get(marca, [])
        if modelos:
            query = ' '.join(modelos[:8])
        else:
            query = marca
    else:
        return []
    
    url = f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q={urllib.parse.quote(query)}&o={pagina}'
    if uf:
        url += f'&sf=1&state={uf}'
    
    print(f'🔍 Buscando: {url}')
    try:
        resp = scraper.get(url, timeout=40)
        if resp.status_code == 200:
            ads = extrair_dados_json(resp.text)
            print(f'   Anúncios no JSON: {len(ads)}')
            
            for ad in ads:
                titulo = ad.get('title') or ad.get('subject', '')
                if not titulo or len(titulo) < 5:
                    continue
                
                # CORREÇÃO DO PREÇO
                preco_str = ad.get('priceValue', '0')
                preco_clean = preco_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
                try:
                    preco = float(preco_clean)
                except:
                    preco = 0
                if preco <= 0:
                    continue
                
                # Ano
                ano = 0
                props = ad.get('properties', [])
                for p in props:
                    if p.get('name') == 'regdate':
                        ano_val = p.get('value', '0')
                        try:
                            ano = int(re.search(r'\d{4}', str(ano_val)).group())
                        except:
                            pass
                        break
                
                km = 0
                for p in props:
                    if p.get('name') == 'mileage':
                        km = int(re.sub(r'\D', '', p.get('value', '0')))
                        break
                cambio = ''
                for p in props:
                    if p.get('name') == 'gearbox':
                        cambio = p.get('value', '')
                        break
                combustivel = ''
                for p in props:
                    if p.get('name') == 'fuel':
                        combustivel = p.get('value', '')
                        break
                
                cidade = ''
                estado = ''
                loc = ad.get('locationDetails', {})
                if loc:
                    cidade = loc.get('municipality', '')
                    estado = loc.get('uf', '')
                
                url_anuncio = ad.get('url') or ad.get('friendlyUrl', '')
                images = ad.get('images', [])
                foto = images[0].get('original') if images else ''
                
                if ano > 2000: continue
                if 0 < ano < ano_min or (ano_max < 2000 and ano > ano_max): continue
                if km and (km < km_min or (km_max < 999999 and km > km_max)): continue
                if uf and estado.upper() != uf.upper(): continue
                
                carros.append({
                    'titulo': titulo[:150], 'preco': preco, 'ano': ano, 'km': km,
                    'cambio': cambio, 'combustivel': combustivel,
                    'cidade': cidade, 'estado': estado, 'url': url_anuncio,
                    'foto': foto
                })
            
            if len(carros) < 30 and not modelo and pagina == 1:
                print(f'   Poucos resultados ({len(carros)}), buscando página 2...')
                carros_pag2 = buscar_olx(marca, modelo, preco_max, ano_min, ano_max, km_min, km_max, uf, pagina=2)
                carros.extend(carros_pag2)
            
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
        .result { border: 1px solid #e0e0e0; padding: 15px; margin: 10px 0; border-radius: 8px; background: #fafafa; display: flex; align-items: center; gap: 15px; }
        .result:hover { border-color: #e94560; background: #fff5f5; }
        .result-img { width: 120px; height: 90px; object-fit: cover; border-radius: 6px; background: #eee; flex-shrink: 0; }
        .result-info { flex: 1; }
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
            {% if c.foto %}
            <img src="{{ c.foto }}" class="result-img" alt="Foto" onerror="this.style.display='none'">
            {% else %}
            <div class="result-img" style="background:#eee; display:flex; align-items:center; justify-content:center; color:#aaa; font-size:2em;">🚗</div>
            {% endif %}
            <div class="result-info">
                <a href="{{ c.url }}" target="_blank"><b>{{ c.titulo[:120] }}</b></a><span class="classic-badge">CLÁSSICO</span>
                <br>
                <span class="detalhes">
                    📅 {{ c.ano if c.ano else 'N/D' }} • 🏁 {{ "{:,.0f}".format(c.km).replace(",", "X").replace(".", ",").replace("X", ".") if c.km else 'N/D' }} km
                    {% if c.cambio %} • ⚙️ {{ c.cambio }}{% endif %}
                    {% if c.combustivel %} • ⛽ {{ c.combustivel }}{% endif %}
                    {% if c.cidade %} • 📍 {{ c.cidade }}/{{ c.estado }}{% endif %}
                </span>
            </div>
            <div style="text-align:right; margin-left:auto;">
                {% if c.preco > 0 %}
                <span class="preco">R$ {{ "{:,.2f}".format(c.preco).replace(",", "X").replace(".", ",").replace("X", ".") }}</span>
                {% if fipe and c.preco < fipe %}<span class="abaixo-fipe">⬇️ FIPE</span>{% endif %}
                {% else %}
                <span class="no-price">Preço sob consulta</span>
                {% endif %}
            </div>
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
