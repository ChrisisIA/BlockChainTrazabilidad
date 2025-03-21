import subprocess
import os

# Configura el hash de Swarm y la ruta de salida
swarm_hash = "2cb6f77d952f17831af3b89da89bb9c7ba9b7f16083fafe324247636ac7d4be8"
output_dir = "/home/nettalco/Documents/blockchain/descargas_swarm"
file_name = "prueba2.json"

# Crear la carpeta de descargas si no existe
os.makedirs(output_dir, exist_ok=True)

# Comando para descargar el archivo con swarm-cli
command = f"swarm-cli download {swarm_hash} {output_dir}"

try:
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    print(f"✅ Archivo descargado exitosamente en: {os.path.join(output_dir, file_name)}")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"❌ Error al descargar el archivo: {e.stderr}")
