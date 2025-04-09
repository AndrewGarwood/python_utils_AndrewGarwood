"""
Configure global variables used in the module.
ENABLE_OVERWRITE: If True, allows overwriting existing files when writing dataframes to files.
ENABLE_DETAILED_LOG: If True, enables detailed logging for debugging purposes.
"""
__all__ = [
    'ENABLE_OVERWRITE', 'ENABLE_DETAILED_LOG', 'DF_FILE_NAME',
    'set_enable_detailed_log', 'set_enable_overwrite', 'set_df_file_name'
]
ENABLE_OVERWRITE: bool = False
ENABLE_DETAILED_LOG: bool = True
DF_FILE_NAME: str = 'inventory_item.csv'

def set_enable_detailed_log(enable: bool) -> None:
    """
    Set the ENABLE_DETAILED_LOG variable to enable or disable detailed logging.

    Args:
        enable (bool): If True, enables detailed logging. If False, disables it.
    """
    global ENABLE_DETAILED_LOG
    ENABLE_DETAILED_LOG = enable


def set_enable_overwrite(enable: bool) -> None:
    """
    Set the ENABLE_OVERWRITE variable to enable or disable overwriting existing files.

    Args:
        enable (bool): If True, enables overwriting existing files. If False, disables it.
    """
    global ENABLE_OVERWRITE
    ENABLE_OVERWRITE = enable

def set_df_file_name(file_name: str) -> None:
    """
    Set the DF_FILE_NAME variable to specify the file name for dataframes.

    Args:
        file_name (str): The file name to set for dataframes.
    """
    global DF_FILE_NAME
    DF_FILE_NAME = file_name