""" """

from green_paths_2.src.config import (
    SEGMENT_STORE_TABLE,
    TRAVEL_TIME_KEY,
    TRAVEL_TIMES_TABLE,
)
import sqlite3
import pandas as pd
import geopandas as gpd
from shapely import wkt
from green_paths_2.src.database_controller import DatabaseController


class ExposureDbController:

    def __init__(self, db_handler: DatabaseController):
        self.db_handler = db_handler

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
        if new_osm_ids:
            path_segments = db_handler.select_rows_by_osm_ids(
                SEGMENT_STORE_TABLE, new_osm_ids
            )
            # update the cache
            return path_segments

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
