import boto3
import json
from pymongo import MongoClient
import os

# Configuración MongoDB
mongoUri    = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
nombreBD    = "shopcloud"
coleccion   = "usuarios"

# Configuración S3
nombreBucket = os.environ.get("S3_BUCKET", "shopcloud-ingesta")
ficheroLocal = "usuarios.json"
s3Key        = "raw/usuarios/usuarios.json"

# 1. Conectar a MongoDB y leer TODOS los registros (estrategia Pull)
print("Conectando a MongoDB...")
client = MongoClient(mongoUri)
db     = client[nombreBD]
docs   = list(db[coleccion].find({}, {"password": 0}))
print(f"Registros leídos: {len(docs)}")

# 2. Convertir ObjectId a string
for doc in docs:
    doc["_id"]       = str(doc["_id"])
    doc["createdAt"] = str(doc.get("createdAt", ""))
    doc["updatedAt"] = str(doc.get("updatedAt", ""))

client.close()

# 3. Guardar en archivo local
with open(ficheroLocal, "w", encoding="utf-8") as f:
    json.dump(docs, f, ensure_ascii=False, indent=2)
print(f"Archivo generado: {ficheroLocal}")

# 4. Subir a S3
print("Subiendo a S3...")
s3 = boto3.client("s3")
s3.upload_file(ficheroLocal, nombreBucket, s3Key)
print(f"Subido a s3://{nombreBucket}/{s3Key}")
print("Ingesta completada")
