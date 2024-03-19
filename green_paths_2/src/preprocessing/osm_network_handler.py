""" For dealing with OSM network related operations. """

import geopandas as gpd
from pyrosm import OSM
import osmium

from green_paths_2.src.config import (
    GENERAL_ID_DEFAULT_KEY,
    NETWORK_COLUMNS_TO_KEEP,
    OSM_ID_DEFAULT_KEY,
    SEGMENT_SAMPLING_POINTS_KEY,
)
from green_paths_2.src.data_utilities import (
    filter_gdf_by_columns_if_found,
    rename_gdf_column,
)
from green_paths_2.src.logging import setup_logger
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.timer import time_logger


from green_paths_2.src.preprocessing.spatial_operations import (
    has_invalid_geometries,
    fix_invalid_geometries,
    handle_gdf_crs,
)


LOG = setup_logger(__name__, LoggerColors.BLUE.value)


# TODO: remove this :D
ROOPE_DEVELOPMENT = False


class OsmNetworkHandler:
    def __init__(self, osm_pbf_file=None):
        self.osm_pbf_file: str = osm_pbf_file
        self.network_gdf: gpd.GeoDataFrame = None

    def get_osm_pbf_file_path(self) -> str:
        return self.osm_pbf_file

    def get_network_gdf(self) -> gpd.GeoDataFrame:
        return self.network_gdf

    def set_network_gdf(self, network_gdf: gpd.GeoDataFrame) -> None:
        self.network_gdf = network_gdf

    def set_geometry_column(self, column_name: str) -> None:
        self.network_gdf.set_geometry(column_name, inplace=True)

    def rename_column(self, old_name: str, new_name: str) -> None:
        self.network_gdf = rename_gdf_column(
            self.network_gdf,
            old_column_name=old_name,
            new_column_name=new_name,
        )

    @time_logger
    def convert_network_to_gdf(self) -> None:
        """Converts the OSM network to a GeoDataFrame."""
        LOG.info("converting OSM network to gdf")
        osm_network = OSM(self.osm_pbf_file)
        # TODO:  -> laita tää ottamaan vaa esim pyöräiltävät tai käveltävät tms.? -> ei vältsii ettei lähe liikaa kamaa pois?
        network_gdf = osm_network.get_network(network_type="all")
        LOG.info("successfully converted OSM network to gdf")
        LOG.info(f"network gdf size: {len(network_gdf)}")
        self.network_gdf = network_gdf

    def handle_crs(self, project_crs, original_crs) -> None:
        """Sets the CRS for the network GeoDataFrame."""
        LOG.info("Handle network CRS")
        self.network_gdf = handle_gdf_crs(
            "network",
            self.network_gdf,
            target_crs=project_crs,
            original_crs=original_crs,
        )

    def handle_invalid_geometries(self) -> None:
        """Handles invalid geometries in the network GeoDataFrame."""
        LOG.info("Handle invalid geometries")
        invalid_geometries = has_invalid_geometries(self.network_gdf, "network")
        if invalid_geometries:
            # TODO: laita conffeihi toi flagi!
            self.network_gdf = fix_invalid_geometries(
                self.network_gdf, remove_invalid=True
            )

    def network_filter_by_columns(self, columns: list[str]) -> None:
        """
        Filters the network GeoDataFrame by the given columns.
        Drops all other columns.
        ::param columns: List of column names.
        """
        self.network_gdf = filter_gdf_by_columns_if_found(
            self.network_gdf, columns, keep=True
        )

    def convert_gdf_geometry_to_wkt(
        self, current_column_name: str, target_column_name: str
    ) -> None:
        """
        Converts the active geometry column to WKT and stores it in a new column.
        This is needed for storing multiple/original geometry in gdf,
        (optional cache) GeoPackage only supports one geometry column.
        ::param current_column_name: Name of the current geometry column.
        ::param target_column_name: Name of the new column that will store the WKT geometry.
        ::return: Name of the new column that stores the WKT geometry.
        """
        self.network_gdf[target_column_name] = self.network_gdf[
            current_column_name
        ].apply(lambda x: x.wkt)
        return target_column_name

    def sample_points(self, geometry, num_points):
        from shapely.geometry import MultiLineString, LineString, Point

        """
        Generate evenly spaced sample points along the geometry.
        Handles both LineString and MultiLineString geometries.
        """
        points = []

        if isinstance(geometry, LineString):
            points = [
                geometry.interpolate(float(i) / (num_points - 1), normalized=True)
                for i in range(num_points)
            ]
        elif isinstance(geometry, MultiLineString):
            # Use .geoms to iterate over each LineString in a MultiLineString
            for line in geometry.geoms:
                points += [
                    line.interpolate(float(i) / (num_points - 1), normalized=True)
                    for i in range(num_points)
                ]

        return points

    def generate_sampling_points(
        self, segment_sampling_points_amount: int
    ) -> gpd.GeoDataFrame:
        """
        Generate sampling points for each road segment.

        Parameters:
        - segment_sampling_points_amount: The number of sampling points to generate for each road segment.

        Returns:
        - GeoDataFrame with sampling points added as a new column.
        """

        self.network_gdf[SEGMENT_SAMPLING_POINTS_KEY] = self.network_gdf.geometry.apply(
            lambda x: self.sample_points(x, segment_sampling_points_amount)
        )

    def process_osm_network(
        self, project_crs: int, original_crs: int, segment_sampling_points_amount: int
    ) -> gpd.GeoDataFrame:
        """
        Process OSM network.

        :param user_config: User configurations.
        :return: GeoDataFrame of the OSM network.
        """
        LOG.info("Processing OSM network.")
        self.convert_network_to_gdf()
        if ROOPE_DEVELOPMENT:
            # ota sata ekeaa rivii vaan
            dev_gdf = self.get_network_gdf().iloc[:100]
            self.set_network_gdf(dev_gdf)

        self.rename_column(GENERAL_ID_DEFAULT_KEY, OSM_ID_DEFAULT_KEY)
        self.handle_crs(project_crs, original_crs)
        self.network_filter_by_columns(NETWORK_COLUMNS_TO_KEEP)
        self.handle_invalid_geometries()
        # self.handle_invalid_geometries()
        self.generate_sampling_points(segment_sampling_points_amount)
        return self.get_network_gdf()
