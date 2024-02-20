""" For dealing with OSM network related operations. """

import geopandas as gpd
from pyrosm import OSM

from src.data_utilities import filter_gdf_by_columns_if_found, rename_gdf_column
from src.preprocessing.user_config_parser import UserConfig
from src.logging import setup_logger
from src.logging import setup_logger, LoggerColors
from src.timer import time_logger

from src.preprocessing.spatial_operations import (
    has_invalid_geometries,
    fix_invalid_geometries,
    handle_gdf_crs,
)


LOG = setup_logger(__name__, LoggerColors.BLUE.value)


# TODO: plottailua, poista tai siirrä
# ax = test_result["buffer"].plot()

# fig = ax.get_figure()
# fig.savefig(
#     "/Users/hcroope/omat/GP2/green_paths_2/green_paths_2/src/data/roope_test.png"
# )

# Convert the network to a GeoDataFrame
# gdf_edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
# LOG.info(gdf_edges.head())
# Get pedestrian roads as GeoDataFrame
# gdf_pedestrian = osm_network.get_network(network_type="walking")
# combined_gdf = pd.concat([gdf_pedestrian, gdf_cycling], ignore_index=True)


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
        """TODO"""
        LOG.info("converting OSM network to gdf")
        osm_network = OSM(self.osm_pbf_file)
        # TODO:  -> laita tää ottamaan vaa esim pyöräiltävät tai käveltävät tms.? -> ei vältsii ettei lähe liikaa kamaa pois?
        network_gdf = osm_network.get_network(network_type="all")
        LOG.info("successfully converted OSM network to gdf")
        LOG.info(f"network gdf size: {len(network_gdf)}")
        self.network_gdf = network_gdf

    def handle_crs(self, user_config: UserConfig) -> None:
        """Sets the CRS for the network GeoDataFrame."""
        LOG.info("Handle network CRS")
        self.network_gdf = handle_gdf_crs(
            "network",
            self.network_gdf,
            target_crs=user_config.project_crs,
            original_crs=user_config.osm_network.original_crs,
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
