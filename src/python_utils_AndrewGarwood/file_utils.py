import os
from typing import List, Dict, Literal
import csv
import pandas as pd
from pandas import DataFrame

__all__ = [
    'validate_file_extension', 'get_subdirectories', 'map_key_to_file_paths', 'recursively_get_files_of_type',
    'tsv_to_csv', 'csv_to_tsv', 'tsv_to_excel', 'excel_to_tsv', 'csv_to_excel', 'excel_to_csv'
]

def validate_file_extension(file_path: str, ext: str) -> str:
    """
    Ensure file_path has the desired extension
    
    Args:
        file_path (str):
        ext (str): desired file extension

    Raises:
        FileNotFoundError:

    Returns:
        str: file_path with desired extension
    """
    ext = ext if ext.startswith('.') else '.' + ext
    if not file_path.endswith(ext):
        file_path += ext
    if  not os.path.isfile(file_path) and not os.path.isdir(os.path.dirname(file_path)):
        raise FileNotFoundError(f'File not found or invalid path: {file_path}')
    return file_path

def get_subdirectories(dir: str) -> List[str]:
    """_summary_
    Given directory path, return list of first level subdirectories
    
    Args:
        dir (str): directory/folder containing subdirectories

    Returns:
        List[str]: list of first level subdirectories
    """
    subdir_list: List[str] = [
        folder_name for folder_name in os.listdir(dir)\
            if os.path.isdir(os.path.join(dir, folder_name))
    ]
    return subdir_list

def map_key_to_file_paths(
    file_paths: List[str],
    dir_delimiter: Literal['/', '\\'] = '\\',
    key_delimiter: str = ' '
) -> Dict[str, List[str]]:
    """_summary_
    Assumes file naming convention in which expected key is first element in file_name.split(key_delimiter).
    Replaces underscore with key_delimiter.
    
    Originally used with recursively_get_files_of_type(...) to map SKUs to Quality Control files so that 
    I could quickly open them in another script without having to search for a specific SKU's file either manually or with os.walk().
    
    Args:
        file_paths (List[str]): _description_
        dir_delimiter (Literal['/', '\\'], optional): _description_. Defaults to '\\'.
        key_delimiter (str, optional): _description_. Defaults to ' '.

    Returns:
        Dict[str, List[str]]: _description_
    """
    key_to_file_path_map: Dict[str, List[str]] = {}
    for file_path in file_paths:
        file_name: str = file_path.replace('_', key_delimiter).rsplit(dir_delimiter, 1)[-1]
        key: str = file_name.split(key_delimiter)[0]
        if key in key_to_file_path_map.keys():
            key_to_file_path_map[key].append(file_path)
        else:
            key_to_file_path_map[key] = [file_path]
    return key_to_file_path_map

def recursively_get_files_of_type(
    dir: str,
    file_types: List[str] = ['pdf', 'docx', 'doc', 'xlsx', 'xls'],
    exclude_keywords: List[str] = ['waiver']
) -> List[str]:
    """_summary_

    Args:
        dir (str): _description_
        file_types (List[str], optional): _description_. Defaults to ['pdf', 'docx', 'doc', 'xlsx', 'xls'].
        exclude_keywords (List[str], optional): _description_. Defaults to ['waiver'].

    Returns:
        List[str]: _description_
    """
    files_found: List[str] = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if ((not exclude_keywords or all(keyword not in file.lower() for keyword in exclude_keywords))
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
    
