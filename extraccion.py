import requests
from bs4 import BeautifulSoup
import time
import numpy as np
import pandas as pd
import json
import os
import re




url_base = "https://www.autocasion.com"
url_actual = "/coches-ocasion"
pagina_actual = 1

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "es-ES,es;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "referer": "http://localhost:8888/",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

datos = []
urls_vistas = set()

while True:
    time.sleep(0.2)
    url = url_base + url_actual
    print(f"Extrayendo página {pagina_actual}: {url}")
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    anuncios = soup.find_all("a", href=True)
    encontrados = 0

    for anuncio in anuncios:
        titulo_tag = anuncio.find("h2", itemprop="name")
        if titulo_tag:
            titulo = titulo_tag.get_text(strip=True)
            url_anuncio = url_base + anuncio['href']
            if url_anuncio in urls_vistas:
                continue
            urls_vistas.add(url_anuncio)

            precio_contado_tag = anuncio.find("p", class_="precio")
            precio_contado = precio_contado_tag.get_text(strip=True) if precio_contado_tag else None

            precio_financiado_tag = anuncio.find("p", class_="precio financiado")
            precio_financiado = precio_financiado_tag.get_text(strip=True) if precio_financiado_tag else None

            ul = anuncio.find("ul")
            tags = [li.get_text(strip=True) for li in ul.find_all("li")] if ul else []

            datos.append({
                "titulo": titulo,
                "url": url_anuncio,
                "precio_contado": precio_contado,
                "precio_financiado": precio_financiado,
                "tags": tags
            })
            encontrados += 1

    if encontrados == 0:
        print("No quedan más anuncios. Terminando.")
        break

    siguiente_pagina_num = pagina_actual + 1
    siguiente = None
    for a in soup.find_all("a", href=True):
        href = a['href']
        if f"?page={siguiente_pagina_num}" in href:
            siguiente = href
            break

    if siguiente:
        url_actual = siguiente
        pagina_actual += 1
    else:
        print("No hay siguiente página. Finalizando.")
        break

print(f"Total anuncios extraídos: {len(datos)}")

with open("datos.json", "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=2)

for i in range(0, len(datos), 1000):
    bloque = datos[i:i+1000]
    for j, item in enumerate(bloque):
        idx = i + j
        print(f"Procesando ({idx+1}/{len(datos)}): {item['url']}")
        try:
            resp = requests.get(item["url"], headers=headers)
            soup = BeautifulSoup(resp.text, "html.parser")

            ul_ficha = soup.find("ul", class_="datos-basicos-ficha")
            item["detalles_ficha"] = [li.get_text(strip=True) for li in ul_ficha.find_all("li")] if ul_ficha else []

            time.sleep(0.2)
        except Exception as e:
            print(f"Error en {item['url']}: {e}")
            item["detalles_ficha"] = []

    with open(f"bloque_{i//1000 + 1}.json", "w", encoding="utf-8") as f:
        json.dump(bloque, f, ensure_ascii=False, indent=2)

archivos = [f for f in os.listdir() if re.match(r"bloque_\d+\.json", f)]
archivos.sort(key=lambda x: int(re.search(r"bloque_(\d+)", x).group(1)))

datos_completos = []
for archivo in archivos:
    with open(archivo, "r", encoding="utf-8") as f:
        datos_completos.extend(json.load(f))

urls = [item["url"] for item in datos_completos]
if len(urls) != len(set(urls)):
    print("¡Alerta! Hay URLs duplicadas.")
else:
    print("Verificación pasada: todas las URLs son únicas.")

df = pd.DataFrame(datos_completos)
df.to_csv("anuncios_unificados.csv", index=False, encoding="utf-8")
