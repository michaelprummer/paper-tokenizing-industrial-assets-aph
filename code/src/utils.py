from numpy import median, absolute
import decimal
import pandas as pd
import distance
from glob import glob
import os
import zipfile
from pathlib import Path
from math import floor
ctx = decimal.Context()
ctx.prec = 3


def count_valid_rows(table: pd.DataFrame, valid_filter) -> float:
    valid = 0

    for _, row in table.iterrows():
        is_valid = bool(row.__getitem__(valid_filter))

        if is_valid:
            # print("VALID:", row.__getitem__("name_a"))
            valid += 1

    return valid if valid <= 0 else valid/table.__len__()


def sum_column_average(table: pd.DataFrame, col_name: str) -> float:
    if table.__len__() == 0:
        return 0
    return sum(table.__getitem__(col_name))/table.__len__()

def to_percent(val, digits=2):
    val *= 10 ** (digits + 2)
    return '{1:.{0}f}%'.format(digits, floor(val) / 10 ** digits)

def get_phash_distance(hashA: str, hashB: str):
    """
    Passing the bit length of the phash which is different from the str length
    to calculate the normalized hamming distance.
    """
    # bit_len = phash_size**2
    str_len = hashA.__len__()

    hamming = distance.hamming(hashA, hashB)
    normalized = 1.0 - (hamming / str_len)

    return (hamming, normalized)


def float_to_str(f):
    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')


def median_absolute_deviation(data, axis=None):
    return median(absolute(data - median(data, axis)), axis)


def add_tex_mid_rules(latex: str, indices: list[int], line_offset: int) -> str:
    """
    Adds a horizontal `index` lines before the last line of the table

    Args:
        latex: latex table
        index: index of horizontal line insertion (in lines)
    """
    lines = latex.splitlines()
    for idx in indices:
        lines.insert(idx + line_offset, r'\midrule')
    return '\n'.join(lines).replace('NaN', '')


def text_to_file(data, write_path: str):
    with open(write_path, 'w') as f:
        f.write(data)

def create_dir(p: str):
    if not os.path.exists(p):
        os.makedirs(p)


def delete_folder(path: str):
    paths = glob(path, recursive=True)
    for folder in paths:
        delete_files(f"{folder}*")
        os.rmdir(folder)


def delete_files(folder: str):
    files = glob(f"{folder}*")
    for file in files:
        os.unlink(file)


def str_byte_len(string: str):
    return len(string.encode('utf-8'))


def extract_zip_files(directory, output: str):
    p = Path(directory)
    for f in p.glob('*.zip'):
        with zipfile.ZipFile(f, 'r') as archive:
            archive.extractall(path=output)
            print(
                f"Extracted contents from '{f.name}' to '{f.stem}' directory.")
