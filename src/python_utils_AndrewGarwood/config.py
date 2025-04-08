"""
Configure global variables used in the module.
ENABLE_OVERWRITE: If True, allows overwriting existing files when writing dataframes to files.
ENABLE_DETAILED_LOG: If True, enables detailed logging for debugging purposes.
"""
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