from flask import Flask, render_template_string, request
import cloudscraper
from bs4 import BeautifulSoup
import re
import urllib.parse
from datetime import datetime

app = Flask(__name__)
scraper = cloudscraper.create_scraper()

def extrair_preco_card(parent, texto):
    """Tenta extrair o preço diretamente do HTML do card, sem acessar a página do anúncio."""
    # 1. Procurar spans com classe de preço
    for classe in ['price', 'preco', 'ad__price', 'actual-price', 'olx-text--heading-2', 'm7nrfa-', 'sc-ifAKCX']:
        elem = parent.find(['span', 'div', 'h2', 'h3'], class_=re.compile(classe, re.IGNORECASE))
        if elem:
            match = re.search(r'R\$\s*([\d.]+)', elem.get_text(strip=True))
            if match:
                try:
                    val = float(match.group(1).replace('.', ''))
                    if 1000 <= val <= 5000000: return val
                except: pass

    # 2. Procurar no texto completo do card (primeiro "R$" válido)
    match = re.search(r'R\$\s*([\d.]+)', texto)
    if match:
        try:
            val = float(match.group(1).replace('.', ''))
            if 1000 <= val <= 5000000: return val
        except: pass

    # 3. Procurar em atributos aria-label ou data-price
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
    """Tenta extrair o preço da página do anúncio (fallback)."""
    try:
        resp = scraper.get(url_anuncio, timeout=6)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # meta tag
            meta = soup.find('meta', itemprop='price') or soup.find('meta', property='product:price:amount')
            if meta and meta.get('content'):
                try: return float(meta['content'])
                except: pass
            # elementos com classe de preço
            for classe in ['price', 'preco', 'ad__price', 'actual-price', 'olx-text--heading-2']:
                elem = soup.find(['span', 'div', 'h2', 'h3'], class_=re.compile(classe, re.IGNORECASE))
                if elem:
                    match = re.search(r'R\$\s*([\d.]+)', elem.get_text(strip=True))
                    if match:
                        try:
                            val = float(match.group(1).replace('.', ''))
                            if 1000 <= val <= 5000000: return val
                        except: pass
            # textos com R$
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

