import pandas as pd
import os
import pymysql
from dotenv import load_dotenv

from uploadFile import upload_to_swarm

# Cargar las variables de entorno
load_dotenv()

DB_USER = os.getenv("DB_PRENDAS_USER")
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

def add_tickbarr_hash(tickbarr, hash):
    conn = connect_to_my_db()
    if conn:
        try:
            query = "INSERT INTO prdotrazhash (TTICKBARR, TTICKHASH, TLINKHASH) VALUES (%s, %s, %s)"
            link = "https://api.gateway.ethswarm.org/bzz/"+hash
            with conn.cursor() as cursor:
                cursor.execute(query, (tickbarr, hash, link))
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)

#Ahora falta ver como agrego contenido a mi db 
#Esta función no sirve solo es de referencia
# def get_files():
#     conn = connect_to_my_db()
#     if conn:
#         try:
#             query = "SELECT * FROM prdorutaarch"
#             df = pd.read_sql(query, conn)
#             conn.close()
#             return df
#         except Exception as e:
#             st.markdown(" Procesando.. ")
#             return None

# tickbarr = "088932801353"
# hash = upload_to_swarm(tickbarr, "fe0766b58a144b7f03ea84fab75b6e0037f05ecd1d7397a7380a20ea26000447")
# add_tickbarr_hash(tickbarr, hash)

df = pd.read_excel('Tickbarrs.xlsx')


#for index, row in df.iterrows():
#    print(row['TTICKBARR'])

for i in range(len(df)):
    tickbarr = '0' + str(df.loc[i, 'TTICKBARR'])
    hash = upload_to_swarm(tickbarr, "fe0766b58a144b7f03ea84fab75b6e0037f05ecd1d7397a7380a20ea26000447")
    add_tickbarr_hash(tickbarr, hash)
    print(tickbarr, " : ", hash)
    #print(tickbarr)

# Mostrar las primeras filas del DataFrame
#print(df)