import os
import glob
import pandas as pd
import sqlite3
from pathlib import Path
from src.utils.prepare_environment import read_config

config = read_config()
UPLOAD_FOLDER = os.path.join(os.getcwd(), config['parameters']['UPLOAD_FOLDER'])

def remove_files(folder):
    if os.path.exists(folder):
        for f in glob.glob(f'{folder}/*'):
            os.remove(f)
    else:
         os.makedirs(folder)

def database_creation(UPLOAD_FOLDER):

    for f in glob.glob(f'{UPLOAD_FOLDER}/*.xlsx'):
        xl = pd.ExcelFile(f)
        for sheet_name in xl.sheet_names:
            sheet = xl.parse(sheet_name)
            try:
                sheet.to_csv(f"{UPLOAD_FOLDER}/{sheet_name}.csv", index=False)
            except:
                pass

    files = glob.glob(f'{UPLOAD_FOLDER}/*.csv')
    if len(files) == 0:
        return False

    uri = f'{UPLOAD_FOLDER}/data_base.db'
    db = sqlite3.connect(uri)
    for f in files:
        data = pd.read_csv(f)
        data.to_sql(
            name=Path(f).stem,
            con=db,
            if_exists="replace",
            index=False
        )
    return True






