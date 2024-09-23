""" Module for calculating exposures for paths."""

import json
from shapely.wkt import loads

from ..database_controller import DatabaseController
from ..exposure_analysing.exposure_db_controller import ExposureDbController

from ...src.config import (
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
    USER_ID_KEY,
)
from ...src.data_utilities import append_multilinestrings, combine_multilinestrings


class ExposuresCalculator:
    """
    Class for calculating exposures for paths.
    Single_path_results to keep track of single path results during calculating of all data source exposures.
    Batch_combined_path_results to keep track of all paths combined results in the batch.
    """

    def __init__(self):
        self.segment_cache = {}
        self.single_path_results = {}
        # all paths combined in the batch
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

    def _add_to_path_batch_results(self, path_results: dict) -> None:
        """
        Add the path results to the combined path results.

        Parameters
        ----------
        path_results : dict
            Path results.
        """
        self.batch_combined_path_results.append(path_results)

    def _get_new_osmids(self, path_osm_ids: list[str] | float) -> list[str]:
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
        # Check if path_osm_ids is a list and not NaN
        if isinstance(path_osm_ids, list):
            return [
                osm_id
                for osm_id in path_osm_ids
                if osm_id not in self.segment_cache.keys()
            ]
        # Handle cases where path_osm_ids is NaN or another non-iterable
        return []

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
            # add new key to existing segment
            if osm_id not in self.segment_cache.keys():
                continue
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

    def classify_and_accumulate(
        self,
        exposure: float | str,
        time: float,
        cumulative_values: dict,
        ranges_for_data: list[tuple[int, int]],
    ) -> dict:
        """
        Classify the exposure into the correct range and accumulate the time value.

        Parameters
        ----------
        exposure : float
            The exposure value to classify.
        time : float
            The time associated with the exposure.
        cumulative_values : dict
            Dictionary holding cumulative exposure values for each range.
        ranges_for_data : list[tuple[int, int]]
            List of exposure ranges (as tuples).

        Returns
        -------
        dict
            Updated cumulative values.
        """
        # Loop through each range and classify the exposure
        classified = False
        for lower_bound, upper_bound in ranges_for_data:
            if lower_bound <= float(exposure) <= upper_bound:
                cumulative_values[f"{lower_bound}-{upper_bound}"] += time
                classified = True
                break

        # If the exposure doesn't fit in any range, add to "other"
        if not classified:
            cumulative_values["other"] += time

        return cumulative_values

    def _calculate_cumulative_exposures(
        self,
        exposure_data_and_time_values: list[tuple],
        ranges_for_data: list[tuple[int, int]],
    ) -> dict:
        """
        Calculate cumulative exposures for the given data source.

        Parameters
        ----------
        exposure_data_and_time_values : list[tuple]
            List of tuples containing exposure data and time values.
        ranges_for_data : list[tuple[int, int]]
            List of ranges for the data source.

        Returns
        -------
        dict
            Cumulative exposures.
        """
        # Initialize cumulative values for each range
        cumulative_values = {f"{r[0]}-{r[1]}": 0 for r in ranges_for_data}
        cumulative_values["other"] = 0  # Handle out-of-range exposures

        # Accumulate values based on ranges
        for exposure, time in exposure_data_and_time_values:
            cumulative_values = self.classify_and_accumulate(
                exposure, time, cumulative_values, ranges_for_data
            )

        # Remove the "other" key if its value is zero
        if cumulative_values["other"] == 0:
            del cumulative_values["other"]

        return cumulative_values

    def calculate_and_save_path_exposures(
        self,
        user_id: str,
        path_segments: list[dict],
        data_names: list[str],
        route: dict,
        cumulative_ranges: list[tuple[int, int]],
        keep_geometries: bool = False,
        combine_geometries: bool = True,
    ):
        """
        Calculate the exposures for each exposure data source for path.
        Use the whole path times sum to calculate the average exposure.

        Parameters
        ----------
        path_segments : list[dict]
            List of segments.
        data_name : str
            Data name.
        """
        # all travel times and lengths from path segments
        total_times_sum = sum([item[TRAVEL_TIME_KEY] for item in path_segments])
        lengths_sum = sum([item[LENGTH_KEY] for item in path_segments])

        # save the metadata to the path result dict
        self._save_path_metadata_to_cache(
            user_id=user_id,
            route=route,
            path_segments=path_segments,
            keep_geometries=keep_geometries,
            times_sum=total_times_sum,
            lengths_sum=lengths_sum,
            combine_geometries=combine_geometries,
        )
        # loop through all the data sources, calculate exposures and save them to the path result dict
        for data_name in data_names:
            path_segments_copy = path_segments.copy()

            # filter out segments where the specific data is not found
            # so that the time-weighted results are correct and not skewed
            valid_segments = [
                item
                for item in path_segments_copy
                if item[data_name] is not None and item[data_name] != 0
            ]

            # Sum travel times and exposures only for valid segments
            # so drop all the times where there is no exposure data from the calculations as they skew average results
            valid_segments_times_sum = sum(
                [item[TRAVEL_TIME_KEY] for item in valid_segments]
            )

            # get exposure data and time values for the current data source being looped
            # only get the values where data is found
            exposure_data_and_time_values = [
                (item[data_name], item[TRAVEL_TIME_KEY]) for item in valid_segments
            ]

            # Extract exposures and lengths for the data source
            exposures = [
                float(exposure)
                for exposure, time in exposure_data_and_time_values
                if exposure is not None
            ]
            if not exposures:
                # If no exposures found for certain data source, skip the data source
                continue

            min_exposure = min(exposures)
            max_exposure = max(exposures)

            # Calculate the time-weighted sum and total length
            weighted_sum = sum(
                float(exposure) * time
                for exposure, time in exposure_data_and_time_values
            )

            # Calculate the time-weighted average exposure
            # use the total time sum to calculate the average exposure
            # this includes segments where data is not found, but gives more realistic average
            average_exposure = (
                weighted_sum / valid_segments_times_sum
                if valid_segments_times_sum != 0
                else -1
            )
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
                min_exposure=min_exposure,
                max_exposure=max_exposure,
                average_exposure=average_exposure,
                weighted_sum=weighted_sum,
                cumulative_exposures=cumulative_exposures,
            )

    def _save_path_metadata_to_cache(
        self,
        user_id: str,
        path_segments: list[dict],
        route: dict,
        keep_geometries: bool,
        times_sum: float,
        lengths_sum: float,
        combine_geometries: bool = True,
    ) -> None:
        """
        Save the path metadata to the cache.

        Parameters
        ----------
        route : dict
            Route dictionary.
        """
        self.single_path_results[FROM_ID_KEY] = route[FROM_ID_KEY]
        self.single_path_results[TO_ID_KEY] = route[TO_ID_KEY]
        self.single_path_results[USER_ID_KEY] = user_id
        self.single_path_results[TRAVEL_TIME_KEY] = round(times_sum, 2)
        self.single_path_results[LENGTH_KEY] = round(lengths_sum, 2)
        if keep_geometries:
            # get geometries and convert to shapely objects from WKT
            segment_geometries = [loads(item[GEOMETRY_KEY]) for item in path_segments]
            if combine_geometries:
                # propertly combine geometries by ordering them by proximity
                combined_geoms = combine_multilinestrings(segment_geometries)
            else:
                # append all the geometries to a single multilinestring
                # used for API where the geometries are not really used for visualization
                # and this is much faster than combining them properly
                combined_geoms = append_multilinestrings(segment_geometries)
            # convert geoms to WKT, for storing to sqlitesdb
            self.single_path_results[GEOMETRY_KEY] = combined_geoms.wkt

    def _save_path_exposure_to_cache(
        self,
        data_name: str,
        min_exposure: float,
        max_exposure: float,
        average_exposure: float,
        weighted_sum: float,
        cumulative_exposures: dict,
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

    def calculate_and_save_combined_path_exposures(
        self,
        user_id: str,
        path_osm_ids: list[str],
        data_names: list[str],
        route: dict,
        cumulative_ranges: list[tuple[int, int]],
        keep_geometries: bool = False,
        combine_geometries: bool = True,
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
            user_id=user_id,
            path_segments=path_segments,
            data_names=data_names,
            route=route,
            cumulative_ranges=cumulative_ranges,
            keep_geometries=keep_geometries,
            combine_geometries=combine_geometries,
        )
        # get and add current path results to the combined path results
        return self._get_single_path_results()

    def update_segment_cache_if_new_segments(
        self,
        db_handler: DatabaseController,
        exposure_db_controller: ExposureDbController,
        path_osm_ids: list[str],
    ):
        """Update the segment cache if new segments are found."""
        new_osm_ids = self._get_new_osmids(path_osm_ids)
        # fetch unvisited segments to cache
        new_path_segments = exposure_db_controller.fetch_unvisited_segments(
            db_handler, new_osm_ids
        )
        # update new segments to cache and fetch travel times
        if new_path_segments:
            # update the exposure calculator osmids cache
            self.update_segments_cache(new_path_segments)
            # fetch travel times for the new segments
            segments_travel_time = (
                exposure_db_controller.fetch_travel_times_for_segments(
                    db_handler, new_osm_ids
                )
            )
            # updata travel times to the exposure calculator osmids cache
            self.update_segments_cache_value(segments_travel_time, TRAVEL_TIME_KEY)
