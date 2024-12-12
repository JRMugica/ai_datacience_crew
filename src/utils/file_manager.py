import os
import glob
import pandas as pd
from src.utils.prepare_environment import read_config

config = read_config()
UPLOAD_FOLDER = os.path.join(os.getcwd(), config['parameters']['UPLOAD_FOLDER'])

def clean_input_files(config):
    if os.path.exists(UPLOAD_FOLDER):
        for f in glob.glob(f'{UPLOAD_FOLDER}/*'):
            os.remove(f)
    else:
         os.makedirs(UPLOAD_FOLDER)

def excel_to_csv(config):

    for f in glob.glob(f'{UPLOAD_FOLDER}/*.xlsx'):
        xl = pd.ExcelFile(f)
        for sheet_name in xl.sheet_names:
            sheet = xl.parse(sheet_name)
            try:
                sheet.to_csv(f"{UPLOAD_FOLDER}/{sheet_name}.csv", index=False)
            except:
                pass






