""" TODO """

import geopandas as gpd

from green_paths_2.src.data_utilities import (
    save_gdf_to_cache_as_gpkg,
)

from green_paths_2.src.exposure_analysing.exposure_calculator import ExposureCalculator
from green_paths_2.src.exposure_analysing.exposure_data_handlers import (
    load_datas_from_cache,
)
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.preprocessing.data_types import RoutingComputers
from green_paths_2.src.preprocessing.user_config_parser import UserConfig
from green_paths_2.src.timer import time_logger

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


def exposure_analysing_pipeline(user_config: UserConfig) -> None:
    """TODO"""
    LOG.info("\n\n\nStarting analysing pipeline\n\n\n")
    routing_results, segment_exposure_store, osm_network_store = load_datas_from_cache(
        user_config.routing.computer
    )

    # TODO -> move this...
    data_names = [data.get("name") for data in user_config.data_sources]

    exposure_calculator = ExposureCalculator(
        routing_results=routing_results,
        segment_exposure_store=segment_exposure_store,
        osm_network_store=osm_network_store,
        data_names=data_names,
    )

    exposure_calculator.construct_master_statistics_dict()

    # TODO: analyze master statistics store?

    exposure_calculator.combine_all_path_statistics_to_master_combined_statistics_list()

    # TODO: ehkä laita noi jonnekki muualle kuin tonne samaan storee

    # TODO: -> nyt tukee vaan 1 -> kato miten järkevä monelle reitille, ehkä se key = from_id + to_id tms?
    # TODO: -> tee joku saveus esim gdf

    print("test combined path statistics")

    test_combined = exposure_calculator.get_master_combined_statistics_store()

    # print(test_combined)
    # print("täää oli toi combined list")
    # return

    test_combined_gdf = gpd.GeoDataFrame(test_combined)

    # set geometry to test_combined_gdf
    # test_combined_gdf.set_geometry("geometry")

    # check crs and set it if not found or incorrect
    if not test_combined_gdf.crs or test_combined_gdf.crs != "EPSG:4326":
        test_combined_gdf.crs = "EPSG:4326"

    print("the crs is...")
    print(test_combined_gdf.crs)

    save_gdf_to_cache_as_gpkg(
        test_combined_gdf,
        "green_paths_2/src/cache/exposure_analysing/test_results.gpkg",
    )

    print(test_combined_gdf)

    # todo
