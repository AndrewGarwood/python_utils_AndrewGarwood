from typing import List, Dict, Set, Any, Tuple, Union, Callable, Optional, Literal
import warnings
from datetime import datetime
import pandas as pd
from pandas import DataFrame, Series, Index
from .regex_utils import extract_leaf
from .write_utils import print_group, DEFAULT_LOG, FIELD_UPDATE_LOG

from objects.FieldCondition import FieldCondition, FieldMap

# TODO: make better usage of df.apply() and other Pandas functions 

def has_columns(
    df: DataFrame, 
    cols_to_check: List[str] | str
) -> bool:
    """
    Args:
        df (DataFrame): _description_
        cols_to_check (List[str] | str): 

    Returns:
        bool: True if all cols_to_check are in df.columns else False
    """
    if isinstance(cols_to_check, str):
        cols_to_check = [cols_to_check]
    return all(col in df.columns for col in cols_to_check)

def impose_column_order(
    df: DataFrame, 
    column_order: List[str],
    from_start: bool = True,
    from_end: bool = False
) -> DataFrame:
    """
    Args:
        df (DataFrame): _description_
        column_order (List[str]): subset of df.columns or a permutation of df.columns
        from_start (bool, optional): if column_order is subset of df.columns, put column_order at the start. Defaults to True.
        from_end (bool, optional): if column_order is subset of df.columns, put column_order at the end. Defaults to False.

    Raises:
        ValueError: if column_order contains invalid column name(s)

    Returns:
        DataFrame: df with columns in specified column_order
    """
    if not has_columns(df, column_order):
        raise ValueError('Invalid Column Name(s)')
    remaining_columns = [col for col in df.columns if col not in column_order]
    result_order = column_order + remaining_columns if from_start else \
        remaining_columns + column_order if from_end else column_order
    return df[result_order]
def map_key_to_row_indices(
    df: DataFrame, 
    key_col: str | int = 'Item Name/Number',
    truncate: bool = False,
    delimiter: str = ':'
) -> Dict[str, List[int]]:
    """
    Originally used in context of mapping item export from QuickBooks
    
    Args:
        df (DataFrame): input DataFrame
        key_col (str | int, optional): values in key_col will be keys of Return Dict. 
            Defaults to 'Item Name/Number'.
        truncate (bool, optional): if values in key_col have leading characters/terms 
            that can be isolated by a delimiter using extract_leaf(key). 
            For QuickBooks, it's' the ':' character. 
            Defaults to False.

    Raises:
        ValueError: if key_col is not in df.columns

    Returns:
        Dict[str, List[int]]: map of keys to list of row indices; 
        multiplicity = len(Dict[key])
    """
    if not has_columns(df, key_col):
        raise ValueError('Invalid Key Column')
    key_to_row_indices: Dict[str, List[int]] = {}  
    for i, row in df.iterrows():
        key: str = str(row[key_col]) \
            if not truncate else extract_leaf(str(row[key_col]), delimiter)
        if key in key_to_row_indices:
            key_to_row_indices[key].append(i)
        else:
            key_to_row_indices[key] = [i]
    return key_to_row_indices

def extract_duplicate_rows_from_key_map(
    df: DataFrame, 
    key_to_row_indices: Dict[str, List[int]]
) -> DataFrame:
    df.insert(loc=1, column='Original Index', value=df.index)
    duplicate_row_indices: List[int] = [
        i for indices in key_to_row_indices.values() \
        if len(indices) > 1 for i in indices
    ]
    duplicates_df: DataFrame = df.iloc[duplicate_row_indices]  # return DataFrame of the duplicate rows
    return duplicates_df

def extract_permuted_key_rows(
    df: DataFrame,
    permuted_key_col: str = 'Item'
) -> DataFrame:
    """
    Used to identify duplicate item SKUs in QuickBooks Item Export
    Example: key1 and key2 are permutations of the same item SKU, 14-500 
        key1=Marketing Supply:MARKETING MATERIALS:14-500
        key2=PACKAGING:14-500
    
    Args:
        df (DataFrame): _description_
        permuted_key_col (str, optional): _description_. Defaults to 'Item'.

    Raises:
        ValueError: _description_

    Returns:
        DataFrame: _description_
    """
    if not has_columns(df, permuted_key_col):
        raise ValueError('Invalid Key Column')
    key_map: Dict[str, List[int]] = map_key_to_row_indices(
        df=df, 
        key_col=permuted_key_col, 
        truncate=True
    )
    duplicates_df: DataFrame = extract_duplicate_rows_from_key_map(df, key_map)
    return duplicates_df


