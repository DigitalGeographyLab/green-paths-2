""" Main module for the exposure analysing pipeline."""

import geopandas as gpd

from ..config import (
    NAME_KEY,
)
from ..exposure_analysing.exposure_calculator import ExposureCalculator
from ..exposure_analysing.exposure_data_handlers import (
    get_datas_from_sources,
    save_final_results_data,
)
from ..green_paths_exceptions import PipeLineRuntimeError
from ..preprocessing.user_config_parser import UserConfig
from ..timer import time_logger

from ..logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


@time_logger
def exposure_analysing_pipeline(
    user_config: UserConfig,
    exposure_gdf: gpd.GeoDataFrame = None,
    processed_osm_network_gdf: gpd.GeoDataFrame = None,
    routing_results_gdf: gpd.GeoDataFrame = None,
    actual_travel_times_gdf: gpd.GeoDataFrame | list = None,
):
    """
    Run the exposure analysing pipeline.

    Parameters
    ----------
    user_config : UserConfig
        User configuration object.
    exposure_gdf : gpd.GeoDataFrame, optional
        GeoDataFrame containing exposure data. Defaults to None.
    processed_osm_network_gdf : gpd.GeoDataFrame, optional
        GeoDataFrame containing processed OSM network data. Defaults to None.
    routing_results_gdf : gpd.GeoDataFrame, optional
        GeoDataFrame containing routing results. Defaults to None.
    actual_travel_times_gdf : gpd.GeoDataFrame, optional
        GeoDataFrame containing actual travel times. Defaults to None.

    Raises
    ------
    PipeLineRuntimeError
        If the exposure analysing pipeline fails.
    """
    LOG.info("\n\n\nStarting analysing pipeline\n\n\n")

    # the preprocessing code and locis is messy
    # the code is not well structured
    # these are mainly affected by time constraints
    # all this probably should be refactored

    # also the logic of turning everything to df or gdf is not ideal
    # should support the original types like dicts etc.
    # although If the support for df/gdf support is wanted, double logic is needed
    try:
        (
            routing_results,
            segment_exposure_store,
            osm_network_store,
            actual_travel_times_store,
        ) = get_datas_from_sources(
            user_config=user_config,
            exposure_gdf=exposure_gdf,
            osm_network_gdf=processed_osm_network_gdf,
            routing_results_gdf=routing_results_gdf,
            actual_travel_times_gdf=actual_travel_times_gdf,
        )

        # validate that the data is found
        if (
            not routing_results
            or not segment_exposure_store
            or not osm_network_store
            or not actual_travel_times_store
        ):
            raise ValueError("Data not found for analysing pipeline.")

        exposure_calculator = ExposureCalculator(
            user_config=user_config,
            routing_results=routing_results,
            segment_exposure_store=segment_exposure_store,
            osm_network_store=osm_network_store,
            actual_travel_times_store=actual_travel_times_store,
            data_names=[data.get(NAME_KEY) for data in user_config.data_sources],
        )

        # TODO: mieti tehokkuutta -> voiko muisti loppua kesken? voisko nää jutut tehdä tehokkaammin???

        exposure_calculator.construct_master_statistics_dict()

        if not exposure_calculator.get_master_statistics_store():
            raise ValueError("No statistics found for any paths.")

        # TODO: analyze master statistics store? -> crash if not enough data found?

        exposure_calculator.calculate_and_combine_paths_statistics()

        if not exposure_calculator.get_master_statistics_store():
            raise ValueError("No statistics found for any paths.")

        combined_results_per_path = (
            exposure_calculator.get_master_combined_statistics_store()
        )

        if not combined_results_per_path:
            raise ValueError("No combined path statistics found for any paths.")

        saved_final_result = save_final_results_data(
            user_config=user_config,
            combined_master_statistics_store=combined_results_per_path,
        )

        print("this is all in final results")
        print(saved_final_result)
        print(len(saved_final_result))
        print(saved_final_result.columns)

        if not saved_final_result.empty:
            LOG.info(f"Saved final result df/gdf head {saved_final_result.head()}")

        LOG.info("Analysing pipeline finished.")
    except PipeLineRuntimeError as e:
        LOG.error(f"Analysing pipeline failed with error: {e}")
        raise e