def buscar_olx(marca, modelo, preco_max=999999, ano_min=1940, ano_max=2000, km_max=999999, uf='', pagina=1, max_detalhes=30):
    carros = []
    query = f'{marca} {modelo}'.strip()
    if not query: query = marca
    # REMOVIDO o parâmetro ps (preço) para evitar filtro invertido da OLX
    url = f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q={urllib.parse.quote(query)}&o={pagina}'
    if uf:
        url += f'&sf=1&state={uf}'
    
    print(f'🔍 Buscando: {url}')
    try:
        resp = scraper.get(url, timeout=20)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
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
                    
                    # Ano
                    ano = 0
                    ano_match = re.search(r'\b(19[4-9][0-9]|2000)\b', titulo)
                    if not ano_match:
                        ano_match = re.search(r'\b(19[4-9][0-9]|2000)\b', texto)
                    if ano_match: ano = int(ano_match.group(1))
                    
                    if ano > 0:
                        if ano < ano_min or ano > ano_max: continue
                    else:
                        termos_modernos = ['flex', '1.0', '1.4', '1.5', '1.6', '1.8', '2.0', '16v', 'vvt', 'multimídia', 'multimidia', 'digital', 'turbo', 'câmbio automático', 'automático', 'aut.', 'start-stop']
                        if any(termo in titulo.lower() for termo in termos_modernos): continue
                    
                    # Preço: tenta extrair do card (rápido)
                    preco = extrair_preco_card(parent, texto)
                    
                    # KM
                    km = 0
                    km_match = re.search(r'(\d{1,3}(?:\.\d{3})*)\s*km', texto, re.IGNORECASE)
                    if km_match: km = int(km_match.group(1).replace('.', ''))
                    
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
            
            # Para os que não tiveram preço no card, tenta a página individual (apenas max_detalhes)
            sem_preco = [c for c in carros if c['preco'] == 0]
            print(f'📋 {len(carros)} anúncios listados ({len(sem_preco)} sem preço no card). Extraindo detalhes...')
            for i, carro in enumerate(sem_preco[:max_detalhes]):
                print(f'   {i+1}/{min(len(sem_preco), max_detalhes)}: {carro["titulo"][:60]}...')
                carro['preco'] = extrair_preco_pagina(carro['url'])
            
            # Aplica filtro de preço máximo (apenas se preço > 0)
            carros = [c for c in carros if not (c['preco'] > 0 and c['preco'] > preco_max)]
            # Ordena: primeiro os com preço conhecido (menor para maior), depois os sem preço (preco=0)
            carros.sort(key=lambda x: (0 if x['preco'] > 0 else 1, x['preco']))
            print(f'✅ Final: {len(carros)} anúncios após filtro de preço máx R$ {preco_max}')
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
        .result { border: 1px solid #e0e0e0; padding: 15px; margin: 10px 0; border-radius: 8px; background: #fafafa; }
        .preco { color: #2e7d32; font-size: 1.3em; font-weight: bold; }
        .abaixo-fipe { background: #e8f5e9; color: #2e7d32; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }
        .detalhes { color: #888; font-size: 0.9em; }
        a { color: #1565c0; text-decoration: none; }
        .classic-badge { background: #8B4513; color: #FFD700; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 8px; }
        .no-price { color: #999; }
    </style>
</head>
<body>
    <div class="header"><h1>🏆 Rajadeira Clássicos</h1><p>Carros antigos de 1940 a 2000</p></div>
    <div class="card">
        <form method="GET" action="/buscar">
            <div class="form-row">
                <div class="form-group"><label>🏭 Marca / Modelo</label><input name="marca" value="{{ marca }}" placeholder="Ex: Fusca, Opala"></div>
                <div class="form-group"><label>🔍 Refinar modelo</label><input name="modelo" value="{{ modelo }}" placeholder="Ex: 1300, Diplomata"></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label>💰 Preço máximo (R$)</label><input type="number" name="preco_max" value="{{ preco_max }}"></div>
                <div class="form-group"><label>📍 UF</label><input name="uf" value="{{ uf }}" maxlength="2"></div>
                <div class="form-group"><label>🏁 KM máximo</label><input type="number" name="km_max" value="{{ km_max }}"></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label>📅 Ano inicial</label><input type="number" name="ano_min" value="{{ ano_min }}" min="1940" max="2000"></div>
                <div class="form-group"><label>📅 Ano final</label><input type="number" name="ano_max" value="{{ ano_max }}" min="1940" max="2000"></div>
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
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, marca='Fusca', modelo='', preco_max='100000', ano_min='1940', ano_max='2000', km_max='', uf='', cambio='', combustivel='', ordem='preco_asc', fipe=None, carros=[])

@app.route('/buscar')
def buscar():
    marca = request.args.get('marca', 'Fusca')
    modelo = request.args.get('modelo', '')
    preco_max = float(request.args.get('preco_max', 100000) or 100000)
    ano_min = int(request.args.get('ano_min', 1940) or 1940)
    ano_max = int(request.args.get('ano_max', 2000) or 2000)
    km_max = int(request.args.get('km_max', 999999) or 999999)
    uf = request.args.get('uf', '').upper()
    cambio = request.args.get('cambio', '')
    combustivel = request.args.get('combustivel', '')
    ordem = request.args.get('ordem', 'preco_asc')
    
    search_modelo = modelo if modelo else marca
    fipe = buscar_fipe(marca, search_modelo, 1980)
    carros = buscar_olx(marca, search_modelo, preco_max, ano_min, ano_max, km_max, uf, max_detalhes=25)
    
    if cambio: carros = [c for c in carros if c['cambio'].lower() == cambio.lower()]
    if combustivel: carros = [c for c in carros if c['combustivel'].lower() == combustivel.lower()]
    
    # Ordenação final (preco_asc já foi aplicada internamente, mas garantimos)
    if ordem == 'preco_asc': carros.sort(key=lambda x: (0 if x['preco'] > 0 else 1, x['preco']))
    elif ordem == 'preco_desc': carros.sort(key=lambda x: x['preco'] if x['preco'] > 0 else 0, reverse=True)
    elif ordem == 'ano_desc': carros.sort(key=lambda x: x['ano'], reverse=True)
    elif ordem == 'ano_asc': carros.sort(key=lambda x: x['ano'])
    
    return render_template_string(HTML,
        marca=marca, modelo=modelo,
        preco_max=str(int(preco_max)), ano_min=str(ano_min), ano_max=str(ano_max),
        km_max=str(km_max) if km_max < 999999 else '',
        uf=uf, cambio=cambio, combustivel=combustivel, ordem=ordem, fipe=fipe, carros=carros[:40]
    )

if __name__ == '__main__':
    print('='*50)
    print('🏆 RAJADEIRA CLÁSSICOS')
    print('🌐 http://localhost:5000')
    print('Preço máximo padrão: R$ 100.000')
    print('='*50)
    app.run(debug=False, host='0.0.0.0', port=5000)
