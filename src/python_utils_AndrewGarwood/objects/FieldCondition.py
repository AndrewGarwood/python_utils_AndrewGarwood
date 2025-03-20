from dataclasses import dataclass
from typing import Callable, List, Tuple, Dict
from pandas import Series

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
    value: Tuple[str] | List[str] | str
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
        all\_ (bool): Default True, if True all criteria must be met
        any\_ (bool): Default False
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