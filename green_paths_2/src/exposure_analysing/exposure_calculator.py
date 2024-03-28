""" Class to handle exposure calculations. """

import numpy as np
from green_paths_2.src.config import OSM_IDS_DEFAULT_KEY
from green_paths_2.src.data_utilities import string_to_list

from green_paths_2.src.exposure_analysing.exposure_data_handlers import (
    combine_multilinestrings_to_single_linestring,
)
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.timer import time_logger

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


class ExposureCalculator:
    """Handle exposure calculations."""

    def __init__(
        self,
        routing_results: list[dict],
        segment_exposure_store: dict,
        osm_network_store: dict,
        data_names: list,
    ) -> None:
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

    # TODO: säädä tää funktion kuntoon -> modulaariseksi :D

    def _init_path_exposure_dict(self, path_data: dict) -> dict:
        """
        Construct almost empty frame for path exposure dict.

        Parameters
        ----------
        path_data : dict
            Path data.

        Returns
        -------
        dict
            Path exposure dict.
        """
        path_exposure_data: dict = {
            "from_id": path_data.get("from_id"),
            "to_id": path_data.get("to_id"),
            "length": {},
            "geometry": {},
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
        # print(self.segment_exposure_store)

        # all_keys_in_segment_exposure_store = self.segment_exposure_store.keys()
        # for key in all_keys_in_segment_exposure_store:
        #     values_for_key = self.segment_exposure_store.get(key)
        #     print("asdfasdfasdfasfasdf")
        #     print(osm_id in values_for_key.keys())
        #     return
        #     return osm_id in values_for_key.keys()

        try:
            path_exposure_update_data = {
                "length": {},
                "geometry": {},
            }

            # handle each data source
            for data_name in self.data_names:
                exposure_data_osm_id_dict = self.segment_exposure_store.get(
                    data_name, None
                )
                if (
                    not exposure_data_osm_id_dict
                    or not osm_id in exposure_data_osm_id_dict.keys()
                ):
                    # TODO: maybe remove this log?
                    # LOG.warning(f"No exposure data found for {data_name}.")
                    continue

                if osm_id in exposure_data_osm_id_dict.keys():
                    path_exposure_update_data[data_name] = {}
                    path_exposure_update_data[data_name][osm_id] = (
                        exposure_data_osm_id_dict.get(osm_id)
                    )
                    # print(f"exposure data: {exposure_data.get(osm_id)}")

            # TODO: add keys to confs

            # cast to int
            # osm_id = int(osm_id)

            # get length for osmid from exposure store
            length_of_segment = self.osm_network_store.get("length").get(osm_id)
            if length_of_segment:
                path_exposure_update_data["length"][osm_id] = length_of_segment
            # get geometry for osmid from exposure store
            osm_id_geometry = self.osm_network_store.get("geometry").get(osm_id)

            if osm_id_geometry:
                path_exposure_update_data["geometry"][osm_id] = osm_id_geometry

            return path_exposure_update_data
        except Exception as e:
            LOG.error(f"Error: {e}")
            raise ValueError(f"Error: {e}")

        # TODO: get travel time... -> OR DO WE NEED?!?!
        # travel_time = travel_times_store.get(osm_id)
        # path_exposure_data["travel_times"][osm_id] = travel_time

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

            path_exposure_data: dict = self._init_path_exposure_dict(path_data)

            path_data_osm_ids = path_data.get(OSM_IDS_DEFAULT_KEY, False)

            # no osm_ids found from path, skip
            if (
                not path_data_osm_ids
                or isinstance(path_data_osm_ids, float)
                or path_data_osm_ids == "'[]'"
                or path_data_osm_ids == "[]"
                or path_data_osm_ids == []
            ):
                # if path has no osm_ids or osms are invalid (e.g., float), skip
                LOG.warning(
                    f"No OSM ids in path or osms are float/nan, skipping. This probably means that no path was found"
                )
                continue

            if isinstance(path_data_osm_ids, str):
                # if osm_ids is a string, convert to list
                path_data_osm_ids = string_to_list(path_data_osm_ids)

            # invalid osm_ids found from path, skip
            if not path_data_osm_ids or not isinstance(path_data_osm_ids, list):
                # if path has no osm_ids or osms are invalid (e.g., float), skip
                LOG.warning(f"Osms are not list after list conversion, skipping.")
                continue

            # loop each osm_id in path
            for osm_id in path_data_osm_ids:
                # check that osm_id is valid, osm_id length should be at least 10, usually 14
                if not isinstance(osm_id, (int, str)) or len(osm_id) < 10:
                    continue

                # cast osm_id to int, should work if osm_id is valid e.g. string
                try:
                    # TODO: think if this is good approach?
                    if not isinstance(osm_id, int):
                        osm_id = int(osm_id)
                except:
                    LOG.error(f"Osmid {osm_id} is not valid, skipping.")
                    continue

                path_exposure_statistics = self._get_statistics_with_osm_id(osm_id)

                # add statistics from single osm_id to a path exposure data
                for key in path_exposure_statistics:
                    path_exposure_data[key].update(path_exposure_statistics[key])

            # after each path is processed, update master exposure list
            self.update_master_statistics_store(path_exposure_data)

        LOG.info("Finished constructing master exposure dict.")

    # TODO: laita funktioihin ja laita ne funktiot jonnekki järkevään ja laita avaimet confiin

    @time_logger
    def combine_all_path_statistics_to_master_combined_statistics_list(self) -> None:
        """
        Calculate path statistics.

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
        LOG.info("Combining path statistics.")

        od_keys = ["from_id", "to_id"]

        # print(self.get_master_statistics_store().items())
        # print("master statistics store")
        # return

        for path_exposure_data in self.get_master_statistics_store():
            print("single path datas")

            print(path_exposure_data)

            statistics_dict_per_path = {}

            for (
                path_attribute_key,
                path_attribute_values,
            ) in path_exposure_data.items():

                print("single path attribute values")
                print(path_attribute_key)
                print(path_attribute_values)

                if path_attribute_key in od_keys:
                    statistics_dict_per_path[path_attribute_key] = path_attribute_values
                    continue

                # init empty dict for each path data source
                # TODO: should these be empty dicts instead of None?
                if path_attribute_key in self.data_names:
                    statistics_dict_per_path[f"{path_attribute_key}_min_exposure"] = (
                        None
                    )
                    statistics_dict_per_path[f"{path_attribute_key}_max_exposure"] = (
                        None
                    )
                    statistics_dict_per_path[f"{path_attribute_key}_mean_exposure"] = (
                        None
                    )
                    statistics_dict_per_path[f"{path_attribute_key}_total_exposure"] = (
                        None
                    )
                else:
                    # init empty dict for other path data
                    statistics_dict_per_path[path_attribute_key] = {}

                if path_attribute_key == "length":
                    total_length = sum(path_attribute_values.values())
                    statistics_dict_per_path[path_attribute_key] = round(
                        total_length, 2
                    )

                if path_attribute_key == "geometry":
                    all_multiline_strings_list = list(path_attribute_values.values())
                    combined_geom_linestring = (
                        combine_multilinestrings_to_single_linestring(
                            all_multiline_strings_list
                        )
                    )
                    statistics_dict_per_path[path_attribute_key] = (
                        combined_geom_linestring
                    )

                if path_attribute_key in self.data_names:
                    exposure_values = path_attribute_values.values()
                    if exposure_values:
                        statistics_dict_per_path[
                            f"{path_attribute_key}_min_exposure"
                        ] = round(min(exposure_values), 2)
                        statistics_dict_per_path[
                            f"{path_attribute_key}_max_exposure"
                        ] = round(max(exposure_values), 2)

                        # TODO: tee painotettu missä kerrotaan pituudella tms. yms.

                        statistics_dict_per_path[
                            f"{path_attribute_key}_mean_exposure"
                        ] = round(sum(exposure_values) / len(exposure_values), 2)

                        statistics_dict_per_path[
                            f"{path_attribute_key}_total_exposure"
                        ] = round(sum(exposure_values), 2)

            # add to master combined list after each path loop
            self.update_master_combined_statistics_store(statistics_dict_per_path)

        LOG.info("Finished combining path statistics.")
