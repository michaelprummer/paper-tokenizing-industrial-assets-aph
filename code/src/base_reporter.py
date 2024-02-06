import pandas as pd
from glob import glob
from mconfig import config
import utils


def hash_size_from_file(file) -> int:
    return int(file.split("-")[1])


def _config(key: str):
    return config[key]


def get_table_data(df: pd.DataFrame):
    aph_norm = utils.sum_column_average(df, "norm")

    p_norm = utils.sum_column_average(df, "phash-n")

    #'APH', 'pHash'
    return [f"{aph_norm:.2%}", f"{p_norm:.2%}"]


def create_base_report(file_path: str):
    """
    Create single report
    """
    reports = []
    files = glob(file_path)

    if files.__len__() == 0:
        print("Error: No files found in path - ", file_path)
        return

    for file in files:
        df = pd.read_excel(file)
        hash_size = hash_size_from_file(file)
        na_data = get_table_data(df)

        reports.append([hash_size] + na_data)
    columns = ['hash_size', 'APH', 'pHash']

    df = pd.DataFrame(reports, columns=columns)

    print(df.to_latex(escape=True, index=False, column_format="cccccc"))


out = config.get('reports_output')
create_base_report(f"{out}/hash-*-versions-output.xlsx")
