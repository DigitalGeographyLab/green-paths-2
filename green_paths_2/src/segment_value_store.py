""" Store for segment values. """

import pandas as pd
import geopandas as gpd
from green_paths_2.src.config import SEGMENT_VALUES_ROUND_DECIMALS

from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.preprocessing.data_source import DataSource


LOG = setup_logger(__name__, LoggerColors.RED.value)


# TODO: get from user_config -> data_keys which are used to calculate normalized value


class SegmentValueStore:

    def __init__(self):
        self.master_segment_store: dict[str, dict[str, float]] = {}
        self.master_segment_gdf: gpd.GeoDataFrame = gpd.GeoDataFrame()

    def get_store(self) -> dict[str, dict[str, float]]:
        return self.master_segment_store

    def set_store(self, master_segment_store: dict[str, dict[str, float]]):
        self.master_segment_store = master_segment_store

    def get_segment_values(
        self, segment_osmids: str | int | list[str | int], drop_osm_id: bool = False
    ) -> dict[str, float | bool]:
        """
        Get exposure values for a single segment or multiple segments using the .get() method.

        Parameters:
        - segment_osmids: OSM ID of the segment or a list of OSM IDs.
        - drop_osm_id: If True, drops the OSM ID from the returned dictionary.

        Returns a dictionary with the OSM IDs as keys and the exposure values as values.
        If a segment ID is not found, returns False for that ID.
        """
        if isinstance(segment_osmids, list):
            return {
                str(osm_id): self.master_segment_store.get(int(osm_id), False)
                for osm_id in segment_osmids
            }
        else:
            if drop_osm_id:
                return self.master_segment_store.get(int(segment_osmids), False)
            else:
                return {
                    str(segment_osmids): self.master_segment_store.get(
                        int(segment_osmids), False
                    )
                }

    def get_all_segment_osmids(self) -> list[str]:
        """
        Get all segments from master segment store.

        Returns:
        - List of segment OSM IDs.
        """
        return list(self.master_segment_store.keys())

    def populate_master_segment_gdf_with_geometries_from_pbf(self, pbf_file_path: str):
        """Populate master segment GeoDataFrame with geometries from PBF file."""
        pass

    def validate_user_min_max_values(self, data_sources: list[DataSource]) -> None:
        """Validate user defined min and max values."""
        values_not_in_range = []
        for data_key, data_source in data_sources.items():
            for osm_id, data in self.master_segment_store.items():
                if data_key in data:
                    if (
                        data[data_key] < data_source.min_data_value
                        or data[data_key] > data_source.max_data_value
                    ):
                        values_not_in_range.append(osm_id, data[data_key])
        if values_not_in_range:
            LOG.warning(
                f"WARNING: {len(values_not_in_range)} values are not within the user defined min and max values. Values: {values_not_in_range}. They will be fitted to the user defined min and max values."
            )

    def save_normalized_values_to_store(self, data_sources) -> list[str]:
        """
        Save normalized values to the master segment store.

        Parameters:
        - data_keys: List of data keys in the segment store.

        Returns:
        - List of normalized data keys.
        """
        normalized_data_keys = []
        for data_key, data_source in data_sources.items():
            normalized_data_key = f"{data_key}_normalized"
            normalized_values = self.calculate_normalised_values(
                data_key,
                data_source.good_exposure,
                data_source.min_data_value,
                data_source.max_data_value,
            )
            self.save_segment_values(normalized_values, normalized_data_key)
            normalized_data_keys.append(normalized_data_key)
        return normalized_data_keys

    def calculate_normalised_values(
        self,
        data_key: str,
        data_good_exposure: bool,
        min_data_value: float | int,
        max_data_value: float | int,
    ) -> dict[str, float]:
        """
        Calculate normalised values for each segment.

        Parameters:
        - data_key: The key of the data source in the segment store.
        - data_good_exposure: TODO

        Returns:
        - Dictionary with the OSM IDs as keys and the normalised values as values.
        """
        # meta_data = self.get_data_info_from_segment_store(data_key)
        # min_val, max_val = meta_data["min"], meta_data["max"]
        normalized_values = {}

        # Iterate through each segment in the master segment store
        for osm_id, data in self.master_segment_store.items():
            if data_key in data:

                # make sure that the data is within the min and max values
                if data[data_key] < min_data_value:
                    exposure_data = min_data_value
                elif data[data_key] > max_data_value:
                    exposure_data = max_data_value
                else:
                    exposure_data = data[data_key]

                # Calculate the normalized value, use min-max formula
                normalized_value = (exposure_data - min_data_value) / (
                    max_data_value - min_data_value
                )

                # Ensure the normalized value is within 0-1
                normalized_value = max(0, min(normalized_value, 1))

                # if data is good exposure, set to normalized value to negative
                # good exposure should make the cost factor smaller (Dijkstra's algorithm)
                # e.g. cheaper road to take in routing
                # negative exposures should be avoided (e.g. noise, air pollution, etc.)
                # by having the cost factor positive, which will increase the cost of the road
                if data_good_exposure:
                    normalized_value = -normalized_value

                # Round and store to store
                normalized_values[osm_id] = round(
                    normalized_value, SEGMENT_VALUES_ROUND_DECIMALS
                )

        return normalized_values

    def get_data_info_from_segment_store(self, data_key: str) -> dict:
        # get min, max, mean, median, std, etc. for each data source from segment store
        data_values = []
        for _, data in self.master_segment_store.items():
            if data_key in data:
                data_values.append(data[data_key])

        return {
            "min": min(data_values),
            "max": max(data_values),
            "mean": sum(data_values) / len(data_values),
            "median": sorted(data_values)[len(data_values) // 2],
            "std": pd.Series(data_values).std(),
        }

    # TODO: test e.g. with
    # from shapely.geometry import Point
    # # Example nested dict: {123: {'noise_data': 1.5, 'geometry': 'POINT(1 2)'}}
    # nested_dict = {
    #     123: {'noise_data': 1.5, 'air_quality': 2.0, 'geometry': Point(1, 2)},
    #     # Add more entries as needed
    # }
    def convert_segment_store_to_gdf(self) -> gpd.GeoDataFrame:
        """
        Convert segment store to GeoDataFrame.

        Returns:
        - GeoDataFrame with segment geometries and values.
        """
        try:
            segment_store = self.get_master_segment_store()
            # Convert segment store to DataFrame
            df = pd.DataFrame.from_dict(segment_store, orient="index")
            # Convert geometry column to GeoSeries
            geometries = gpd.GeoSeries(df.pop("geometry"))
            # Convert DataFrame to GeoDataFrame
            gdf = gpd.GeoDataFrame(df, geometry=geometries)
            return gdf
        except Exception as e:
            LOG.error(f"Error converting segment store to GeoDataFrame: {e}")

    def save_segment_values(self, data_segment_values: dict, data_name: str) -> None:
        """
        Merge segment values from current data to master segment values.

        Parameters:
        - segment_values_current_data: The segment values from the current data.
        - data_name: The name of the data source.

        Returns:
        - The updated master segment values dictionary.
        """
        try:
            master_store = self.master_segment_store.copy()
            for osm_id, value in data_segment_values.items():
                if osm_id not in master_store:
                    master_store[osm_id] = {}
                master_store[osm_id][data_name] = value
            self.set_store(master_store)
        except Exception as e:
            # TODO: throw error?
            LOG.error(f"Error saving segment values: {e}")

    # TODO: tarvitaanko? -> arvojen lisääminen gdf -> pitäisikö kaikki lisätä dictinä?
    # def merge_segment_values(
    #     master_segment_values: gpd.GeoDataFrame,
    #     segment_values_current_data: dict,
    #     data_name: str,
    # ) -> gpd.GeoDataFrame:

    #     for (
    #         data_name,
    #         data_values,
    #     ) in segment_values_current_data:  # loop_data yields data name and values
    #         # Convert data_values dict to DataFrame for merge
    #         temp_df = pd.DataFrame(
    #             list(data_values.items()), columns=["osm_id", data_name]
    #         )
    #         gdf = gdf.merge(temp_df, on="osm_id", how="left")