def custom_join(
    base_df: DataFrame, 
    permuted_df: DataFrame, 
    base_key_col: str = 'Item Name/Number',
    base_name_col: str = 'Display Name',
    premuted_key_col: str = 'Item',
    premuted_name_col: str = 'Description',
    cols_to_add: List[str] = ['Account', 'Asset Account', 'COGS Account'],
    enable_overwrite: bool = False,
    enable_detailed_log: bool = True
) -> DataFrame:
    """_summary_
    Originally used in context of adding account fields to a tsv of 2 cols [Item Name/Number, Display Name]
    Args:
        base_df (DataFrame): _description_
        permuted_df (DataFrame): _description_
        base_key_col (str, optional): _description_. Defaults to 'Item Name/Number'.
        base_name_col (str, optional): _description_. Defaults to 'Display Name'.
        premuted_key_col (str, optional): _description_. Defaults to 'Item'.
        premuted_name_col (str, optional): _description_. Defaults to 'Description'.
        cols_to_add (List[str], optional): _description_. Defaults to ['Account', 'Asset Account', 'COGS Account'].
        enable_overwrite (bool, optional): _description_. Defaults to False.
        enable_detailed_log (bool, optional): _description_. Defaults to True.

    Returns:
        DataFrame: _description_
    """
    
    if (not has_columns(base_df, base_key_col) 
        or not has_columns(permuted_df, [premuted_key_col]+cols_to_add)
        ):
        return ValueError('Invalid Key Column(s)')
    for col in cols_to_add:
        if not has_columns(base_df, col):
            base_df[col] = ''
    update_dict: Dict[Tuple, str] = {}
    processed_keys: Set[str] = set()
    num_updated, num_duplicates, num_unmatched_keys = 0, 0, 0
    base_key_map: Dict[str, List[int]] = map_key_to_row_indices(base_df, base_key_col)
    permuted_key_map: Dict[str, List[int]] = map_key_to_row_indices(permuted_df, premuted_key_col)
    for permuted_key in permuted_key_map.keys():
        permuted_index: int = permuted_key_map[permuted_key][0]
        leaf_key: str = extract_leaf(permuted_key)
        is_unique_key_in_base: bool = (leaf_key in base_key_map.keys()
            and len(base_key_map[leaf_key]) == 1
            and leaf_key not in processed_keys
            )
        if is_unique_key_in_base:
            base_index: int = base_key_map[leaf_key][0]
            for col in cols_to_add:
                base_val: str = str(base_df.at[base_index, col])
                ext_val: str = str(permuted_df.at[permuted_index, col])
                if ((ext_val and base_val != ext_val) 
                    and (enable_overwrite or not base_val)):
                    if enable_detailed_log:
                        print_group(
                            label=f'Value Update',
                            data=[
                                f'    base_df: row={base_index}, SKU={leaf_key}, Name={base_df.at[base_index, base_name_col]}',
                                f'extended_df: row={permuted_index}, SKU={permuted_key}, Name={permuted_df.at[permuted_index, premuted_name_col]}',  
                                f'\tOld {col}: {base_val}',
                                f'\tNew {col}: {ext_val}',
                            ],
                            print_to_console=False
                        )
                    # base_df.at[base_index, col] = ext_val
                    update_dict[(base_index, col)] = ext_val
                    num_updated += 1  
            processed_keys.add(leaf_key)  
        elif leaf_key in base_key_map.keys() and leaf_key in processed_keys:
            num_duplicates += 1
            base_index: int = base_key_map[leaf_key][0]
            if enable_detailed_log:
                print_group(
                    label='Duplicate Found',
                    data=[
                        f'\t Truncated SKU: {leaf_key}', 
                        f'\tTruncated Name: {base_df.loc[base_index, base_name_col]}',
                        f'\t  Extended SKU: {permuted_key}',
                        f'\t Extended Name: {permuted_df.loc[permuted_index, premuted_name_col]}',
                    ],
                    print_to_console=False
                )
        elif leaf_key not in base_key_map.keys():
            num_unmatched_keys += 1
            if enable_detailed_log:
                print_group(
                    label='Key Not Found',
                    data=[
                        f'Truncated: ',
                        f'\tKey:  {leaf_key}', 
                        f'Extended:',  
                        f'\tKey:  {permuted_key}',
                        f'\tName: {permuted_df.loc[permuted_index, premuted_name_col]}',
                    ],
                    print_to_console=False
                )
    for (index, col), val in update_dict.items():
        base_df.at[index, col] = val
    print(
        f'Number of Updates:        {num_updated}\n'
        f'Number of Duplicates:     {num_duplicates}\n'
        f'Number of Unmatched Keys: {num_unmatched_keys}'
    )
    return base_df

