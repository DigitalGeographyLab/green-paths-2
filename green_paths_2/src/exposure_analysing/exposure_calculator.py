""" Class to handle exposure calculations. """

import numpy as np
from green_paths_2.src.config import (
    CUMULATIVE_EXPOSURE_LENGTH_METERS_SUFFIX,
    FROM_ID_KEY,
    GEOMETRY_KEY,
    LENGHT_WEIGHTED_TOTAL_EXPOSURE_SUFFIX,
    LENGTH_KEY,
    MAX_EXPOSURE_SUFFIX,
    MIN_EXPOSURE_SUFFIX,
    ORIGIN_DESTINATION_KEYS,
    OSM_IDS_KEY,
    SUM_EXPOSURE_SUFFIX,
    TO_ID_KEY,
)
from green_paths_2.src.data_utilities import string_to_list

from green_paths_2.src.exposure_analysing.exposure_data_handlers import (
    combine_multilinestrings_to_single_linestring,
)
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.preprocessing.user_config_parser import UserConfig
from green_paths_2.src.timer import time_logger

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


class ExposureCalculator:
    """Handle exposure calculations."""

    def __init__(
        self,
        user_config: UserConfig,
        routing_results: list[dict],
        segment_exposure_store: dict,
        osm_network_store: dict,
        data_names: list,
    ) -> None:
        self.user_config = user_config
        self.routing_results = routing_results
        self.segment_exposure_store = segment_exposure_store
        self.osm_network_store = osm_network_store
        self.data_names = data_names
        self.master_statistics_store = []
        self.master_combined_statistics_store = []

    def get_master_statistics_store(self) -> []:
        """Return master statistics store dict."""
        return self.master_statistics_store

    def set_master_statistics_store(self, master_statistics_store: list) -> None:
        """Set master statistics store dict."""
        self.master_statistics_store = master_statistics_store

    def update_master_statistics_store(self, path_exposure_data: list) -> None:
        """Update master statistics store dict."""
        self.master_statistics_store.append(path_exposure_data)

    def get_master_combined_statistics_store(self) -> list:
        """Return master combined statistics list."""
        return self.master_combined_statistics_store

    def set_master_combined_statistics_store(
        self, master_combined_statistics_store: list
    ) -> None:
        """Set master combined statistics list."""
        self.master_combined_statistics_store = master_combined_statistics_store

    def update_master_combined_statistics_store(self, path_statistics: dict) -> None:
        """Update master combined statistics list."""
        self.master_combined_statistics_store.append(path_statistics)

    def _init_path_exposure_dict(self, path_data: dict) -> dict:
        """
        Construct initial path exposure dict.

        Parameters
        ----------
        path_data : dict
            Path data.

        Returns
        -------
        dict
            Path exposure dict.
        """
        if self.user_config.analysing and self.user_config.analysing.keep_geometry:
            path_exposure_data: dict = {
                FROM_ID_KEY: path_data.get(FROM_ID_KEY),
                TO_ID_KEY: path_data.get(TO_ID_KEY),
                LENGTH_KEY: {},
                GEOMETRY_KEY: {},
            }
        else:
            path_exposure_data: dict = {
                FROM_ID_KEY: path_data.get(FROM_ID_KEY),
                TO_ID_KEY: path_data.get(TO_ID_KEY),
                LENGTH_KEY: {},
                # "travel_times": {},
            }

        # init all datas to empty dict
        for data_name in self.data_names:
            path_exposure_data[data_name] = {}

        return path_exposure_data

    def _get_statistics_with_osm_id(self, osm_id: int) -> dict:
        """
        Get statistics for each osm_id from exposure store.

        Parameters
        ----------
        osm_id : int
            Osm id.

        Returns
        -------
        dict
            exposure update data for each osm_id.
        """

        if self.user_config.analysing and self.user_config.analysing.keep_geometry:
            path_exposure_update_data = {
                LENGTH_KEY: {},
                GEOMETRY_KEY: {},
            }
        else:
            path_exposure_update_data = {
                LENGTH_KEY: {},
            }

        # handle each data source
        for data_name in self.data_names:
            exposure_data_osm_id_dict = self.segment_exposure_store.get(data_name, None)
            # if no exposure data found for data source, skip
            if (
                not exposure_data_osm_id_dict
                or not osm_id in exposure_data_osm_id_dict.keys()
            ):
                continue

            if osm_id in exposure_data_osm_id_dict.keys():
                path_exposure_update_data[data_name] = {}
                path_exposure_update_data[data_name][osm_id] = (
                    exposure_data_osm_id_dict.get(osm_id)
                )

        # get length for osmid from exposure store
        length_of_segment = self.osm_network_store.get(LENGTH_KEY).get(osm_id)
        if length_of_segment:
            path_exposure_update_data[LENGTH_KEY][osm_id] = length_of_segment
        # get geometry for osmid from exposure store
        osm_network_geometry = self.osm_network_store.get(GEOMETRY_KEY)
        if osm_network_geometry:
            osm_id_geometry = osm_network_geometry.get(osm_id)
            if osm_id_geometry:
                path_exposure_update_data[GEOMETRY_KEY][osm_id] = osm_id_geometry

        return path_exposure_update_data

        # TODO: get travel time... -> do we need?
        # travel_time = travel_times_store.get(osm_id)
        # path_exposure_data["travel_times"][osm_id] = travel_time

    def _validate_and_convert_osmids(self, path_data_osm_ids: list | str) -> list[int]:
        """
        Validate and convert osm_ids from path data.

        Parameters
        ----------
        path_data_osm_ids : list | str
            Path data osm ids.

        Returns
        -------
        list
            Valid osm ids.
        """
        # no osm_ids found from path
        if (
            not path_data_osm_ids
            or isinstance(path_data_osm_ids, float)
            or path_data_osm_ids == "'[]'"
            or path_data_osm_ids == "[]"
            or path_data_osm_ids == []
        ):
            return False

        # convert osm_ids to list if they are string
        if isinstance(path_data_osm_ids, str):
            path_data_osm_ids = string_to_list(path_data_osm_ids)

        # if still not list, try force conversion
        # this might happen if list are java.util.ArrayList
        if not isinstance(path_data_osm_ids, list):
            path_data_osm_ids = list(path_data_osm_ids)

        # invalid osm_ids found from path, skip
        if not path_data_osm_ids or not isinstance(path_data_osm_ids, list):
            return False

        return path_data_osm_ids

    def _process_path_statistics(
        self,
        path_exposure_data: dict,
        osm_ids: list[int],
    ):
        # loop each osm_id in path
        for osm_id in osm_ids:
            # cast osm_id to int, should work if osm_id is valid e.g. string or Java Float
            try:
                if not isinstance(osm_id, int):
                    osm_id = int(osm_id)
            except:
                LOG.error(f"Osmid {osm_id} is not valid for casting to int, skipping.")
                return False

            if not isinstance(osm_id, int) or len(str(osm_id)) < 10:
                LOG.error(f"Osmid {osm_id} is not valid, skipping.")
                return False

            path_exposure_statistics = self._get_statistics_with_osm_id(osm_id)

            # add statistics from single osm_id to a path exposure data
            for key in path_exposure_statistics:
                path_exposure_data[key].update(path_exposure_statistics[key])

        return path_exposure_data

    @time_logger
    def construct_master_statistics_dict(self) -> None:
        """
        Construct exposure dict from routing results and exposure store.

        Returns
        -------
        dict
            Master statistics dict.
        """
        LOG.info("Starting to construct master exposure dict.")

        if not self.routing_results:
            raise ValueError("No routing results found.")

        for path_data in self.routing_results:

            path_exposure_data = self._init_path_exposure_dict(path_data)
            path_data_osm_ids = path_data.get(OSM_IDS_KEY, False)
            valid_osm_ids = self._validate_and_convert_osmids(path_data_osm_ids)

            if not valid_osm_ids:
                # if path has no osm_ids or osms are invalid (e.g., float), skip
                LOG.warning(
                    f"No OSM ids in path or osms are not valid after conversions, skipping."
                )
                continue

            path_statistics = self._process_path_statistics(
                path_exposure_data=path_exposure_data, osm_ids=valid_osm_ids
            )

            # after each path is processed, update master exposure list
            self.update_master_statistics_store(path_statistics)

        LOG.info("Finished constructing master exposure dict.")

    def _init_keys_for_path_exposure_dict(
        self,
        path_attribute_key: str,
        path_attribute_values: dict,
        statistics_dict_per_path: dict,
    ) -> dict:
        """
        Initialize keys for path exposure dict.

        Parameters
        ----------
        path_exposure_data : dict
            Path exposure data.

        Returns
        -------
        dict
            Path exposure data.
        """
        if path_attribute_key in ORIGIN_DESTINATION_KEYS:
            statistics_dict_per_path[path_attribute_key] = path_attribute_values
            return statistics_dict_per_path, True

        if path_attribute_key in self.data_names:
            statistics_dict_per_path[f"{path_attribute_key}{MIN_EXPOSURE_SUFFIX}"] = (
                None
            )
            statistics_dict_per_path[f"{path_attribute_key}{MAX_EXPOSURE_SUFFIX}"] = (
                None
            )
            statistics_dict_per_path[f"{path_attribute_key}{SUM_EXPOSURE_SUFFIX}"] = (
                None
            )
            statistics_dict_per_path[
                f"{path_attribute_key}{LENGHT_WEIGHTED_TOTAL_EXPOSURE_SUFFIX}"
            ] = None
            statistics_dict_per_path[
                f"{path_attribute_key}{CUMULATIVE_EXPOSURE_LENGTH_METERS_SUFFIX}"
            ] = None
        else:
            # init empty dict for other path data
            statistics_dict_per_path[path_attribute_key] = {}
        return statistics_dict_per_path, False

    def _calculate_length_for_path(
        self,
        path_attribute_key: str,
        path_attribute_values: dict,
    ) -> dict:
        """
        Calculate combined length for path. Return tuple with key and value.

        Parameters
        ----------
        path_attribute_key : str
            Path attribute key.
        path_attribute_values : dict
            Path attribute values.

        Returns
        -------
        list
            Tuple with key and value.

        """
        return [(path_attribute_key, round(sum(path_attribute_values.values()), 2))]

    def _calculate_geometry_for_path(
        self,
        path_attribute_key: str,
        path_attribute_values: dict,
    ) -> dict:
        """
        Combine all geometries to one for path. Return tuple with key and value.

        Parameters
        ----------
        path_attribute_key : str
            Path attribute key.
        path_attribute_values : dict
            Path attribute values.

        Returns
        -------
        list
            Tuple with key and value.
        """
        all_multiline_strings_list = list(path_attribute_values.values())
        combined_geom_linestring = combine_multilinestrings_to_single_linestring(
            all_multiline_strings_list
        )
        return [(path_attribute_key, combined_geom_linestring)]

    def _calculate_length_weighted_total_exposure(
        self, exposure_values: dict, path_lengths: dict
    ) -> float:
        """
        Calculate length weighted total exposure.
        Sum of all exposures multiplied by length of each segment
        divided by total length of path.

        Parameters
        ----------
        exposure_values : list
            Exposure values.
        path_lengths : dict
            Path lengths.

        Returns
        -------
        float
            Length weighted total exposure.
        """
        total_weighted_exposure = 0.0
        for osm_id, exposure_value in exposure_values.items():
            length_for_osmid = path_lengths.get(osm_id)
            if not length_for_osmid:
                continue
            weighted_exposure = exposure_value * length_for_osmid
            total_weighted_exposure += weighted_exposure

        total_lenght = sum(path_lengths.values())
        total_weighted_exposure = total_weighted_exposure / total_lenght
        return total_weighted_exposure

    def find_range(self, value: float, ranges: list[int, float]) -> str:
        """Find range for value from ranges."""
        for r in ranges:
            start, end = r
            if start <= value <= end:
                return f"{start}-{end}"
        return None

    def _calculate_cumulative_exposure_lengths(
        self, attribute_key: str, exposure_values: dict, path_lengths: dict
    ) -> dict:
        """
        Calculate cumulative exposure lengths.
        If ranges are set for the data source, use ranges as keys for cumulative exposure lengths.
        If no ranges are set or the exposure values isn't between any range,
        use exposure values as keys for cumulative exposure lengths.

        Parameters
        ----------
        exposure_values : dict
            Exposure values.

        path_lengths : dict
            Path lengths.

        Returns
        -------
        dict
            Cumulative exposure lengths.
        """
        # use exposure values as keys and distances as values
        cumulative_exposure_lengths = {}
        for osm_id, exposure_value in exposure_values.items():
            # use single decimal for exposure values
            rounded_exposure_value = round(exposure_value, 1)
            length_for_osmid = path_lengths.get(osm_id)
            if not length_for_osmid:
                continue

            if (
                self.user_config.analysing
                and self.user_config.analysing.cumulative_ranges
            ):
                # if cumulative ranges are set for the data source
                # use ranges as keys for cumulative exposure lengths
                if hasattr(self.user_config.analysing.cumulative_ranges, attribute_key):
                    ranges_for_data = getattr(
                        self.user_config.analysing.cumulative_ranges, attribute_key
                    )

                    target_range_for_exposure = self.find_range(
                        rounded_exposure_value, ranges_for_data
                    )

                    if target_range_for_exposure:
                        if target_range_for_exposure in cumulative_exposure_lengths:
                            cumulative_exposure_lengths[
                                target_range_for_exposure
                            ] += length_for_osmid
                        else:
                            cumulative_exposure_lengths[target_range_for_exposure] = (
                                length_for_osmid
                            )
                        # next exposure value
                        continue

            # fall back to use exposure values as keys for cumulative exposure lengths
            # no ranges for cumulative values set or value not between ranges,
            # use exposure values as keys
            if rounded_exposure_value in cumulative_exposure_lengths:
                cumulative_exposure_lengths[rounded_exposure_value] += length_for_osmid
            else:
                cumulative_exposure_lengths[rounded_exposure_value] = length_for_osmid

        # round all values to 1 decimals
        cumulative_exposure_lengths = {
            exposure_key: round(length, 1)
            for exposure_key, length in cumulative_exposure_lengths.items()
        }
        return cumulative_exposure_lengths

    def _calculate_exposure_values_for_path(
        self,
        path_attribute_key: str,
        path_attribute_values: dict,
        path_lengths: dict,
    ) -> list:
        """
        Calculate exposure values for path. Return list of tuples with key and value.

        Parameters
        ----------
        path_attribute_key : str
            Path attribute key.
        path_attribute_values : dict
            Path attribute values.
        statistics_dict_per_path : dict
            Statistics dict per path.

        Returns
        -------
        list
            List of tuples with key and value.
        """
        attribute_key_values = []
        exposure_values = path_attribute_values.values()
        if exposure_values:

            attribute_key_values.append(
                (
                    f"{path_attribute_key}{MIN_EXPOSURE_SUFFIX}",
                    round(min(exposure_values), 2),
                )
            )

            attribute_key_values.append(
                (
                    f"{path_attribute_key}{MAX_EXPOSURE_SUFFIX}",
                    round(max(exposure_values), 2),
                )
            )

            attribute_key_values.append(
                (
                    f"{path_attribute_key}{SUM_EXPOSURE_SUFFIX}",
                    round(sum(exposure_values), 2),
                )
            )

            weighted_exposure_total = self._calculate_length_weighted_total_exposure(
                path_attribute_values,
                path_lengths,
            )

            attribute_key_values.append(
                (
                    f"{path_attribute_key}{LENGHT_WEIGHTED_TOTAL_EXPOSURE_SUFFIX}",
                    round(weighted_exposure_total, 2),
                )
            )

            # calculate cumulative sum of exposure values by using exposure values as keys and distances as values

            cumulative_exposure_lengths = self._calculate_cumulative_exposure_lengths(
                path_attribute_key,
                path_attribute_values,
                path_lengths,
            )
            attribute_key_values.append(
                (
                    f"{path_attribute_key}{CUMULATIVE_EXPOSURE_LENGTH_METERS_SUFFIX}",
                    cumulative_exposure_lengths,
                )
            )

        return attribute_key_values

    def _process_path_attribute(
        self,
        path_exposure_data,
        path_attribute_key,
        path_attribute_values,
        statistics_dict_per_path,
    ) -> dict:
        """
        Process path attribute. Get key value pairs for statistics dict per path.

        Parameters
        ----------
        path_exposure_data : dict
            Path exposure data.
        path_attribute_key : str
            Path attribute key.
        path_attribute_values : dict
            Path attribute values.
        statistics_dict_per_path : dict
            Statistics dict per path.

        Returns
        -------
        dict
            Statistics dict per path.
        """

        attribute_key_values = []

        if path_attribute_key == LENGTH_KEY:
            attribute_key_values = self._calculate_length_for_path(
                path_attribute_key,
                path_attribute_values,
            )

        elif path_attribute_key == GEOMETRY_KEY:
            attribute_key_values = self._calculate_geometry_for_path(
                path_attribute_key,
                path_attribute_values,
            )

        elif path_attribute_key in self.data_names:
            # remove possible nan values from path attribute values
            # osm_ids can get nan values especially when running piplines with multiple data sources
            # where the all segments dont have data for for all data sources
            path_attribute_values = {
                k: v for k, v in path_attribute_values.items() if not np.isnan(v)
            }

            path_lengths = path_exposure_data.get(LENGTH_KEY)
            # print(statistics_dict_per_path)
            attribute_key_values = self._calculate_exposure_values_for_path(
                path_attribute_key,
                path_attribute_values,
                path_lengths,
            )

        # add key value pairs to statistics dict
        for attribute_key, attribute_value in attribute_key_values:
            statistics_dict_per_path[attribute_key] = attribute_value

        return statistics_dict_per_path

    @time_logger
    def calculate_and_combine_paths_statistics(self) -> None:
        """
        Calculate and combine path statistics for all paths.

        Parameters
        ----------
        path_key : str
            Path key.
        path_exposures : dict
            Path exposures.

        Returns
        -------
        dict
            Path statistics.
        """
        LOG.info("Combining paths statistics.")

        for path_exposure_data in self.get_master_statistics_store():
            # init empty dict for each path
            path_statistics = {}

            # loop through all the path attributes keys and values
            for (
                path_attribute_key,
                path_attribute_values,
            ) in path_exposure_data.items():

                # add keys to statistics dict
                path_statistics, is_od_key = self._init_keys_for_path_exposure_dict(
                    path_attribute_key,
                    path_attribute_values,
                    path_statistics,
                )

                # if current key is origin or destination, skip other calculations
                if is_od_key:
                    continue

                # update path
                path_statistics.update(
                    self._process_path_attribute(
                        path_exposure_data,
                        path_attribute_key,
                        path_attribute_values,
                        path_statistics,
                    )
                )

            # add to master combined list after each whole path is processed
            self.update_master_combined_statistics_store(path_statistics)

        LOG.info("Finished combining path statistics.")
