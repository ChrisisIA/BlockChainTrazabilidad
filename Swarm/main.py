import schedule
import time
import datetime

from uploadFile import upload_to_swarm
from oracle_tickbarrs import get_tickbarrs_yesterday
from saveHashInDb import save_tickbarr_hash_to_db, save_failed_tickbarr


def up_tickbarr_to_swarm(stamp):
    #df = get_tickbarrs_yesterday().head(16)
    df = get_tickbarrs_yesterday().head()
    print(df)
    for tickbarr in df['TTICKBARR']:
        try:
            hash = upload_to_swarm(tickbarr, stamp)
            save_tickbarr_hash_to_db(tickbarr, hash)
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
            time.sleep(60)  # Esperar un minuto antes de verificar nuevamente
        except KeyboardInterrupt:
            print("\nPrograma terminada por el usuario")
            break

#run_program_at_scheduled_time("5d89c57cd80484dffb91deb89e16f7012d46d8267488732f7da5a11550990d89", "05:00")
up_tickbarr_to_swarm("5d89c57cd80484dffb91deb89e16f7012d46d8267488732f7da5a11550990d89")