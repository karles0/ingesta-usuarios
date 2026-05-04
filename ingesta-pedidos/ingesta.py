import requests
import json
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

BASE_URL_MS1 = os.getenv("BASE_URL_MS1")
BASE_URL_MS2 = os.getenv("BASE_URL_MS2")
EMAIL       = os.getenv("EMAIL")
PASSWORD    = os.getenv("PASSWORD")
BUCKET_NAME = os.getenv("BUCKET_NAME")

s3 = boto3.client("s3")

# ========= LOGIN (MS1) =========
print("🔐 Login...")
login_res = requests.post(f"{BASE_URL_MS1}/usuarios/login", json={
    "email": EMAIL,
    "password": PASSWORD
})
if login_res.status_code != 200:
    print("❌ Login falló:", login_res.text)
    exit(1)
token = login_res.json().get("token")
if not token:
    print("❌ No se obtuvo token:", login_res.text)
    exit(1)
headers = {"Authorization": f"Bearer {token}"}
print("✅ Token OK")

# ========= DESCARGA PEDIDOS =========
def descargar_paginado(endpoint, nombre):
    print(f"📥 Descargando {nombre}...")
    registros = []
    page = 1
    limit = 100

    while True:
        url = f"{BASE_URL_MS2}/{endpoint}?page={page}&limit={limit}"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"❌ Error HTTP página {page}:", res.text)
            break
        json_res = res.json()
        # El response es un mapa genérico, busca la lista
        data = None
        if isinstance(json_res, list):
            data = json_res
        elif isinstance(json_res, dict):
            for key in ["data", "content", "pedidos", "items"]:
                if key in json_res and isinstance(json_res[key], list):
                    data = json_res[key]
                    break
        if not data:
            print(f"✔ Fin de {nombre}")
            break
        registros.extend(data)
        print(f"✔ Página {page}: {len(data)} registros")
        if len(data) < limit:
            break
        page += 1

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

pedidos = descargar_paginado("pedidos", "pedidos")
subir_s3(pedidos, "pedidos.json", "pedidos")
