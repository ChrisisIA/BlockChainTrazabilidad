import json
import math

def filtrar_json(json_data, campos_por_clave):
    
    resultado = {}
    
    for clave_principal, campos_a_conservar in campos_por_clave.items():
        if clave_principal in json_data and json_data[clave_principal]:
            datos_filtrados = []
            for i in range(len(json_data[clave_principal])):
                filtrar = {}  
                for campo in campos_a_conservar:
                    if campo in json_data[clave_principal][i]:
                        valor = json_data[clave_principal][i][campo]
                        if valor is not None and valor != "NaT" and not (isinstance(valor, float) and math.isnan(valor)):
                            filtrar[campo] = valor
                datos_filtrados.append(filtrar)

            resultado[clave_principal] = datos_filtrados
    
    return resultado

# Abrir el archivo JSON y cargarlo en una variable
with open('segundo.json', 'r', encoding='utf-8') as file:
    datos_json = json.load(file)

with open('relevant_data.json', 'r', encoding='utf-8') as file:
    relevant_json = json.load(file)



json_final = filtrar_json(datos_json, relevant_json)
print(json_final)