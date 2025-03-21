import requests
import json
from get_tickbar_data import get_json_from_tickbarr  # Tu función que obtiene el JSON

# Configuración
bee_api_url = "http://localhost:1633"  # URL de tu nodo Bee
batch_id = "8776e76fb223fefd4fbcf8d08dbafb3583010736261b213aed42236d7d1466f4"  # Tu lote de postage

# Obtener el JSON desde la función
json_data = get_json_from_tickbarr("088932801353")  # Esta función debe devolver un diccionario en Python

# Convertir el JSON a string para enviarlo
#json_string = json.dumps(json_data)

# Subir el JSON a Swarm
response = requests.post(
    f"{bee_api_url}/bzz",
    headers={
        "swarm-postage-batch-id": batch_id,
        "Content-Type": "application/json"  # Asegura que se visualice en el navegador
    },
    data=json_data  # Pasamos directamente el JSON como string
)

# Verificar la respuesta
try:
    response_data = response.json()
    swarm_hash = response_data["reference"]
    print("JSON subido correctamente.")
    print("Hash Swarm:", swarm_hash)
    print("Accede a tu JSON en: https://api.gateway.ethswarm.org/bzz/" + swarm_hash)
except requests.exceptions.JSONDecodeError:
    print("Error: la respuesta no contiene JSON válido. Respuesta completa:", response.text)
