import os
import shutil
import glob
import pandas as pd
import sqlite3
from pathlib import Path
from langchain_community.utilities.sql_database import SQLDatabase

def remove_files(folder):
    shutil.rmtree(folder)
    os.makedirs(folder)

def database_creation(folder):

    for f in glob.glob(f'{folder}/*.xlsx'):
        xl = pd.ExcelFile(f)
        for sheet_name in xl.sheet_names:
            sheet = xl.parse(sheet_name)
            try:
                sheet.to_csv(f"{folder}/{sheet_name}.csv", index=False)
            except:
                pass

    files = glob.glob(f'{folder}/*.csv')
    if len(files) == 0:
        return None

    uri = f'{folder}/data_base.db'
    db = sqlite3.connect(uri)
    for f in files:
        data = pd.read_csv(f)
        data.to_sql(
            name=Path(f).stem,
            con=db,
            if_exists="replace",
            index=False
        )
        print(f"File {f} ingested into database")
        print(f"> Head {data.head(3)}")

    return SQLDatabase.from_uri(f"sqlite:///{Path(uri).as_posix()}")






