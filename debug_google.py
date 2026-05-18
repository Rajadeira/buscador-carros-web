import requests
import urllib.parse

marca = 'Honda'
modelo = 'Civic'
query = f'{marca} {modelo} 2020 site:olx.com.br'
url = f'https://www.google.com/search?q={urllib.parse.quote(query)}&num=10&hl=pt-BR'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'pt-BR,pt;q=0.9'
}

print(f'🔍 URL: {url}')
resp = requests.get(url, headers=headers, timeout=15)
print(f'Status: {resp.status_code}')
print(f'Content-Type: {resp.headers.get("Content-Type")}')
print(f'Tamanho: {len(resp.text)} caracteres')

# Salvar HTML para análise
with open('google_debug.html', 'w', encoding='utf-8') as f:
    f.write(resp.text)
print('✅ HTML salvo em google_debug.html')

# Verificar se contém 'olx.com.br'
if 'olx.com.br' in resp.text:
    print('✅ O HTML contém "olx.com.br"')
else:
    print('❌ O HTML NÃO contém "olx.com.br"')

# Mostrar trecho inicial
print('\n--- PRIMEIROS 500 CARACTERES ---')
print(resp.text[:500])