def extract_rows_with_empty_fields(
    df: DataFrame,
    fields: List[str],
    key_col: str = 'Item Name/Number',
    enable_detailed_log: bool = False
) -> DataFrame:
    if not has_columns(df, [key_col]+fields):
        return ValueError('Invalid Column Name')
    empty_rows: List[int] = []
    for i, row in df.iterrows():
        empty_fields: List[str] = \
            [str(row[field]) for field in fields if not row[field]]
        if empty_fields:
            empty_rows.append(i)
            if enable_detailed_log:
                print_group(
                    label=f'Empty Field(s) Found: {len(empty_fields)}',
                    data=[
                        f'Row: {i}',
                        f'Key: {row[key_col]}',
                        f'Empty Field(s): {empty_fields}'
                    ],
                    print_to_console=False, log_path=DEFAULT_LOG
                )
    return df.loc[empty_rows]

def update_field(
    df: DataFrame,
    update_field: str,
    update_val: str,
    conditions: List[FieldCondition],
    key_col: str = 'Item Name/Number',
    name_col: str = 'Display Name',
    enable_overwrite: bool = False,
    enable_detailed_log: bool = True,
    df_file_name: str = 'inventory_item.tsv',
) -> DataFrame:
    """
    modular update of field in a DataFrame based on conditions
    
    Args:
        df (DataFrame): DataFrame to update
        update_field (str): column in df to update
        update_val (str): if all conditions are met, update row[update_field] to update_val for row in df
        conditions (List[FieldCondition]): specify condition functions and FieldMap inputs to be met for update
        enable_overwrite (bool, optional): overwrite rows that meet conditions already have value in update_field. 
            Defaults to False.
        enable_detailed_log (bool, optional): if want to write record of updates made to .output/field_update_log.txt. 
            Defaults to True.
        df_file_name (str, optional): Provide a file name for logging purposes. 
            Defaults to 'inventory_item.tsv'.

    Returns:
        DataFrame: updated df
    
    Example:
        df = update_field(
            df=df,
            update_field='Class', 
            update_val='Parent Class : Child Class',
            conditions=[
                FieldCondition(
                    condition_fn=field_contains, 
                    fn_criteria=FieldMap(
                        field='Display Name', 
                        value='Child Class Keyword'
                        )
                    )
                ], 
                enable_overwrite=True,
                df_file_name='inventory_item.tsv'
            )
    """
    cols_to_check: List[str] = \
        [crit.field for c in conditions for crit in c.fn_criteria]\
        +[update_field]+[key_col, name_col]
    if not has_columns(df, cols_to_check):
        return ValueError('Invalid Column(s)')
    update_dict: Dict[Tuple[str, str], Set[int]] = {}
    for i, row in df.iterrows():
        for c in conditions:
            if c.check_row(row):
                update_dict[(update_field, update_val)] = \
                    update_dict.get((update_field, update_val), set())
                if enable_overwrite or not row[update_field]:
                    update_dict[(update_field, update_val)].add(i)
    for (field, val), indices in update_dict.items():
        indices = list(indices)
        if enable_detailed_log:
            print_group(
                label=f'({df_file_name}) Updating {field} to {val}: count={len(indices)}', 
                data=[
                    f'row={j}, sku={df.at[j, key_col]}, name={df.at[j, name_col]}'
                    for j in indices
                    ],
                print_to_console=False, 
                log_path=FIELD_UPDATE_LOG
                )
        df.loc[indices, field] = val
    return df



def field_equals(
    row: Series, 
    ignore_case: bool, 
    target_field: str, 
    *target: str
) -> bool:
    target: Tuple[str] = tuple(t for sublist in target for t in (sublist if isinstance(sublist, tuple) else (sublist,)))  # temporary solution. if target is a 2D tuple, make it a 1D tuple
    field_val: str = str(row[target_field]) if target_field in row.index else ''
    if ignore_case:
        field_val = field_val.lower()
        target = [t.lower() for t in target]
    return any([t == field_val for t in target]) \
        if target and field_val else False

