import pandas as pd
import os
import pymysql
import warnings
from dotenv import load_dotenv

from uploadFile import upload_to_swarm
from oracle_tickbarrs import get_tickbarrs_yesterday

# Cargar las variables de entorno
load_dotenv()

DB_USER = os.getenv("DB_PRENDAS_USER")
warnings.filterwarnings('ignore')

DB_PASSWORD = os.getenv("DB_PRENDAS_PASSWORD")
DB_HOST = os.getenv("DB_PRENDAS_HOST")
DB_PORT = int(os.getenv("DB_PRENDAS_PORT"))
DB_NAME = os.getenv("DB_PRENDAS_NAME")

db_config = {
    'host': DB_HOST,
    'port': DB_PORT,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

def connect_to_my_db():
    try:
        conn = pymysql.connect(**db_config)
        return conn
    except Exception as e:
        print("falló al conectarse a la base de datos de MariaDB")
        return None

def save_tickbarr_hash_to_db(tickbarr, hash):
    conn = connect_to_my_db()
    if conn:
        try:
            query = "INSERT INTO apdobloctrazhash (TTICKBARR, TTICKHASH) VALUES (%s, %s)"
            with conn.cursor() as cursor:
                cursor.execute(query, (tickbarr, hash))
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)

def up_tickbarr_to_swarm(stamp):
    df = get_tickbarrs_yesterday().head(16)
    print(df)
    for tickbarr in df['TTICKBARR']:
        hash = upload_to_swarm(tickbarr, stamp)
        save_tickbarr_hash_to_db(tickbarr, hash)

# df = pd.read_excel('Tickbarrs_small.xlsx')


# for i in range(len(df)):
#     tickbarr = '0' + str(df.loc[i, 'TTICKBARR'])
#     print("tickbarr:", tickbarr)
#     hash = upload_to_swarm(tickbarr, "742bfeab75365749b4a909f1bc384a06ae98a8cb9e9d2850aa4c3209bbdd4a0e")
#     save_tickbarr_hash_to_db(tickbarr, hash)
#     print(tickbarr, " : ", hash)

# Mostrar las primeras filas del DataFrame
#print(df)

up_tickbarr_to_swarm("742bfeab75365749b4a909f1bc384a06ae98a8cb9e9d2850aa4c3209bbdd4a0e")