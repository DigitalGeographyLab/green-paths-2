""" Main module for the exposure analysing pipeline."""

import json
import os
import geopandas as gpd
import pandas as pd

from green_paths_2.src.database_controller import DatabaseController
from green_paths_2.src.exposure_analysing.exposure_db_controller import (
    ExposureDbController,
)
from green_paths_2.src.exposure_analysing.exposures_calculator import (
    ExposuresCalculator,
)

from ..config import (
    ANALYSING_KEY,
    CSV_FILE_NAME,
    CUMULATIVE_RANGES_KEY,
    GP2_DB_PATH,
    GPKG_FILE_NAME,
    KEEP_GEOMETRY_KEY,
    NAME_KEY,
    OSM_IDS_KEY,
    OUTPUT_FINAL_RESULTS_DIR_PATH,
    OUTPUT_RESULTS_FILE_NAME,
    OUTPUT_RESULTS_TABLE,
    ROUTING_RESULTS_TABLE,
    SAVE_OUTPUT_NAME_KEY,
    TRAVEL_TIME_KEY,
)
from ..exposure_analysing.exposure_data_handlers import (
    get_batch_limit,
    save_to_gpkg_or_csv,
)
from ..green_paths_exceptions import PipeLineRuntimeError
from ..preprocessing.user_config_parser import UserConfig
from ..timer import time_logger

from ..logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


@time_logger
def exposure_analysing_pipeline(user_config: UserConfig):
    """
    Run the exposure analysing pipeline.

    Parameters
    ----------
    user_config : UserConfig
        User configuration object.

    Raises
    ------
    PipeLineRuntimeError
        If the exposure analysing pipeline fails.
    """
    LOG.info("\n\n\nStarting analysing pipeline\n\n\n")

    try:
        output_results_table_created = False

        db_handler = DatabaseController(GP2_DB_PATH)
        exposure_db_controller = ExposureDbController(db_handler)
        exposure_calculator = ExposuresCalculator()
        routing_results_count = db_handler.get_row_count(ROUTING_RESULTS_TABLE)
        batch_limit = get_batch_limit(
            user_config=user_config, routing_results_count=routing_results_count
        )
        # get data names as list so that we can loop each different data source
        data_names = [data.get(NAME_KEY) for data in user_config.data_sources]
        # process the routing results in batches
        for offset in range(0, routing_results_count, batch_limit):
            # clear cache for not to overflow memory
            exposure_calculator.clear_segment_cache()
            # clear batch specific cache
            exposure_calculator.clear_batch_combined_path_results()
            # fetch a batch of routing results
            routing_results_batch = db_handler.fetch_batch(
                ROUTING_RESULTS_TABLE, limit=batch_limit, offset=offset
            )
            LOG.info(
                f"Processing {offset} - {offset + batch_limit} / {routing_results_count} paths"
            )
            for path in routing_results_batch:
                # Convert row osmids to list from JSON string
                path_osm_ids = json.loads(path[OSM_IDS_KEY])
                # skip if no osmids in path...
                if not path_osm_ids:
                    continue

                new_osm_ids = exposure_calculator._get_new_osmids(path_osm_ids)
                # fetch unvisited segments to cache
                path_segments = exposure_db_controller.fetch_unvisited_segments(
                    db_handler, new_osm_ids
                )
                # update new segments to cache and fetch travel times
                if path_segments:
                    # update the exposure calculator osmids cache
                    exposure_calculator.update_segments_cache(path_segments)
                    # fetch travel times for the new segments
                    segments_travel_time = (
                        exposure_db_controller.fetch_travel_times_for_segments(
                            db_handler, new_osm_ids
                        )
                    )
                    # updata travel times to the exposure calculator osmids cache
                    exposure_calculator.update_segments_cache_value(
                        segments_travel_time, TRAVEL_TIME_KEY
                    )

                cumulative_ranges = user_config.get_nested_attribute(
                    [ANALYSING_KEY, CUMULATIVE_RANGES_KEY]
                )
                keep_geometries = user_config.get_nested_attribute(
                    [ANALYSING_KEY, KEEP_GEOMETRY_KEY]
                )

                # calculate and save path exposures
                exposure_calculator.calculate_and_save_combined_path_exposures(
                    path_osm_ids, data_names, path, cumulative_ranges, keep_geometries
                )
                # clear single path cache after each path
                exposure_calculator.clear_single_path_results()

            # add to db after each batch
            batch_path_results = exposure_calculator.get_batch_combined_path_results()

            # create table for final outputs if not yet created
            if not output_results_table_created:
                table_structure_from_data = next(iter(batch_path_results))

                db_handler.create_table_from_dict_data(
                    OUTPUT_RESULTS_TABLE, table_structure_from_data
                )
                output_results_table_created = True

            db_handler.add_many_list(OUTPUT_RESULTS_TABLE, batch_path_results)

            # after each batch processed and added to db, clear the batch specific cache
            exposure_calculator.clear_batch_combined_path_results()

        # after all chunks are processed, get all and save to csv of gpkg
        output_all_final_results, output_column_names = db_handler.get_all(
            OUTPUT_RESULTS_TABLE, column_names=True
        )

        final_output_df = pd.DataFrame(
            output_all_final_results, columns=output_column_names
        )

        # see if user configurations have output file name, if not use defaults
        output_file_name = user_config.get_nested_attribute(
            [ANALYSING_KEY, SAVE_OUTPUT_NAME_KEY]
        )
        if not output_file_name:
            output_file_name = OUTPUT_RESULTS_FILE_NAME

        output_file_type = GPKG_FILE_NAME if keep_geometries else CSV_FILE_NAME

        time_now = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
        results_output_path = os.path.join(
            OUTPUT_FINAL_RESULTS_DIR_PATH,
            f"{time_now}_{output_file_name}.{output_file_type}",
        )
        save_to_gpkg_or_csv(final_output_df, results_output_path)

        LOG.info("Analysing pipeline finished.")
    except PipeLineRuntimeError as e:
        LOG.error(f"Analysing pipeline failed with error: {e}")
        raise e
