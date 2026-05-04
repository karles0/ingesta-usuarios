import requests
import json
import time
import subprocess
import os
from dotenv import load_dotenv

# cargar variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
BUCKET_NAME = os.getenv("BUCKET_NAME")
FILE_NAME = "usuarios.json"

# LOGIN
login = requests.post(f"{BASE_URL}/usuarios/login", json={
    "email": EMAIL,
    "password": PASSWORD
})

token = login.json()["token"]

headers = {
    "Authorization": f"Bearer {token}"
}

usuarios = []
page = 1
limit = 100

while True:
    res = requests.get(f"{BASE_URL}/usuarios?page={page}&limit={limit}", headers=headers)
    data = res.json()["data"]

    if not data:
        break

    usuarios.extend(data)
    print(f"Página {page}")

    page += 1
    time.sleep(0.2)

with open(FILE_NAME, "w") as f:
    json.dump(usuarios, f)

print("Archivo generado")

# subir a S3
subprocess.run(f"aws s3 cp {FILE_NAME} s3://{BUCKET_NAME}/", shell=True)
