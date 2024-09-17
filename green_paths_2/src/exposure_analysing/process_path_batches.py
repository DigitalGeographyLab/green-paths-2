""" This module contains the functions to process the routing results in batches. """

import json

from ..database_controller import DatabaseController
from ..exposure_analysing.exposure_db_controller import ExposureDbController
from ..exposure_analysing.exposures_calculator import ExposuresCalculator
from ..preprocessing.user_config_parser import UserConfig

from ..exposure_analysing.exposure_data_handlers import get_batch_limit


from ..config import (
    ANALYSING_KEY,
    CUMULATIVE_RANGES_KEY,
    DB_OUTPUT_RESULST_BASE_COLUMNS,
    FROM_ID_KEY,
    OSM_IDS_KEY,
    OUTPUT_RESULTS_TABLE,
    ROUTING_RESULTS_TABLE,
    TO_ID_KEY,
)
from ..green_paths_exceptions import PipeLineRuntimeError
from ..logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


# TODO: rename
def process_exposure_results_as_batches(
    db_handler: DatabaseController,
    exposure_db_controller: ExposureDbController,
    exposure_calculator: ExposuresCalculator,
    user_config: UserConfig,
    data_names: list[str],
    keep_geometries: bool,
    existing_columns: set = None,
):

    routing_results_count = db_handler.get_row_count(ROUTING_RESULTS_TABLE)

    if routing_results_count == 0:
        raise RuntimeError("No routing results found in exposure analysing")

    batch_limit = get_batch_limit(routing_results_count=routing_results_count)

    # tää ylemmäs:
    # first time create the table
    # results_table_exists = self.db_handler.check_table_exists(OUTPUT_RESULTS_TABLE)

    db_handler.create_table_from_dict_data(
        table=OUTPUT_RESULTS_TABLE, data=DB_OUTPUT_RESULST_BASE_COLUMNS, force=True
    )

    # init the all possible columns with the defaults that can be found from each path
    # and which were already added to the db
    if existing_columns:
        all_possible_columns = existing_columns.copy()
        all_possible_columns.update({TO_ID_KEY, FROM_ID_KEY})
    else:
        all_possible_columns = {TO_ID_KEY, FROM_ID_KEY}

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

            # fetch segments that have not been visited yet and add to cache
            # will add the whole segment from segment store to cache
            exposure_calculator.update_segment_cache_if_new_segments(
                db_handler=db_handler,
                exposure_db_controller=exposure_db_controller,
                path_osm_ids=path_osm_ids,
            )

            cumulative_ranges = user_config.get_nested_attribute(
                [ANALYSING_KEY, CUMULATIVE_RANGES_KEY]
            )

            # calculate and save path exposures
            single_path_results = (
                exposure_calculator.calculate_and_save_combined_path_exposures(
                    path_osm_ids, data_names, path, cumulative_ranges, keep_geometries
                )
            )

            exposure_calculator._add_to_path_batch_results(single_path_results)
            # clear single path cache after each path
            exposure_calculator.clear_single_path_results()

        # add to db after each batch
        batch_path_results = exposure_calculator.get_batch_combined_path_results()

        if not batch_path_results:
            # TODO: should we actually just return?
            raise PipeLineRuntimeError(
                "No paths found in the batch, check the routing results. Maybe no overlap of street network with the OD data?"
            )

        found_columns_from_batch = {
            key for item in batch_path_results for key in item.keys()
        }

        new_columns = found_columns_from_batch - all_possible_columns

        if new_columns:
            # create table or update if exists and new columns found
            new_columns = exposure_db_controller.update_exposure_table(new_columns)

            all_possible_columns.update(new_columns)

        db_handler.add_many_list(OUTPUT_RESULTS_TABLE, batch_path_results)

        # after each batch processed and added to db, clear the batch specific cache
        exposure_calculator.clear_batch_combined_path_results()

    # TODO: maybe remove this if API analysing logic is changed...
    return all_possible_columns
