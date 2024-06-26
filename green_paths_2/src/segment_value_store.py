""" Store for segment values. """

import pandas as pd
import geopandas as gpd
from .config import (
    DATA_COVERAGE_SAFETY_PERCENTAGE,
    GEOMETRY_KEY,
    LENGTH_KEY,
    NORMALIZED_DATA_SUFFIX,
    OSM_ID_KEY,
    SEGMENT_VALUES_ROUND_DECIMALS,
)

from .green_paths_exceptions import (
    DataManagingError,
    SegmentValueStoreError,
)
from .logging import setup_logger, LoggerColors
from .preprocessing.data_source import DataSource


LOG = setup_logger(__name__, LoggerColors.RED.value)


class SegmentValueStore:

    def __init__(self):
        self.master_segment_store: dict[str, dict[str, float]] = {}
        self.master_segment_gdf: gpd.GeoDataFrame = gpd.GeoDataFrame()

    def get_store(self) -> dict[str, dict[str, float]]:
        return self.master_segment_store

    def set_store(self, master_segment_store: dict[str, dict[str, float]]):
        self.master_segment_store = master_segment_store

    def get_all_store_data_keys(self) -> list[str]:
        return list(self.master_segment_store.values())[0].keys()

    def get_master_segment_gdf(self) -> gpd.GeoDataFrame:
        return self.master_segment_gdf

    def set_master_segment_gdf(self, master_segment_gdf: gpd.GeoDataFrame):
        self.master_segment_gdf = master_segment_gdf

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

    def remove_all_rows_without_exposure_data(
        self, segment_store_gdf: gpd.GeoDataFrame
    ) -> gpd.GeoDataFrame:
        data_keys = self.get_all_store_data_keys()

        # remote all data_key (column) rows without data or with NaN or False
        for data_key in data_keys:
            segment_store_gdf = segment_store_gdf[
                segment_store_gdf[data_key].notna() & segment_store_gdf[data_key]
            ]
        return segment_store_gdf

    def combine_exposures_to_geometries_and_lenghts(
        self,
        osm_network_gdf: gpd.GeoDataFrame,
    ) -> None:
        """Add geometries to segment store from OSM network GeoDataFrame."""
        LOG.info("Combining exposures to geometries to master_segment_gdf.")
        try:
            exposure_dict = self.get_store()
            # set network_gdf index to osm_id
            osm_network_gdf = osm_network_gdf.set_index(OSM_ID_KEY)
            for osm_id, _ in exposure_dict.items():
                # set value "osm_id" to the exposure_dict with the key osm_id
                exposure_dict[osm_id][OSM_ID_KEY] = osm_id
                # set value "geometry" to the exposure_dict with the key osm_id
                exposure_dict[osm_id][GEOMETRY_KEY] = osm_network_gdf.loc[
                    osm_id, GEOMETRY_KEY
                ]
                exposure_dict[osm_id][LENGTH_KEY] = osm_network_gdf.loc[
                    osm_id, LENGTH_KEY
                ]

            self.set_store(exposure_dict)
        except SegmentValueStoreError as e:
            LOG.error(f"Error combining exposures to geometries: {e}")
            return False

    # TODO: Do we want to crash?
    def validate_data_coverage(
        self,
        data_sources: list[DataSource],
        osm_network_segment_count: int,
        datas_coverage_safety_limit: int | float,
    ) -> None:
        """Validate that the data covers the entire network."""
        for data_name, _ in data_sources.items():
            data_items_found = len(self.master_segment_store)
            # loop through the master segment store and check if the data is found by data_name as key in datasource items
            # get the length of the data found
            data_found_count = 0
            for _, data in self.master_segment_store.items():
                if data_name in data.keys():
                    data_found_count += 1

            data_coverage_percentage = round(
                (data_found_count / osm_network_segment_count) * 100, 2
            )

            LOG.info(
                f"Data coverage (data/segments) for {data_name} is: {data_found_count}/{osm_network_segment_count} = {data_coverage_percentage}%."
            )
            # TODO -> should we crash of fail here if too low %???

            if data_coverage_percentage < datas_coverage_safety_limit:
                LOG.error(
                    f"ERROR: Data coverage for {data_name} is less than safety limit: {datas_coverage_safety_limit}%."
                )
                LOG.error(
                    f"Data coverage for {data_name} is: {data_coverage_percentage}%."
                )
                LOG.error(
                    f"Safety limit is needed that we can be sure that the GP2 routes are actually using exposure datas."
                )
                LOG.error(
                    f"Modify the safety limit if needed in the user configurations. The default from GP2 config is {DATA_COVERAGE_SAFETY_PERCENTAGE}"
                )
                raise DataManagingError(
                    f"Data coverage for {data_name} is less than safety limit: {datas_coverage_safety_limit}%."
                )

    def validate_user_min_max_values(self, data_sources: list[DataSource]) -> None:
        """Validate user defined min and max values."""
        values_not_in_range = []
        data_values_not_in_range = []
        for data_key, data_source in data_sources.items():
            for osm_id, data in self.master_segment_store.items():
                if data_key in data:
                    if (
                        data[data_key] < data_source.min_data_value
                        or data[data_key] > data_source.max_data_value
                    ):
                        values_not_in_range.append(f"{osm_id}: {data[data_key]}")
                        data_values_not_in_range.append(data[data_key])
        if values_not_in_range:
            LOG.warning(
                f"WARNING: {len(values_not_in_range)} values are not within the user defined min and max values, for data {data_key}. Values not in range max: {max(data_values_not_in_range)}, min : {min(data_values_not_in_range)}. They will be fitted to the user defined min and max values."
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
            normalized_data_key = f"{data_key}{NORMALIZED_DATA_SUFFIX}"
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
        - data_good_exposure:
            If True, good exposure is considered as negative values, which makes the traversing cost smaller.
            If False, good exposure is considered as positive values, which makes the traversing cost larger.
            So negative values mean that the segment is bad for traversing and should be avoided, and vice versa.
        - min_data_value: The minimum value of the data source.
        - max_data_value: The maximum value of the data source.


        Returns:
        - Dictionary with the OSM IDs as keys and the normalised values as values.
        """
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

                if data_good_exposure:
                    normalized_value = -normalized_value

                # Round and store to store
                normalized_values[osm_id] = round(
                    normalized_value, SEGMENT_VALUES_ROUND_DECIMALS
                )

        return normalized_values

    def convert_segment_store_to_gdf(self) -> None:
        """
        Convert segment store to GeoDataFrame.

        Returns:
        - GeoDataFrame with segment geometries and values.
        """
        try:
            segment_store = self.get_store()
            # Convert segment store to DataFrame
            df = pd.DataFrame.from_dict(segment_store, orient="index")
            # handle geometry if gdf has geometry
            if "geometry" in df.columns:
                # Convert geometry column to GeoSeries
                geometries = gpd.GeoSeries(df.pop("geometry"))
                # Convert DataFrame to GeoDataFrame
                gdf = gpd.GeoDataFrame(df, geometry=geometries)
            else:
                gdf = gpd.GeoDataFrame(df)
            self.set_master_segment_gdf(gdf)
        except SegmentValueStoreError as e:
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
        except SegmentValueStoreError as e:
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
