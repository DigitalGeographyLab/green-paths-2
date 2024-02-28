""" Helper class to download OSM network data for a specified area. """

import os
import shutil
import pyrosm

from green_paths_2.src.logging import setup_logger, LoggerColors

from green_paths_2.src.config import DATA_CACHE_DIR_PATH, OSM_CACHE_DIR_NAME
from green_paths_2.src.timer import time_logger

LOG = setup_logger(__name__, LoggerColors.RED.value)


def get_available_pyrosm_data_sources() -> None:
    """List all available data sources from pyrosm."""
    LOG.info(pyrosm.data.available)


@time_logger
def download_and_move_osm_pbf(name_of_city: str) -> None:
    """Download OSM PBF file for a specified city and move it to cache dir."""
    pyrosm_default_save_path, cache_file_path = download_osm_pbf(name_of_city)

    # Move the file from pyrosm tmp default save path to cache dir
    if os.path.exists(pyrosm_default_save_path):
        shutil.move(pyrosm_default_save_path, cache_file_path)
    LOG.info(
        f"Downloaded {name_of_city} OSM network file to cache. Path: {cache_file_path}"
    )


def download_osm_pbf(area: str):
    """
    Download OSM PBF file for a specified area.
    :param area: Area name (e.g. Helsinki) as a string.
    :return: Path to the downloaded OSM PBF file.
    """

    network_file_name = f"{area}_network.osm.pbf"
    cache_file_path = os.path.join(
        DATA_CACHE_DIR_PATH, OSM_CACHE_DIR_NAME, network_file_name
    )

    if os.path.exists(cache_file_path):
        LOG.info(
            f"{network_file_name} OSM network file already exists in cache, skipping download. Path: {cache_file_path}"
        )
        return cache_file_path, cache_file_path

    if isinstance(area, str):
        return pyrosm.get_data(area), cache_file_path
    else:
        raise ValueError(
            "osm network area parameter should be name of city (string). For supported cities run: python green_paths_2.py fetch_osm_network -l"
        )
