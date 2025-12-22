import schedule
import time
import datetime
import json

from uploadFile import upload_to_swarm
from oracle_tickbarrs import get_tickbarrs_yesterday2
from saveHashInDb import save_tickbarr_hash_to_db, save_failed_tickbarr


def up_tickbarr_to_swarm(stamp):
    #df = get_tickbarrs_yesterday().head(16)
    df = get_tickbarrs_yesterday2()
    print(df)
    print(df.columns)

    # Iterar sobre las filas del DataFrame
    # for index, row in df.iterrows():
    #     tickbarr = row['TTICKBARR']
    #     print("Procesando tickbarr:", tickbarr)
    #     num_box = row['TNUMECAJA']
    #     print("Número de caja:", num_box)
    #     code_esty_clie = row['TCODIESTICLIE']
    #     print("Código de esty clie:", code_esty_clie)
    #     code_etiq_clie = row['TCODIETIQCLIE']
    #     code_tall = row['TCODITALL']

#up_tickbarr_to_swarm("2e")

from get_tickbar_data import get_json_from_tickbarr  # Tu función que obtiene el JSON
json_data = get_json_from_tickbarr("091938005564")
data = json.loads(json_data)
print(data['tztotrazwebinfo'])