from dataclasses import dataclass
from typing import Callable, List, Tuple, Dict
from pandas import Series

__all__ = [
    'FieldMap', 'FieldCondition', 'field_equals', 'field_not_equals', 'field_startswith',
    'field_endswith', 'field_contains', 'field_is_empty'
]


@dataclass
class FieldMap:
    """
    FieldMap is a dataclass that represents a field (i.e. column) 
    and its value(s) to be used in a FieldCondition
    
    Args:
        field (str): The name of the field (i.e. column) in the DataFrame.
        value (Tuple[str] | List[str] | str): The value(s) to be checked against the field.
        ignore_case (bool): Default False
    """
    field: str
    value: Tuple[str] | List[str] | str = ''
    ignore_case: bool = False
    
    def __post_init__(self):
        if isinstance(self.value, str):
            self.value = (self.value,)
        elif isinstance(self.value, list):
            self.value = tuple(self.value)

@dataclass
class FieldCondition:
    """
    FieldCondition is a dataclass that represents a condition to be used in
    the update_field function. It requires a condition function, a list of
    FieldMap objects, and a boolean indicating whether all or any of the
    criteria must be met.
    
    Args:
        condition_fn (Callable[..., bool]):
        fn_criteria (List[FieldMap]):
        all\\_ (bool): Default True, if True all criteria must be met
        any\\_ (bool): Default False
        none (bool): Default False
    """
    condition_fn: Callable[..., bool]
    fn_criteria: List[FieldMap]
    all_: bool = True
    any_: bool = False
    none: bool = False
    
    def __post_init__(self):
        if not self.fn_criteria:
            raise ValueError('FieldCondition requires at least one criteria')
        if not self.condition_fn:
            raise ValueError('FieldCondition requires a condition function')
        if self.all_ and self.any_:
            raise ValueError('FieldCondition cannot require all and any criteria')
        if self.all_ and self.none:
            raise ValueError('FieldCondition cannot require all and none criteria')
        if self.any_ and self.none:
            raise ValueError('FieldCondition cannot require any and none criteria')
        
        if isinstance(self.fn_criteria, FieldMap):
            self.fn_criteria = [self.fn_criteria]

    def check_row(self, row: Series) -> bool:
        """
        Check if the record meets the criteria
        specified in the FieldCondition condition_fn and fn_criteria
        """
        if self.all_:
            return all([
                self.condition_fn(row, c.ignore_case, c.field, c.value) 
                for c in self.fn_criteria
                ])
        elif self.any_:
            return any([
                self.condition_fn(row, c.ignore_case, c.field, c.value) 
                for c in self.fn_criteria
                ])
        elif self.none:
            return not any([
                self.condition_fn(row, c.ignore_case, c.field, c.value) 
                for c in self.fn_criteria
                ])
        else:
            raise ValueError('FieldCondition must require all, any, or none criteria')
        

def field_equals(
    row: Series, 
    case_sensitive: bool, 
    target_field: str, 
    *target: str
) -> bool:
    target: Tuple[str] = flatten_to_tuple(target)
    field_val: str = str(row[target_field]) if target_field in row.index else ''
    if case_sensitive:
        field_val = field_val.lower()
        target = [t.lower() for t in target]
    return any([t == field_val for t in target]) \
        if target and field_val else False

def field_not_equals(
    row: Series, 
    case_insensitive: bool, 
    target_field: str, 
    *target: str
) -> bool:
    return not field_equals(row, case_insensitive, target_field, *target)

def field_startswith(
    row: Series, 
    case_insensitive: bool, 
    target_field: str, 
    *target: str
) -> bool:
    target: Tuple[str] = flatten_to_tuple(target)
    field_val: str = str(row[target_field]) if target_field in row.index else ''
    if case_insensitive:
        field_val = field_val.lower()
        target = [p.lower() for p in target]
    return field_val.startswith(target) \
        if target and field_val else False

def field_endswith(
    row: Series, 
    ignore_case: bool, 
    target_field: str, 
    *target: str
) -> bool:
    target: Tuple[str] = flatten_to_tuple(target)
    field_val: str = str(row[target_field]) if target_field in row.index else ''
    if ignore_case:
        field_val = field_val.lower()
        target = tuple([t.lower() for t in target])
    return field_val.endswith(target) \
        if target and field_val else False

def field_contains(
    row: Series, 
    case_insensitive: bool, 
    target_field: str, 
    *target: str
) -> bool:
    target: Tuple[str] = flatten_to_tuple(target)
    field_val: str = str(row[target_field]) if target_field in row.index else ''
    if case_insensitive:
        field_val = field_val.lower()
        target = [t.lower() for t in target]
    return any([t in field_val for t in target]) \
        if target and field_val else False

def field_is_empty(
    row: Series, 
    ignore_case: bool,
    target_field: str,
    *target: str
) -> bool:
    field_val: str = str(row[target_field]).lower().replace('nan', '').replace('null', '') if target_field in row.index else ''
    return field_val == '' if target_field in row.index else False


def flatten_to_tuple(
    target: str | Tuple[str] | List[str] | List[Tuple[str]],
) -> Tuple[str]:
    """
    flatten_to_tuple takes a string, tuple, or list of strings and returns a tuple of strings
    """
    if isinstance(target, str):
        return (target,)
    elif isinstance(target, list) or isinstance(target, tuple):
        return tuple(t for sublist in target for t in (sublist if isinstance(sublist, tuple) else (sublist,)))
    else:
        raise ValueError('target must be a string, tuple, or list of strings')