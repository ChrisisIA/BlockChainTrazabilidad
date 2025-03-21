import pandas as pd
import os
import pymysql

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

#Ahora falta ver como agrego contenido a mi db 
#Esta función no sirve solo es de referencia
def get_files():
    conn = connect_to_my_db()
    if conn:
        try:
            query = "SELECT * FROM prdorutaarch"
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.markdown(" Procesando.. ")
            return None


df = pd.read_excel('Tickbarrs.xlsx')


#for index, row in df.iterrows():
#    print(row['TTICKBARR'])

connection = connect_to_db()

contador = 100

for i in range(10):
    tickbarr = df.loc[i, 'TTICKBARR']
    print(tickbarr)
    contador += 1

# Mostrar las primeras filas del DataFrame
#print(df)