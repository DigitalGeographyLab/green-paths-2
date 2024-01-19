import os
import shutil
from pyrosm import get_data
from typing import Union, Tuple

from src.logging import setup_logger, LoggerColors


from src.config import DATA_CACHE_DIR_PATH

# helsinki_pbf = download_osm_pbf("Helsinki")
# bbox_pbf = download_osm_pbf((24.940, 60.155, 25.020, 60.205))  # Example coordinatess


# DATA_CACHE_DIR_PATH: str = (
#     "/Users/hcroope/omat/GP2/green_paths_2/green_paths_2/src/data/cache"
# )


LOG = setup_logger(__name__, LoggerColors.RED.value)


def download_osm_pbf(area: Union[str, Tuple[float, float, float, float]]):
    """
    Download OSM PBF file for a specified area.
    :param area: Area name (e.g. Helsinki) as a string OR bounding box as a tuple (minx, miny, maxx, maxy).
    :return: Path to the downloaded OSM PBF file.
    """

    network_file_name = f"{area}_osm_network.osm.pbf"
    cache_file_path = os.path.join(DATA_CACHE_DIR_PATH, network_file_name)

    if os.path.exists(cache_file_path):
        LOG.info(
            f"OSM network file already exists in cache, skipping download. Path: {cache_file_path}"
        )
        return cache_file_path, cache_file_path

    if isinstance(area, str):
        return get_data(area), cache_file_path
    elif isinstance(area, tuple) and len(area) == 4:
        return get_data(bbox=area), cache_file_path
    else:
        raise ValueError(
            "osm network area parameter should be either name (string) or bounding box coordinates (tuple)."
        )


import argparse

# roope todo -> tää vaa väliaikainen...
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a function with a CLI parameter.")
    parser.add_argument(
        "param",
        type=str,
        help="Name of city or a bounding box (tuple, minx, miny, maxx, maxy).",
    )

    args = parser.parse_args()

    default_path, cache_file_path = download_osm_pbf(args.param)

    # Move the file
    if os.path.exists(default_path):
        shutil.move(default_path, cache_file_path)
