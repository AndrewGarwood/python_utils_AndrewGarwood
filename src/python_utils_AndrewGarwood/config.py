"""
Configure global variables used in the module.
ENABLE_OVERWRITE: If True, allows overwriting existing files when writing dataframes to files.
ENABLE_DETAILED_LOG: If True, enables detailed logging for debugging purposes.
"""
ENABLE_OVERWRITE: bool = False
ENABLE_DETAILED_LOG: bool = True
DF_FILE_NAME: str = 'inventory_item.csv'