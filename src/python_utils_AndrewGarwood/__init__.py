import os
import sys
from typing import List, Dict, Set, Any,Tuple, Union, Callable, Optional, Literal
import re
import json

import pandas as pd
from pandas import DataFrame, Series, Index, Timestamp

from .config.env import ENABLE_DETAILED_LOG, ENABLE_OVERWRITE, set_enable_detailed_log, set_enable_overwrite, set_df_file_name

from .pd_utils import has_columns, impose_column_order, map_key_to_row_indices,\
    extract_permuted_key_rows, extract_duplicate_rows_from_key_map, extract_rows_with_empty_fields,\
    update_field, filter_by_text, filter_by_date_range, group_and_aggregate, \
    permuted_key_join, apply_update_dict

from .objects.FieldCondition import FieldCondition, FieldMap, field_contains, \
    field_equals, field_not_equals, field_startswith, field_endswith, field_is_empty

from .file import validate_file_extension, get_subdirectories, recursively_get_files_of_type,\
    map_key_to_file_paths, tsv_to_csv, csv_to_tsv, tsv_to_excel, excel_to_tsv, csv_to_excel, excel_to_csv

from .regex import ahead_is, ahead_not, behind_is, behind_not, \
    equivalent_alphanumeric, equivalent_alphanumeric_split_set, extract_leaf, extract_dimensions, \
    extract_unit_measurements, extract_city, extract_state, extract_zip, extract_phone, extract_name_from_address, \
    STATE_ABBREVIATIONS, STATE_NAMES, STREET_SUFFIX_PATTERN, street_suffix_list, suite_pattern, NAME_SUFFIX_PATTERN,\
    NUMBER_PATTERN, UNITS, DIMENSION_SYMBOL_PATTERN

from .io import print_group, concatenate_dataframes_to_excel, \
    concatenate_dataframes_to_excel_sheet, write_dataframes_to_excel, \
    read_file_lines_as_list, write_list_to_txt_file, write_list_to_json, write_dict_to_json
__all__ = [
    'os', 'sys', 're', 'json',
    
    'List', 'Dict', 'Set', 'Any', 'Tuple', 'Union', 'Callable', 'Optional', 'Literal',
    
    'pd', 'DataFrame', 'Series', 'Index', 'Timestamp',

    'ENABLE_DETAILED_LOG', 'ENABLE_OVERWRITE', 'set_enable_detailed_log', 'set_enable_overwrite', 'set_df_file_name',
    
    'has_columns', 'impose_column_order', 'map_key_to_row_indices', 'extract_permuted_key_rows', 'extract_duplicate_rows_from_key_map',
    'extract_rows_with_empty_fields', 'update_field', 'apply_update_dict',
    'filter_by_text', 'filter_by_date_range', 'group_and_aggregate', 'permuted_key_join',
    
    'FieldCondition', 'FieldMap', 'field_contains', 'field_equals', 'field_not_equals', 'field_startswith',
    'field_endswith', 'field_is_empty',
    
    'validate_file_extension', 'get_subdirectories', 'recursively_get_files_of_type', 'map_key_to_file_paths',
    'tsv_to_csv', 'csv_to_tsv', 'tsv_to_excel', 'excel_to_tsv', 'csv_to_excel', 'excel_to_csv',
    
    'ahead_is', 'ahead_not', 'behind_is', 'behind_not', 'equivalent_alphanumeric', 'equivalent_alphanumeric_split_set',
    'extract_leaf', 'extract_dimensions', 'extract_unit_measurements', 'extract_city', 'extract_state', 'extract_zip',
    'extract_phone', 'extract_name_from_address', 'STATE_ABBREVIATIONS', 'STATE_NAMES', 'STREET_SUFFIX_PATTERN',
    'street_suffix_list', 'suite_pattern', 'NAME_SUFFIX_PATTERN', 'NUMBER_PATTERN', 'UNITS', 'DIMENSION_SYMBOL_PATTERN',
    
    'print_group', 'concatenate_dataframes_to_excel', 'concatenate_dataframes_to_excel_sheet', 'write_dataframes_to_excel',
    'read_file_lines_as_list', 'write_list_to_txt_file', 'write_list_to_json', 'write_dict_to_json'
]