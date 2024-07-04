""" Module for calculating exposures for paths."""

import json
from shapely.wkt import loads

from green_paths_2.src.config import (
    CUMULATIVE_EXPOSURE_SECONDS_SUFFIX,
    FROM_ID_KEY,
    GEOMETRY_KEY,
    LENGTH_KEY,
    MAX_EXPOSURE_SUFFIX,
    MIN_EXPOSURE_SUFFIX,
    OSM_ID_KEY,
    OTHER_KEY,
    TO_ID_KEY,
    TRAVEL_TIME_KEY,
    TRAVERSAL_TIME_WEIGHTED_PATH_EXPOSURE_AVERAGE_SUFFIX,
    TRAVERSAL_TIME_WEIGHTED_PATH_EXPOSURE_SUM_SUFFIX,
)
from green_paths_2.src.data_utilities import combine_multilinestrings


class ExposuresCalculator:
    """Class for calculating exposures for paths."""

    def __init__(self):
        self.segment_cache = {}
        self.single_path_results = {}
        # batch
        self.batch_combined_path_results = []

    def clear_segment_cache(self) -> None:
        """Clear the segment cache."""
        self.segment_cache = {}

    def clear_single_path_results(self) -> None:
        """Clear the single path results."""
        self.single_path_results = {}

    def clear_batch_combined_path_results(self) -> None:
        """Clear the batch combined path results."""
        self.batch_combined_path_results = []

    def _get_single_path_results(self) -> dict:
        """
        Get the single path results.

        Returns
        -------
        dict
            Single path results.
        """
        return self.single_path_results

    def get_batch_combined_path_results(self) -> list[dict]:
        """
        Get the combined path results.

        Returns
        -------
        list[dict]
            Combined path results.
        """
        return self.batch_combined_path_results

    def _add_to_path_results(self, path_results: dict) -> None:
        """
        Add the path results to the combined path results.

        Parameters
        ----------
        path_results : dict
            Path results.
        """
        self.batch_combined_path_results.append(path_results)

    def _get_new_osmids(self, path_osm_ids: list[str]) -> list[str]:
        """
        Get the new OSM IDs that are not in the cache.

        Parameters
        ----------
        path_osm_ids : list[str]
            List of OSM IDs.

        Returns
        -------
        list[str]
            List of new OSM IDs.
        """
        return [
            osm_id for osm_id in path_osm_ids if osm_id not in self.segment_cache.keys()
        ]

    def update_segments_cache(self, path_segments: list[dict]) -> None:
        """
        Update the cache with the new segments, or update the existing segments with a new key.

        Parameters
        ----------
        path_segments : list[dict]
            List of segments.
        """
        for segment in path_segments:
            osm_id = segment[OSM_ID_KEY]
            # add new segment to cache, from routing results most likely
            self.segment_cache[osm_id] = segment

    def update_segments_cache_value(
        self, path_segments: list[dict], new_key=None
    ) -> None:
        """
        Update the cache with the new segments, or update the existing segments with a new key.

        Parameters
        ----------
        path_segments : list[dict]
            List of segments.
        new_key : str, optional
            New key to update the segments with. Defaults to None.
        """
        for segment in path_segments:
            osm_id = segment[OSM_ID_KEY]
            # add new key to existing segment, from travel times most likely
            if osm_id not in self.segment_cache.keys():
                continue
            # print(osm_id)
            # print("onkoooo")
            # print(osm_id in self.segment_cache.keys())
            self.segment_cache[osm_id][new_key] = segment[new_key]

    def _get_segments_from_cache(self, path_osm_ids: list[str]) -> list[dict]:
        """
        Get segments from cache.

        Parameters
        ----------
        path_osm_ids : list[str]
            List of OSM IDs.

        Returns
        -------
        list[dict]
            List of segments.
        """
        return [
            self.segment_cache[osmid]
            for osmid in path_osm_ids
            if osmid in self.segment_cache.keys()
        ]

    # Function to classify and accumulate values into ranges
    def classify_and_accumulate(
        self,
        exposure: float,
        time: float,
        cumulative_values: dict,
        ranges: list[tuple[int, int]],
    ):
        """
        Find out which range the exposure belongs to and accumulate the time.

        Parameters
        ----------
        exposure : float
            Exposure value.
        time : float
            Time value.
        cumulative_values : dict
            Cumulative values.
        ranges : list[tuple[int, int]]
            List of ranges.

        Returns
        -------
        dict
            Cumulative values.
        """
        added_to_range = False
        for r in ranges:
            min_range, max_range = r
            if min_range <= exposure < max_range:
                cumulative_values[f"{min_range}-{max_range}"] += time
                added_to_range = True
                break
        if not added_to_range:
            cumulative_values[OTHER_KEY] += time
        return cumulative_values

    def _calculate_cumulative_exposures(
        self,
        exposure_data_and_time_values: list[tuple],
        ranges_for_data: list[tuple[int, int]],
    ):
        """todo"""
        # Initialize cumulative values for each range
        cumulative_values = {f"{r[0]}-{r[1]}": 0 for r in ranges_for_data}
        cumulative_values[OTHER_KEY] = 0

        # Accumulate values based on ranges
        for exposure, time in exposure_data_and_time_values:
            cumulative_values = self.classify_and_accumulate(
                exposure, time, cumulative_values, ranges_for_data
            )

        # Remove the "other" key if its value is zero
        if cumulative_values[OTHER_KEY] == 0:
            del cumulative_values[OTHER_KEY]

        return cumulative_values

    def calculate_and_save_path_exposures(
        self,
        path_segments: list[dict],
        data_names: list[str],
        route: dict,
        cumulative_ranges: list[tuple[int, int]],
        keep_geometries: bool = False,
    ):
        """
        Calculate the exposures for each exposure data source for path.

        Parameters
        ----------
        path_segments : list[dict]
            List of segments.
        data_name : str
            Data name.
        """
        for data_name in data_names:
            exposure_data_and_time_values = [
                (item[data_name], item[TRAVEL_TIME_KEY])
                for item in path_segments
                if item[data_name] is not None
            ]

            # Extract exposures and lengths
            exposures = [t[0] for t in exposure_data_and_time_values]
            times = [t[1] for t in exposure_data_and_time_values]

            # Calculate max and min of exposures

            if not exposures:
                # If no exposures found for certain data source, skip the data source
                continue

            min_exposure = min(exposures)
            max_exposure = max(exposures)
            # Calculate the time-weighted sum and total length
            weighted_sum = sum(
                exposure * time for exposure, time in exposure_data_and_time_values
            )
            lengths_sum = sum([item[LENGTH_KEY] for item in path_segments])
            times_sum = sum(times)

            # Calculate the time-weighted average exposure
            average_exposure = weighted_sum / times_sum if times_sum != 0 else 0
            # get cumulative ranges for the current data source being looped
            if cumulative_ranges and hasattr(cumulative_ranges, data_name):
                ranges_for_data = getattr(cumulative_ranges, data_name)
                cumulative_exposures = self._calculate_cumulative_exposures(
                    exposure_data_and_time_values=exposure_data_and_time_values,
                    ranges_for_data=ranges_for_data,
                )
            else:
                cumulative_exposures = None

            # save the results to the path result dict
            # for each data source
            self._save_path_exposure_to_cache(
                data_name=data_name,
                route=route,
                path_segments=path_segments,
                min_exposure=min_exposure,
                max_exposure=max_exposure,
                average_exposure=average_exposure,
                weighted_sum=weighted_sum,
                times_sum=times_sum,
                lengths_sum=lengths_sum,
                cumulative_exposures=cumulative_exposures,
                keep_geometries=keep_geometries,
            )

    def _save_path_exposure_to_cache(
        self,
        data_name: str,
        route: dict,
        path_segments: list[dict],
        min_exposure: float,
        max_exposure: float,
        average_exposure: float,
        weighted_sum: float,
        times_sum: float,
        lengths_sum: float,
        cumulative_exposures: dict,
        keep_geometries: bool = False,
    ) -> None:
        """
        Save the path exposure results for exposure data source to the cache.
        Also save general to_, from_id and geometry to the result dict.

        Parameters
        ----------
        data_name : str
            Data name.
        route : dict
            Route dictionary.
        path_segments : list[dict]
            List of segments.
        max_exposure : float
            Maximum exposure.
        min_exposure : float
            Minimum exposure.
        average_exposure : float
            Average exposure.
        time_weighted_sum : float
            Time-weighted sum.
        times_sum : float
            Sum of times.
        lengths_sum : float
            Sum of lengths.
        cumulative_exposures : dict
            Cumulative exposures.
        """
        # kinda workaround to save generic items to dict, should make better
        if FROM_ID_KEY not in self.single_path_results.keys():
            self.single_path_results[FROM_ID_KEY] = route[FROM_ID_KEY]
        if TO_ID_KEY not in self.single_path_results.keys():
            self.single_path_results[TO_ID_KEY] = route[TO_ID_KEY]
        if GEOMETRY_KEY not in self.single_path_results.keys() and keep_geometries:
            # get geometries and convert to shapely objects from WKT
            segment_geometries = [loads(item[GEOMETRY_KEY]) for item in path_segments]
            # save geometry to the result dict
            combined_geoms = combine_multilinestrings(segment_geometries)
            # convert geoms to WKT, for storing to sqlitesdb
            self.single_path_results[GEOMETRY_KEY] = combined_geoms.wkt
        if TRAVEL_TIME_KEY not in self.single_path_results.keys():
            self.single_path_results[TRAVEL_TIME_KEY] = round(times_sum, 2)
        if LENGTH_KEY not in self.single_path_results.keys():
            self.single_path_results[LENGTH_KEY] = round(lengths_sum, 2)

        # save all the results to the path result dict
        self.single_path_results[f"{data_name}{MAX_EXPOSURE_SUFFIX}"] = round(
            max_exposure, 2
        )
        self.single_path_results[f"{data_name}{MIN_EXPOSURE_SUFFIX}"] = round(
            min_exposure, 2
        )
        self.single_path_results[
            f"{data_name}{TRAVERSAL_TIME_WEIGHTED_PATH_EXPOSURE_AVERAGE_SUFFIX}"
        ] = round(average_exposure, 2)
        self.single_path_results[
            f"{data_name}{TRAVERSAL_TIME_WEIGHTED_PATH_EXPOSURE_SUM_SUFFIX}"
        ] = round(weighted_sum, 2)
        # handle cumulative exposures if they exist
        if cumulative_exposures:
            cumulative_key = f"{data_name}{CUMULATIVE_EXPOSURE_SECONDS_SUFFIX}"
            # Serialize to JSON string in order to store to sqlite db
            self.single_path_results[cumulative_key] = json.dumps(cumulative_exposures)

    def calculate_combined_path_exposures(
        self,
        path_osm_ids: list[str],
        data_names: list[str],
        route: dict,
        cumulative_ranges: list[tuple[int, int]],
        keep_geometries: bool = False,
    ) -> None:
        """
        Calculate the aggregated and combined path exposures.

        Parameters
        ----------
        path_osm_ids : list[str]
            List of OSM IDs.
        data_names : list[str]
            List of data names.
        route : dict
            Route dictionary.
        cumulative_ranges : list[tuple[int, int]]
            List of cumulative ranges.
        """
        path_segments = self._get_segments_from_cache(path_osm_ids)
        self.calculate_and_save_path_exposures(
            path_segments=path_segments,
            data_names=data_names,
            route=route,
            cumulative_ranges=cumulative_ranges,
            keep_geometries=keep_geometries,
        )
        # get and add current path results to the combined path results
        path_combined = self._get_single_path_results()
        self._add_to_path_results(path_combined)
