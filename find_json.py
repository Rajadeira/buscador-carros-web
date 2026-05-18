from bs4 import BeautifulSoup

with open('pagina_fusca.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')

print(f'🔍 {len(scripts)} scripts encontrados')
for i, script in enumerate(scripts):
    if script.string and ('thumbnail' in script.string or 'adList' in script.string):
        print(f'\n✅ Script {i} contém "thumbnail" ou "adList":')
        # Mostrar apenas a parte inicial e final para não sobrecarregar
        texto = script.string
        # Encontrar a posição de thumbnail
        pos = texto.find('thumbnail')
        if pos > 0:
            print(f'   Trecho ao redor de "thumbnail":')
            print(texto[max(0, pos-200):pos+300])
        pos = texto.find('adList')
        if pos > 0:
            print(f'\n   Trecho ao redor de "adList":')
            print(texto[max(0, pos-200):pos+300])
        break
else:
    print('❌ Nenhum script contém "thumbnail" ou "adList"')
