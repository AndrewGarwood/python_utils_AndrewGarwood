import os
from typing import List
import csv
import pandas as pd
from pandas import DataFrame


def validate_file_extension(file_path: str, ext: str) -> str:
    ext = ext if ext.startswith('.') else '.' + ext
    if not file_path.endswith(ext):
        file_path += ext
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'File not found: {file_path}')
    return file_path

def get_subdirectories(dir_path: str) -> List[str]:
    subdir_list: List[str] = [
        folder_name for folder_name in os.listdir(dir_path)\
            if os.path.isdir(os.path.join(dir_path, folder_name))
    ]
    return subdir_list

def recursively_get_files_of_type(
    dir: str,
    file_types: List[str] = ['pdf', 'docx', 'doc', 'xlsx', 'xls'],
    exclude_keywords: List[str] = ['waiver']
) -> List[str]:
    files_found: List[str] = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if (all(keyword not in file.lower() for keyword in exclude_keywords) 
                and file.rsplit('.', 1)[-1] in file_types
                ):
                files_found.append(os.path.join(root, file))
    return files_found

def tsv_to_csv(input_tsv_path: str, output_csv_path: str):
    input_tsv_path = validate_file_extension(input_tsv_path, '.tsv')
    output_csv_path = validate_file_extension(output_csv_path, '.csv')
    with open(input_tsv_path, 'r', newline='', encoding='utf-8') as tsv_file:
        tsv_reader = csv.reader(tsv_file, delimiter='\t')
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in tsv_reader:
                csv_writer.writerow(row)

def csv_to_tsv(input_csv_path: str, output_tsv_path: str):
    input_csv_path = validate_file_extension(input_csv_path, '.csv')
    output_tsv_path = validate_file_extension(output_tsv_path, '.tsv')
    with open(input_csv_path, 'r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        with open(output_tsv_path, 'w', newline='', encoding='utf-8') as tsv_file:
            tsv_writer = csv.writer(tsv_file, delimiter='\t')
            for row in csv_reader:
                tsv_writer.writerow(row)

def tsv_to_excel(input_tsv_path: str, output_excel_path: str):
    input_tsv_path = validate_file_extension(input_tsv_path, '.tsv')
    output_excel_path = validate_file_extension(output_excel_path, '.xlsx')
    df: DataFrame = pd.read_csv(input_tsv_path, delimiter='\t')
    df.to_excel(output_excel_path, index=False, freeze_panes=(1,0))

def excel_to_tsv(input_excel_path: str, output_tsv_path: str):
    input_excel_path = validate_file_extension(input_excel_path, '.xlsx')
    output_tsv_path = validate_file_extension(output_tsv_path, '.tsv')
    df: DataFrame = pd.read_excel(input_excel_path)
    df.to_csv(output_tsv_path, sep='\t', index=False)

def csv_to_excel(input_csv_path: str, output_excel_path: str):
    input_csv_path = validate_file_extension(input_csv_path, '.csv')
    output_excel_path = validate_file_extension(output_excel_path, '.xlsx')
    df: DataFrame = pd.read_csv(input_csv_path)
    df.to_excel(output_excel_path, index=False, freeze_panes=(1,0))

def excel_to_csv(input_excel_path: str, output_csv_path: str):
    input_excel_path = validate_file_extension(input_excel_path, '.xlsx')
    output_csv_path = validate_file_extension(output_csv_path, '.csv')
    df: DataFrame = pd.read_excel(input_excel_path)
    df.to_csv(output_csv_path, index=False)
    
