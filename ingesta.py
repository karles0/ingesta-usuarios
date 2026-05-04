import requests
import json
import time
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
BUCKET_NAME = os.getenv("BUCKET_NAME")
FILE_NAME = "usuarios.json"

# ========= LOGIN =========
print("🔐 Login...")

login_res = requests.post(f"{BASE_URL}/usuarios/login", json={
    "email": EMAIL,
    "password": PASSWORD
})

if login_res.status_code != 200:
    print("❌ Login falló:", login_res.text)
    raise SystemExit(1)

token = login_res.json().get("token")
if not token:
    print("❌ No se obtuvo token:", login_res.text)
    raise SystemExit(1)

headers = {"Authorization": f"Bearer {token}"}
print("✅ Token OK")

# ========= DESCARGA =========
usuarios = []
page = 1
limit = 100

print("📥 Descargando usuarios...")

while True:
    url = f"{BASE_URL}/usuarios?page={page}&limit={limit}"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print(f"❌ Error HTTP página {page}:", res.text)
        break

    json_res = res.json()

    if "data" not in json_res:
        print("❌ Respuesta sin 'data':", json_res)
        break

    data = json_res["data"]

    if not data:
        print("✔ Fin de páginas")
        break

    usuarios.extend(data)
    print(f"✔ Página {page} ({len(data)})")

    page += 1
    time.sleep(0.2)

print(f"📊 Total: {len(usuarios)}")

# ========= GUARDAR =========
with open(FILE_NAME, "w") as f:
    json.dump(usuarios, f)

print("💾 JSON guardado")

# ========= S3 (boto3) =========
print("☁️ Subiendo a S3...")

s3 = boto3.client("s3")

try:
    s3.upload_file(
        FILE_NAME,
        BUCKET_NAME,
        f"usuarios/{FILE_NAME}"
    )
    print("🚀 Subido a S3 correctamente")
except Exception as e:
    print("❌ Error subiendo a S3:", e)
    raise
