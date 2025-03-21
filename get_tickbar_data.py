import os
import pandas as pd
import cx_Oracle
from dotenv import load_dotenv
import json

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")

db_config = {
    'user' : DB_USER,
    'password' : DB_PASSWORD,
    'dsn' : cx_Oracle.makedsn(DB_HOST, DB_PORT, DB_NAME)
}

list_temp_dfs = ["tztotrazwebinfo", "tztotrazwebalma", "tztotrazwebacab", "tztotrazwebacabmedi"]

def connect():
    connection = cx_Oracle.connect(user=db_config['user'], password=db_config['password'], dsn=db_config['dsn'])
    return connection

def get_df_temp(table, conn):
    try:
        query = f"SELECT * FROM {table}"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(e)
        return ""


def get_tickbar(tickbarr: str, idioma: str, sector: str):
    conn = connect()
    try:
        cursor = conn.cursor()
        p_menserro = cursor.var(cx_Oracle.STRING)
        cursor.callproc("tzprc_traztick", [tickbarr, idioma, sector, p_menserro])

        if p_menserro.getvalue():
            print(f"Error: {p_menserro.getvalue()}")
            return None
        else:
            dicc_df = {}
            for temp_names in list_temp_dfs:
                dicc_df[temp_names] = get_df_temp(temp_names, conn)
            
            return dicc_df
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

def convert_df_to_json(df):
    lista_dicc = df.to_dict(orient="records")  # Convierte todas las filas a una lista de diccionarios
    result_json = json.dumps(lista_dicc, indent=1, default=str)  # Serializa a JSON
    return result_json

def make_json_from_dfs(dicc_df):
    dicc_main = {}
    for temp_name in list_temp_dfs:
        json_value = convert_df_to_json(dicc_df[temp_name])
        dicc_main[temp_name] = json.loads(json_value)
    main_json = json.dumps(dicc_main, indent=1)
    return main_json

def save_json_to_file(json_data, filename="output.json"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json_data)  # Guarda el JSON en el archivo
    print(f"JSON guardado en {filename}")

def get_json_from_tickbarr(tickbarr: str):
    dicc_df = get_tickbar(tickbarr, "es", None)
    return make_json_from_dfs(dicc_df)


# tickbarrs por probar: 089853705010  -  088932801353

#dicc_df = get_tickbar("089853705010", "es", None)
#print(dicc_df)
#main_json = make_json_from_dfs(dicc_df)
#save_json_to_file(main_json, "segundo.json")
#print(main_json)


#info_json = convert_df_to_json(df1)
#print(info_json)