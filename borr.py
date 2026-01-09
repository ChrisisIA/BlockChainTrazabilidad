
from google import genai

# Especificar la API Key directamente
client = genai.Client(api_key="AIzaSyA87DCtZfHg5w38vpTzoV94KJtZ7c29OCE")  # ← Pega tu clave aquí

response = client.models.generate_content(
    model="gemini-2.5-flash", 
    contents="dime un chiste sobre programacion"
)

print(response.text)
