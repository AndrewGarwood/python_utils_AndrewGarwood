import os
import sys
from typing import List, Dict, Set, Any,Tuple, Union, Callable, Optional, Literal
import re
import json

import pandas as pd
from pandas import DataFrame, Series, Index, Timestamp

from .config import ENABLE_DETAILED_LOG, ENABLE_OVERWRITE

from .pd_utils import has_columns, impose_column_order, map_key_to_row_indices,\
    extract_permuted_key_rows, extract_duplicate_rows_from_key_map, extract_rows_with_empty_fields,\
    update_field, field_contains, field_equals, field_not_equals, field_startswith,\
    filter_by_text, filter_by_date_range, group_and_aggregate, permuted_key_join

from .objects.FieldCondition import FieldCondition, FieldMap

from .file_utils import validate_file_extension, get_subdirectories, recursively_get_files_of_type,\
    map_key_to_file_paths, tsv_to_csv, csv_to_tsv, tsv_to_excel, excel_to_tsv, csv_to_excel, excel_to_csv

from .regex_utils import ahead_is, ahead_not, behind_is, behind_not, \
    equivalent_alphanumeric, equivalent_alphanumeric_split_set, extract_leaf, extract_dimensions, \
    extract_unit_measurements, extract_city, extract_state, extract_zip, extract_phone, extract_name_from_address, \
    STATE_ABBREVIATIONS, STATE_NAMES, street_suffix_pattern, street_suffix_list, suite_pattern, name_suffixes,\
    number_pattern, units, dimension_symbol_pattern

from .write_utils import print_group, concatenate_dataframes_to_excel, concatenate_dataframes_to_excel_sheet, write_dataframes_to_excel

__all__ = [
    'os', 'sys', 're', 'json',
    
    'List', 'Dict', 'Set', 'Any', 'Tuple', 'Union', 'Callable', 'Optional', 'Literal',
    
    'pd', 'DataFrame', 'Series', 'Index', 'Timestamp',

    'ENABLE_DETAILED_LOG', 'ENABLE_OVERWRITE',
    
    'has_columns', 'impose_column_order', 'map_key_to_row_indices', 'extract_permuted_key_rows', 'extract_duplicate_rows_from_key_map',
    'extract_rows_with_empty_fields', 'update_field', 'field_contains', 'field_equals', 'field_not_equals', 'field_startswith',
    'filter_by_text', 'filter_by_date_range', 'group_and_aggregate', 'permuted_key_join',
    
    'FieldCondition', 'FieldMap',
    
    'validate_file_extension', 'get_subdirectories', 'recursively_get_files_of_type', 'map_key_to_file_paths',
    'tsv_to_csv', 'csv_to_tsv', 'tsv_to_excel', 'excel_to_tsv', 'csv_to_excel', 'excel_to_csv',
    
    'ahead_is', 'ahead_not', 'behind_is', 'behind_not', 'equivalent_alphanumeric', 'equivalent_alphanumeric_split_set',
    'extract_leaf', 'extract_dimensions', 'extract_unit_measurements', 'extract_city', 'extract_state', 'extract_zip',
    'extract_phone', 'extract_name_from_address', 'STATE_ABBREVIATIONS', 'STATE_NAMES', 'street_suffix_pattern',
    'street_suffix_list', 'suite_pattern', 'name_suffixes', 'number_pattern', 'units', 'dimension_symbol_pattern',
    
    'print_group', 'concatenate_dataframes_to_excel', 'concatenate_dataframes_to_excel_sheet', 'write_dataframes_to_excel'
]