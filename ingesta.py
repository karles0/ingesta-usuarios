import requests
import json
import os
import boto3

BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
BUCKET_NAME = os.getenv("BUCKET_NAME")

FILE_NAME = "usuarios.json"

# 🔐 LOGIN
print("🔐 Login...")
login = requests.post(f"{BASE_URL}/auth/login", json={
    "email": EMAIL,
    "password": PASSWORD
})

print("LOGIN STATUS:", login.status_code)
print("LOGIN RESPONSE:", login.text)

if login.status_code != 200:
    print("❌ Login falló:", login.text)
    exit()

token = login.json().get("token")
print("✅ Token OK")

headers = {
    "Authorization": f"Bearer {token}"
}

# 📥 DESCARGAR USUARIOS
print("📥 Descargando usuarios...")

usuarios = []
page = 1

while True:
    res = requests.get(f"{BASE_URL}/usuarios?page={page}", headers=headers)

    if res.status_code != 200:
        print("❌ Error obteniendo datos:", res.text)
        break

    data = res.json()
    users = data.get("data") or data

    if not users:
        break

    usuarios.extend(users)
    print(f"✔ Página {page} - {len(users)} registros")

    page += 1

print(f"📊 Total usuarios: {len(usuarios)}")

# 💾 GUARDAR JSON
print("💾 Guardando JSON...")

with open(FILE_NAME, "w") as f:
    json.dump(usuarios, f, indent=2)

print("✅ Archivo JSON listo")

# ☁️ SUBIR A S3
print("☁️ Subiendo a S3...")

s3 = boto3.client("s3")

s3.upload_file(
    FILE_NAME,
    BUCKET_NAME,
    f"usuarios/{FILE_NAME}"
)

print("🚀 Subido a S3 correctamente")
