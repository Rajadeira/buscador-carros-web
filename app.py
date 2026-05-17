from flask import Flask, render_template, request, jsonify
from datetime import datetime
import threading
import sys
import os

sys.path.append(os.path.dirname(__file__))

from scrapers.webmotors import WebMotorsScraper
from scrapers.mercado_livre import MercadoLivreScraper
from scrapers.olx import OLXScraper

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rajadeira-buscador-carros-2024'

buscas_ativas = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar():
    data = request.json
    
    busca_id = datetime.now().strftime('%Y%m%d%H%M%S')
    buscas_ativas[busca_id] = {
        'status': 'executando',
        'resultados': [],
        'termo': f"{data.get('marca', '')} {data.get('modelo', '')}"
    }
    
    thread = threading.Thread(target=executar_busca, args=(busca_id, data))
    thread.start()
    
    return jsonify({'status': 'success', 'busca_id': busca_id})

@app.route('/status/<busca_id>')
def status(busca_id):
    if busca_id in buscas_ativas:
        busca = buscas_ativas[busca_id]
        return jsonify({
            'status': busca['status'],
            'total': len(busca['resultados'])
        })
    return jsonify({'status': 'erro', 'mensagem': 'Busca não encontrada'})

@app.route('/resultados/<busca_id>')
def resultados(busca_id):
    if busca_id in buscas_ativas:
        busca = buscas_ativas[busca_id]
        return render_template('resultados.html', 
                             busca=busca, 
                             busca_id=busca_id)
    return "Busca não encontrada", 404

def executar_busca(busca_id, params):
    scrapers = {
        'webmotors': WebMotorsScraper(),
        'mercado_livre': MercadoLivreScraper(),
        'olx': OLXScraper()
    }
    
    todos_resultados = []
    sites_ativos = params.get('sites', ['webmotors', 'mercado_livre', 'olx'])
    
    for site in sites_ativos:
        if site in scrapers:
            try:
                resultados = scrapers[site].pesquisar(
                    marca=params.get('marca', ''),
                    modelo=params.get('modelo', ''),
                    preco_min=float(params.get('preco_min', 0)),
                    preco_max=float(params.get('preco_max', 999999)),
                    ano_min=int(params.get('ano_min', 0)),
                    ano_max=int(params.get('ano_max', 2024))
                )
                todos_resultados.extend(resultados)
            except Exception as e:
                print(f"Erro no {site}: {e}")
    
    buscas_ativas[busca_id]['resultados'] = todos_resultados
    buscas_ativas[busca_id]['status'] = 'concluido'

if __name__ == '__main__':
    print("=" * 50)
    print("🚗 Buscador de Carros - Rajadeira")
    print("🌐 Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
