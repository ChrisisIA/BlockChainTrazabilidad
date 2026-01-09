import schedule
import time
import datetime

from uploadFile import upload_to_swarm
from oracle_tickbarrs import get_tickbarrs_yesterday
from saveHashInDb import save_tickbarr_hash_to_db, save_failed_tickbarr


def up_tickbarr_to_swarm(stamp):
    #df = get_tickbarrs_yesterday().head(16)
    df = get_tickbarrs_yesterday()
    print(df)

    # Iterar sobre las filas del DataFrame
    for index, row in df.iterrows():
        tickbarr = row['TTICKBARR']
        print("Procesando tickbarr:", tickbarr)
        num_box = row['TNUMECAJA']
        print("Número de caja:", num_box)
        code_esty_clie = row['TCODIESTICLIE']
        print("Código de esty clie:", code_esty_clie)
        code_etiq_clie = row['TCODIETIQCLIE']
        code_tall = row['TCODITALL']

        try:
            data_columns, hash = upload_to_swarm(tickbarr, stamp)
            save_tickbarr_hash_to_db(tickbarr, data_columns['caja'], code_esty_clie, code_etiq_clie, data_columns['talla'], hash, data_columns['cod_cliente'], data_columns['cliente'], data_columns['tipo_prenda'], data_columns['edad'], data_columns['genero'], data_columns['destino'], data_columns['tipo_tejido'])
            print(f"✓ Tickbarr {tickbarr} procesado exitosamente")
        except Exception as e:
            # Si falla, guardar el error y continuar con el siguiente
            save_failed_tickbarr(tickbarr, str(e))
            print(f"✗ Error en tickbarr {tickbarr}, continuando con el siguiente...")

def run_program_at_scheduled_time(stamp, scheduled_time="05:00"):
    schedule.every().day.at(scheduled_time).do(up_tickbarr_to_swarm, stamp=stamp)
    print(f"Programa programado para ejecutarse diariamente a las {scheduled_time}.")
    while True:
        try:
            schedule.run_pending()
            print("Esperando la siguiente ejecución programada...", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep(59)  # Esperar un minuto antes de verificar nuevamente
        except KeyboardInterrupt:
            print("\nPrograma terminada por el usuario")
            break

run_program_at_scheduled_time("51179dfdae435f60e8b1a127cd7364ef560a6873d04ad2830e24630bff815d2e", "09:57")