import requests
import json
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
BUCKET_NAME = os.getenv("BUCKET_NAME")

s3 = boto3.client("s3")

def descargar_todo(endpoint, nombre):
    print(f"📥 Descargando {nombre}...")
    registros = []
    skip = 0
    limit = 100

    while True:
        url = f"{BASE_URL}/{endpoint}/?skip={skip}&limit={limit}"
        res = requests.get(url)
        if res.status_code != 200:
            print(f"❌ Error HTTP: {res.text}")
            break
        data = res.json()
        if not data:
            print(f"✔ Fin de {nombre}")
            break
        registros.extend(data)
        print(f"✔ skip={skip}: {len(data)} registros")
        skip += limit

    print(f"📊 Total {nombre}: {len(registros)}")
    return registros

def subir_s3(registros, nombre_archivo, carpeta):
    file_path = f"/tmp/{nombre_archivo}"
    with open(file_path, "w") as f:
        for r in registros:
            f.write(json.dumps(r) + "\n")
    print(f"☁️ Subiendo {nombre_archivo} a S3...")
    s3.upload_file(file_path, BUCKET_NAME, f"{carpeta}/{nombre_archivo}")
    print(f"🚀 {nombre_archivo} subido correctamente")

# ===== PRODUCTOS =====
productos = descargar_todo("productos", "productos")
subir_s3(productos, "productos.json", "productos")

# ===== CATEGORIAS =====
categorias = descargar_todo("categorias", "categorias")
subir_s3(categorias, "categorias.json", "categorias")
