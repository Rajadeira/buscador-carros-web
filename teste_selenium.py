from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

print("🔧 Iniciando Chrome...")

options = Options()
options.add_argument('--headless')  # Rodar sem abrir janela
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    url = "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?q=Honda%20Civic&ps=100000&sf=1&state=CE"
    
    print(f"🔍 Acessando: {url}")
    driver.get(url)
    time.sleep(5)  # Aguardar carregar
    
    # Rolar a página
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    
    # Pegar todos os links da página
    links = driver.find_elements(By.TAG_NAME, 'a')
    
    anuncios = []
    for link in links:
        try:
            href = link.get_attribute('href')
            if href and ('anuncio' in href.lower() or 'item' in href.lower()):
                texto = link.text.strip()
                if texto and len(texto) > 10:
                    anuncios.append({'url': href, 'texto': texto[:100]})
        except:
            pass
    
    print(f"\n✅ Encontrados: {len(anuncios)} links de anúncios")
    for i, a in enumerate(anuncios[:10]):
        print(f"\n#{i+1}: {a['texto'][:80]}")
        print(f"   🔗 {a['url'][:120]}")
    
    driver.quit()
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
