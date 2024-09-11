""" Cache cleaner module. """

import os

from ..src.database_controller import DatabaseController
from .config import GP2_DB_PATH
from .green_paths_exceptions import DataManagingError
from .logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.RED.value)


def empty_folder(folder_path: str) -> None:
    """
    Empty a folder by deleting all files in it.

    Parameters:
    ------------
    - folder_path: Path to the folder to be emptied.

    Raises:
    -----------
    - DataManagingError: If the file deletion fails.
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except DataManagingError as e:
            LOG.error(f"Failed to delete {file_path}. Reason: {e}")


def clear_db(table_names: list[str]):
    LOG.info("Clearing db tables")
    db_handler = DatabaseController()
    conn = db_handler.connect()
    cursor = conn.cursor()
    if not table_names:
        # get all table names to clear
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = cursor.fetchall()
        table_names = [db_item[0] for db_item in table_names]

    for table_name in table_names:
        clear_table(conn, cursor, table_name)
    conn.close()
    LOG.info(f"Tables cleared succesfully: {table_names}")


def clear_table(conn, cursor, table_name):
    # Clear the specified table
    cursor.execute(f"DELETE FROM {table_name};")
    # Commit changes
    conn.commit()
