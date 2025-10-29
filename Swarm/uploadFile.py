import requests
from get_tickbar_data import get_json_from_tickbarr  # Tu función que obtiene el JSON

def upload_to_swarm(tickbarr: str, batch_stamp: str):
    # Configuración
    bee_api_url = "http://localhost:1633"  # URL de tu nodo Bee
    batch_id = batch_stamp  # Tu lote de postage

    # Obtener el JSON desde la función
    json_data = get_json_from_tickbarr(tickbarr)  # Esta función debe devolver un diccionario en Python

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
        print("Subido Correctamente.")
        print("Tickbarr:", tickbarr)
        print("Hash Swarm:", swarm_hash)
        return swarm_hash
    except requests.exceptions.JSONDecodeError:
        print("Error: la respuesta no contiene JSON válido. Respuesta completa:", response.text)

#swarm_hash = upload_to_swarm("089744701145", "742bfeab75365749b4a909f1bc384a06ae98a8cb9e9d2850aa4c3209bbdd4a0e")
