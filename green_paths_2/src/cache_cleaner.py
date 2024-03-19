""" """

import os

from green_paths_2.src.config import DATA_CACHE_DIR_PATH

from green_paths_2.src.logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.RED.value)


def empty_folder(folder_path: str) -> None:
    """
    Empty a folder by deleting all files in it.

    Parameters:
    - folder_path: Path to the folder to be emptied.
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            LOG.error(f"Failed to delete {file_path}. Reason: {e}")


def clear_cache_dirs(dirs: list[str]) -> None:
    LOG.info(f"Emptying cache directories: {dirs}")
    cache_root_dir_path = DATA_CACHE_DIR_PATH
    for dir in dirs:
        if dir == "all":
            empty_folder(cache_root_dir_path)
            return
    else:
        cache_dir_path = os.path.join(cache_root_dir_path, dir)
        if os.path.exists(cache_dir_path):
            empty_folder(os.path.join(cache_root_dir_path, dir))
        else:
            LOG.warning(f"Cache directory {cache_dir_path} is not valid, skippin.")
    LOG.info("Given cache directories emptied.")