def field_not_equals(
    row: Series, 
    ignore_case: bool, 
    target_field: str, 
    *target: str
) -> bool:
    return not field_equals(row, ignore_case, target_field, *target)

def field_startswith(
    row: Series, 
    ignore_case: bool, 
    target_field: str, 
    *target: str
) -> bool:
    target: Tuple[str] = tuple(t for sublist in target for t in (sublist if isinstance(sublist, tuple) else (sublist,)))  # temporary solution. if target is a 2D tuple, make it a 1D tuple
    field_val: str = str(row[target_field]) if target_field in row.index else ''
    if ignore_case:
        field_val = field_val.lower()
        target = [p.lower() for p in target]
    return field_val.startswith(target) \
        if target and field_val else False

def field_contains(
    row: Series, 
    ignore_case: bool, 
    target_field: str, 
    *target: str
) -> bool:
    target: Tuple[str] = tuple(t for sublist in target for t in (sublist if isinstance(sublist, tuple) else (sublist,)))  # temporary solution. if target is a 2D tuple, make it a 1D tuple
    field_val: str = str(row[target_field]) if target_field in row.index else ''
    if ignore_case:
        field_val = field_val.lower()
        target = [t.lower() for t in target]
    return any([t in field_val for t in target]) \
        if target and field_val else False

def filter_by_text(
    df: DataFrame, 
    keep: Dict[str, List[str]]={}, 
    discard: Dict[str, List[str]]={}
) -> DataFrame:
    """
    Filter a DataFrame by whether text is contained in specified columns.
    Case-sensitive. 
    Discard takes precedence over keep due to order of operations.
    
    Args:
        df (DataFrame): DataFrame with columns containing keys of keep and discard
        keep (Dict[str, List[str]], optional): keep rows if column_key_str contains any of List[str]. Defaults to {}.
        discard (Dict[str, List[str]], optional): discard rows if column_key_str contains any of List[str]. Defaults to {}.
    
    Returns:
        DataFrame: filtered DataFrame
    """
    warnings.filterwarnings('ignore')
    if not has_columns(df, list(keep.keys()) + list(discard.keys())): 
        raise ValueError('Invalid Column Name(s) in keep or discard params')
    for col_name, filter_values in keep.items():
        pattern = '|'.join(filter_values)
        df = df[df[col_name].str.contains(
            pat=pattern, case=False, na=False, regex=True)]
    for col_name, filter_values in discard.items():
        pattern = '|'.join(filter_values)
        df = df[~df[col_name].str.contains(
            pat=pattern, case=False, na=False, regex=True)]
    warnings.filterwarnings('default')
    return df

def filter_by_date_range(
    df: DataFrame, 
    date_col: str, 
    start_date: str, 
    end_date: str
) -> DataFrame:
    """
    Includes start_date and end_date in the range
    Args:
        df (DataFrame): _description_
        date_col (str): filter by date range on this column
        start_date (str): format: 'mm/dd/yyyy'
        end_date (str): format: 'mm/dd/yyyy'

    Raises:
        ValueError: _description_

    Returns:
        DataFrame: _description_
    """
    if not has_columns(df, date_col):
        raise ValueError('Invalid Column Name')
    
    try:
        start_date = datetime.strptime(start_date, '%m/%d/%Y')
        end_date = datetime.strptime(end_date, '%m/%d/%Y')
    except Exception as e:
        raise ValueError("Date format should be mm/dd/yyyy", e)
    return df[(df[date_col] >= start_date) & (df[date_col] <= end_date)]

def aggregate_by_column(
    df: DataFrame,
    key_col: str,
    add_group_bys: List[str]=[],
    agg_dict: Dict[str, Literal['sum', 'mean', 'count']]={'Amount': 'sum', 'Qty': 'sum'}
) -> DataFrame:
    if not has_columns(df, [key_col]+add_group_bys+list(agg_dict.keys())):
        raise ValueError('Invalid Column Name(s)')
    aggregated_df: DataFrame = df.groupby([key_col]+add_group_bys).agg(
        agg_dict
    ).reset_index()
    return aggregated_df