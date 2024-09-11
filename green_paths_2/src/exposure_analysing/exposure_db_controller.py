from ...src.config import (
    OUTPUT_RESULTS_TABLE,
    SEGMENT_STORE_TABLE,
    TRAVEL_TIMES_TABLE,
)
from ...src.database_controller import DatabaseController


class ExposureDbController:

    def __init__(self, db_handler: DatabaseController):
        self.db_handler = db_handler
        self.results_table_created = False

    def fetch_unvisited_segments(
        self, db_handler: DatabaseController, new_osm_ids: list[str]
    ) -> list[dict]:
        """
        Fetches segments that have not been visited yet, and updates the cache.

        Parameters
        ----------
        db_handler : DatabaseController
            Database controller object.
        path_osm_ids : list[str]
            List of OSM IDs.

        """
        # get all the segments that are not in the cache
        # check that not all element are nan
        if new_osm_ids and not all([x is None for x in new_osm_ids]):
            path_segments = db_handler.select_rows_by_osm_ids(
                SEGMENT_STORE_TABLE, new_osm_ids
            )
            # update the cache
            return path_segments
        return []

    def fetch_travel_times_for_segments(
        self, db_handler: DatabaseController, path_osm_ids: list[str]
    ) -> None:
        """
        Fetches travel times for segments and updates the cache.

        Parameters
        ----------
        db_handler : DatabaseController
            Database controller object.
        path_osm_ids : list[str]
            List of OSM IDs.

        """
        segments_travel_time = db_handler.select_rows_by_osm_ids(
            TRAVEL_TIMES_TABLE, path_osm_ids
        )
        return segments_travel_time

    def update_exposure_table(self, new_columns: list[str]) -> None:
        """
        Updates the exposure table with the given exposure data.

        Parameters
        ----------
        exposure_data : dict
            Exposure data.
        """

        # ROOPE TODO: tän salee vois tehä ihan vitun paljon helpommin ku joku loop... pitää vaa loopata settiin ihan kaikki mitä löytyy ja sit tehä niille noi luo table

        # Fetch existing columns in the table
        # db_columns = set(self.db_handler.get_existing_columns(OUTPUT_RESULTS_TABLE))

        # Collect all possible columns across all batches
        for column in new_columns:
            try:
                self.db_handler.add_column_if_not_exists(
                    table_name=OUTPUT_RESULTS_TABLE, column_name=column
                )
            except Exception as e:
                print(
                    f"Failed to add column '{column}' to table '{OUTPUT_RESULTS_TABLE}': {e}"
                )

        return new_columns
