"""
@file: config/env.py

Configure global variables used in the module.
ENABLE_OVERWRITE: If True, allows overwriting existing files when writing dataframes to files.
ENABLE_DETAILED_LOG: If True, enables detailed logging for debugging purposes.
"""
__all__ = [
    'ENABLE_OVERWRITE', 'ENABLE_DETAILED_LOG', 'DF_FILE_NAME',
    'set_enable_detailed_log', 'set_enable_overwrite', 'set_df_file_name', 
    
    'DEFAULT_LOG', 'PATH_TO_LOGS', 'setup_logging', 'log', 'LogLevelEnum',
    'STOP_RUNNING',
]
import os
import sys
import logging
from typing import List, Dict
from datetime import datetime
from enum import Enum
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

CONFIG_ENV_FILE_PATH = Path(__file__).resolve()
PATH_TO_LOGS = CONFIG_ENV_FILE_PATH.parent.parent / 'logs'
"""
`PATH_TO_LOGS: Path = CURRENT_FILE_PATH.parent.parent / 'logs'`
- `CURRENT_FILE_PATH.parent` is the parent directory of the current file, which is the 'config' directory.
- `CURRENT_FILE_PATH.parent.parent` is the parent directory of the 'config' directory, which is the root directory of the project.
"""
DEFAULT_LOG: str = os.getenv('DEFAULT_LOG', str(CONFIG_ENV_FILE_PATH.parent.parent / 'logs' / 'DEFAULT_LOG.log'))

IS_LOGGING_SETUP: bool = False



def STOP_RUNNING(msg:str=None, exit_code:int=0) -> None:
    """Stop the program from running.
    Args:
        msg (str): Optional message to display before stopping the program.
        exit_code (int): Exit code to return when stopping the program. Default is 0.
    """
    print(f"Stopping the program with exit code {exit_code}", f'\n{msg}' if msg else "")
    sys.exit(exit_code)

def setup_logging(filename: str='DEFAULT_LOG', format: str='%(asctime)s - %(levelname)s - %(message)s') -> None:
    """Set up logging configuration.
    This function configures the logging settings for the module. It sets the logging level to `INFO`, specifies the format of log messages, and defines the handlers for log output.
    The log messages will be sent to both the console and a file, `PATH_TO_LOGS / f'{filename}.log'`.
    Args:
        filename (str): The name of the log file. Default is `'DEFAULT_LOG'`.
        format (str): The format of the log messages. Default is `'%(asctime)s - %(levelname)s - %(message)s'`.
    Example:
    ```
    setup_logging(filename='my_log', format='%(asctime)s - %(levelname)s - %(message)s')
    ```
    """
    logging.basicConfig(
        level=logging.INFO,
        format=format,  # each log message will include the timestamp (asctime), the severity level (levelname), and the actual log message (message), separated by hyphens.
        handlers=[  # specify where the log messages should be sent. In this case, a log.StreamHandler() is provided, which directs the log output to the standard output stream (typically the console). This is useful for real-time monitoring of log messages during script execution.
            logging.StreamHandler(),
            logging.FileHandler(filename=PATH_TO_LOGS / f'{filename}.log')
            ]
    )
    global IS_LOGGING_SETUP
    IS_LOGGING_SETUP = True
    
class LogLevelEnum(Enum):
    """Enum for log levels.
    Args:
        DEBUG (str): Debug level.
        INFO (str): Info level.
        WARNING (str): Warning level.
        ERROR (str): Error level.
        CRITICAL (str): Critical level.
    """
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

def log(
    label: str, 
    *details, 
    log_level: LogLevelEnum=LogLevelEnum.DEBUG, 
    label_indent: int=None, 
    subdetails: Dict[str, List[str]], 
    **kwargs
) -> None:
    """Wrapper function for logging module.
    This function allows you to log messages at different severity levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
    Args:
        label (str): The main message/title/label of the log. Can be indented if `label_indent` is provided.
        *details: Additional arguments to pass to the logging function. Will be indented by 4 spaces.
        log_level (str): The logging level. Default is `DEBUG`.
        subdetails (dict): A dictionary of subdetails to log. Each key-value pair represents a `sublabel` (indented 8 spaces) mapped to a `subdetails_list` (indented 12 spaces).
        label_indent (int): The number of spaces to indent the label. Default is `None`.
        **kwargs: Additional keyword arguments to pass to the logging function.
    """
    if not IS_LOGGING_SETUP:
        setup_logging()
    
    SPACES_PER_INDENT = 4
    TMESTAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # remove when confirm if redundant
    indented_args = []
    label = f'log() [{TMESTAMP}] ' + str(label).strip()
    
    if label_indent is not None and isinstance(label_indent, int):
        label = label.rjust(SPACES_PER_INDENT * label_indent + len(label))
    
    if details is not None and isinstance(details, list):
        largest_detail_length: int = max([len(str(detail)) for detail in details]) if details else 0
        indented_args.extend([str(detail).rjust(SPACES_PER_INDENT + largest_detail_length) for detail in details])
    
    if subdetails is not None and isinstance(subdetails, dict):
        for sublabel, subdetails_list in subdetails.items():
            sublabel = str(sublabel).strip().rjust(SPACES_PER_INDENT * 2 + len(sublabel))
            indented_args.append(sublabel)
            largest_subdetail_length: int = max([len(str(subdetail)) for subdetail in subdetails_list]) if subdetails_list else 0
            indented_args.extend([str(subdetail).rjust(SPACES_PER_INDENT * 3 + largest_subdetail_length) for subdetail in subdetails_list])
    
    match log_level:
        case LogLevelEnum.DEBUG:
            logging.debug(label, *indented_args, **kwargs)
        case LogLevelEnum.INFO:
            logging.info(label, *indented_args, **kwargs)
        case LogLevelEnum.WARNING:
            logging.warning(label, *indented_args, **kwargs)
        case LogLevelEnum.ERROR:
            logging.error(label, *indented_args, **kwargs)
        case LogLevelEnum.CRITICAL:
            logging.critical(label, *indented_args, **kwargs)
        case _:
            raise ValueError(f"Invalid log level: {log_level}")


ENABLE_OVERWRITE: bool = False
ENABLE_DETAILED_LOG: bool = True
DF_FILE_NAME: str = 'inventory_item.csv'

def set_enable_detailed_log(enable: bool) -> None:
    """
    Set the ENABLE_DETAILED_LOG variable to enable or disable detailed logging.

    Args:
        enable (bool): If True, enables detailed logging. If False, disables it.
    """
    if not isinstance(enable, bool):
        raise ValueError("enable must be a boolean value")
    global ENABLE_DETAILED_LOG
    ENABLE_DETAILED_LOG = enable

def set_enable_overwrite(enable: bool) -> None:
    """
    Set the ENABLE_OVERWRITE variable to enable or disable overwriting existing files.

    Args:
        enable (bool): If True, enables overwriting existing files. If False, disables it.
    """
    if not isinstance(enable, bool):
        raise ValueError("enable must be a boolean value")
    global ENABLE_OVERWRITE
    ENABLE_OVERWRITE = enable

def set_df_file_name(file_name: str) -> None:
    """
    Set the DF_FILE_NAME variable to specify the file name for dataframes.

    Args:
        file_name (str): The file name to set for dataframes.
    """
    if (not file_name or type(file_name) != str or len(file_name) < 1):
        raise ValueError("file_name must be a non-empty string")
    global DF_FILE_NAME
    DF_FILE_NAME = file_name