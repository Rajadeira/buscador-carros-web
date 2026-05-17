from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
from scrapers.webmotors import WebMotorsScraper
from scrapers.mercado_livre import MercadoLivreScraper
from scrapers.olx import OLXScraper
from scrapers.icarros import iCarrosScraper
from scrapers.kavak import KavakScraper

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>🚗 Buscador Rajadeira - 5 Sites</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body class="bg-light">
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-8 mx-auto">
                <div class="card shadow-lg">
                    <div class="card-header bg-primary text-white">
                        <h3>🚗 Buscador Rajadeira</h3>
                        <p class="mb-0">Busca em 5 sites simultaneamente!</p>
                    </div>
                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-6">
                                <label>🏭 Marca</label>
                                <input class="form-control" id="marca" value="Honda" placeholder="Ex: Honda, Toyota, VW">
                            </div>
                            <div class="col-6">
                                <label>🚙 Modelo</label>
                                <input class="form-control" id="modelo" value="Civic" placeholder="Ex: Civic, Corolla, Golf">
                            </div>
                        </div>
                        
                        <div class="row mb-3">
                            <div class="col-6">
                                <label>💰 Preço Máximo</label>
                                <input type="number" class="form-control" id="preco_max" value="200000">
                            </div>
                            <div class="col-6">
                                <label>📅 Ano Mínimo</label>
                                <input type="number" class="form-control" id="ano_min" value="2015">
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label>🌐 Sites para buscar:</label>
                            <div class="row">
                                <div class="col-4"><input type="checkbox" id="site_webmotors" checked> WebMotors</div>
                                <div class="col-4"><input type="checkbox" id="site_ml" checked> Mercado Livre</div>
                                <div class="col-4"><input type="checkbox" id="site_olx" checked> OLX</div>
                                <div class="col-4"><input type="checkbox" id="site_icarros" checked> iCarros</div>
                                <div class="col-4"><input type="checkbox" id="site_kavak" checked> Kavak</div>
                            </div>
                        </div>
                        
                        <button class="btn btn-primary btn-lg w-100" onclick="buscar()">
                            🔍 Buscar em Todos os Sites
                        </button>
                        
                        <div id="loading" class="mt-3 text-center d-none">
                            <div class="spinner-border text-primary"></div>
                            <p id="status-text">Buscando anúncios...</p>
                        </div>
                        
                        <div id="resultados" class="mt-3"></div>
                    </div>
                </div>
                <div class="text-center mt-3 text-muted">
                    <small>WebMotors | Mercado Livre | OLX | iCarros | Kavak</small>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    async function buscar() {
        document.getElementById('loading').classList.remove('d-none');
        document.getElementById('resultados').innerHTML = '';
        document.getElementById('status-text').textContent = 'Buscando em 5 sites...';
        
        const params = new URLSearchParams();
        params.append('marca', document.getElementById('marca').value);
        params.append('modelo', document.getElementById('modelo').value);
        params.append('preco_max', document.getElementById('preco_max').value);
        params.append('ano_min', document.getElementById('ano_min').value);
        
        // Verificar sites selecionados
        const sites = [];
        if (document.getElementById('site_webmotors').checked) sites.push('webmotors');
        if (document.getElementById('site_ml').checked) sites.push('mercado_livre');
        if (document.getElementById('site_olx').checked) sites.push('olx');
        if (document.getElementById('site_icarros').checked) sites.push('icarros');
        if (document.getElementById('site_kavak').checked) sites.push('kavak');
        
        params.append('sites', sites.join(','));
        
        try {
            const response = await fetch('/buscar_agora?' + params.toString());
            const data = await response.json();
            
            document.getElementById('loading').classList.add('d-none');
            
            if (data.erro) {
                document.getElementById('resultados').innerHTML = '<div class="alert alert-danger">' + data.erro + '</div>';
                return;
            }
            
            let html = '<div class="alert alert-success"><strong>' + data.total + ' carros encontrados!</strong></div>';
            
            // Agrupar por fonte
            const fontes = {};
            data.carros.forEach(c => {
                if (!fontes[c.fonte]) fontes[c.fonte] = [];
                fontes[c.fonte].push(c);
            });
            
            for (const [fonte, carros] of Object.entries(fontes)) {
                html += '<h5 class="mt-3">📍 ' + fonte + ' (' + carros.length + ' carros)</h5>';
                carros.forEach(c => {
                    html += '<div class="card mb-2 border-' + getCorFonte(fonte) + '">';
                    html += '<div class="card-body py-2">';
                    html += '<div class="row">';
                    html += '<div class="col-8"><strong>' + c.titulo + '</strong><br>';
                    html += '<small>Ano: ' + c.ano + '</small></div>';
                    html += '<div class="col-4 text-end"><span class="badge bg-success">R$ ' + c.preco.toLocaleString('pt-BR') + '</span></div>';
                    html += '</div></div></div>';
                });
            }
            
            document.getElementById('resultados').innerHTML = html;
            
        } catch (error) {
            document.getElementById('loading').classList.add('d-none');
            document.getElementById('resultados').innerHTML = '<div class="alert alert-danger">Erro: ' + error.message + '</div>';
        }
    }
    
    function getCorFonte(fonte) {
        const cores = {
            'WebMotors': 'primary',
            'Mercado Livre': 'warning',
            'OLX': 'success',
            'iCarros': 'info',
            'Kavak': 'danger'
        };
        return cores[fonte] || 'secondary';
    }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/buscar_agora')
def buscar_agora():
    marca = request.args.get('marca', 'Honda')
    modelo = request.args.get('modelo', 'Civic')
    preco_max = float(request.args.get('preco_max', 200000))
    ano_min = int(request.args.get('ano_min', 2015))
    sites_param = request.args.get('sites', '')
    
    sites_ativos = sites_param.split(',') if sites_param else ['webmotors', 'mercado_livre', 'olx', 'icarros', 'kavak']
    
    scrapers = {
        'webmotors': WebMotorsScraper(delay=1.0),
        'mercado_livre': MercadoLivreScraper(delay=1.0),
        'olx': OLXScraper(delay=1.0),
        'icarros': iCarrosScraper(delay=1.0),
        'kavak': KavakScraper(delay=1.0)
    }
    
    todos_carros = []
    
    for site_nome in sites_ativos:
        if site_nome in scrapers:
            try:
                scraper = scrapers[site_nome]
                carros = scraper.pesquisar(
                    marca=marca,
                    modelo=modelo,
                    preco_max=preco_max,
                    ano_min=ano_min
                )
                # Filtrar por preço máximo
                carros_filtrados = [c for c in carros if c.preco <= preco_max]
                todos_carros.extend(carros_filtrados)
            except Exception as e:
                print(f"Erro no {site_nome}: {e}")
    
    resultado = {
        'total': len(todos_carros),
        'carros': [
            {
                'titulo': c.titulo,
                'preco': c.preco,
                'ano': c.ano,
                'fonte': c.fonte
            }
            for c in todos_carros
        ]
    }
    
    return jsonify(resultado)

if __name__ == '__main__':
    print('='*60)
    print('🚗 BUSCADOR RAJADEIRA - 5 SITES')
    print('🌐 http://localhost:5000')
    print('📱 WebMotors | Mercado Livre | OLX | iCarros | Kavak')
    print('='*60)
    app.run(debug=False, host='0.0.0.0', port=5000)
