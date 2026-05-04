import requests
import json
import os
import boto3

# 🔧 VARIABLES DE ENTORNO
BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
BUCKET_NAME = os.getenv("BUCKET_NAME")

FILE_NAME = "usuarios.json"

# 🔐 LOGIN
print("🔐 Login...")

login = requests.post(f"{BASE_URL}/usuarios/login", json={
    "email": EMAIL,
    "password": PASSWORD
})

print("STATUS:", login.status_code)
print("RESPONSE:", login.text)

if login.status_code != 200:
    print("❌ Login falló")
    exit()

token = login.json().get("token")

if not token:
    print("❌ No se recibió token")
    exit()

print("✅ Token OK")

headers = {
    "Authorization": f"Bearer {token}"
}

# 📥 DESCARGAR USUARIOS (PAGINADO)
print("📥 Descargando usuarios...")

usuarios = []
page = 1

while True:
    url = f"{BASE_URL}/usuarios?page={page}"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print("❌ Error en request:", res.text)
        break

    data = res.json()

    # Ajuste flexible según API
    users = data.get("data") if isinstance(data, dict) else data

    if not users:
        break

    usuarios.extend(users)
    print(f"✔ Página {page}: {len(users)} registros")

    page += 1

print(f"📊 Total usuarios: {len(usuarios)}")

# 💾 GUARDAR JSON EN FORMATO CORRECTO (ARRAY)
print("💾 Guardando JSON...")

with open(FILE_NAME, "w") as f:
    json.dump(usuarios, f, indent=2)

print("✅ Archivo JSON listo")

# ☁️ SUBIR A S3
print("☁️ Subiendo a S3...")

try:
    s3 = boto3.client("s3")

    s3.upload_file(
        FILE_NAME,
        BUCKET_NAME,
        f"usuarios/{FILE_NAME}"
    )

    print("🚀 Subido a S3 correctamente")

except Exception as e:
    print("❌ Error subiendo a S3:", str(e))
