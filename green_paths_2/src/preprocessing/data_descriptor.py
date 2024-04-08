""" This module is used to describe the data sources and the OSM network. """

import os
import geopandas as gpd
from green_paths_2.src.config import (
    DATA_CACHE_DIR_PATH,
    DESCRIPTOR_FILE_NAME,
    LOGS_CACHE_DIR_NAME,
    USER_CONFIG_PATH,
)
from green_paths_2.src.config_validator import validate_user_config
from green_paths_2.src.data_utilities import determine_file_type
from green_paths_2.src.green_paths_exceptions import PipeLineRuntimeError
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.preprocessing.custom_functions import (
    apply_custom_processing_function,
)
from green_paths_2.src.preprocessing.data_source import DataSource
from green_paths_2.src.preprocessing.data_types import DataTypes
from green_paths_2.src.preprocessing.osm_network_handler import OsmNetworkHandler
from green_paths_2.src.preprocessing.raster_operations import (
    check_raster_file_crs,
    describe_raster_data,
    reproject_raster_to_crs,
)
from green_paths_2.src.preprocessing.spatial_operations import (
    check_if_raster_and_network_extends_overlap,
    check_if_vector_data_and_network_extends_overlap,
    create_buffer_for_geometries,
    handle_gdf_crs,
    has_invalid_geometries,
)
from green_paths_2.src.preprocessing.user_config_parser import UserConfig
from green_paths_2.src.preprocessing.user_data_handler import UserDataHandler
from green_paths_2.src.preprocessing.vector_processor import (
    list_vector_data_layers,
    load_vector_data,
)


LOG = setup_logger(__name__, LoggerColors.RED.value)


class DataDescriptor:
    """
    This class is used to describe the data sources and the OSM network.
    Run the descriptor only with a valid user config file.
    Use validate cli command to validate the user config file first.
    """

    def __init__(self):
        self.data_description_text: str = ""

    def _write_new_line_to_data_description_text(self, new_line: str) -> None:
        self.data_description_text += new_line + "\n"

    # TODO: laita tähän extendien checkaaminen et overlappaa, vector sekä raster

    def describe(self, save_to_file: bool = False) -> None:
        """
        Describe data
        Descriptor needs to be run with valid user config file.
        Will call validation module before running the descriptor.

        Parameters
        ----------
        save_to_file : bool, optional
            If True, will save the data description to a file, by default False

        Raises
        ------
        PipeLineRuntimeError
            If the descriptor fails.
        """

        if not validate_user_config():
            LOG.error(
                "User config file is not valid. Descriptor needs to be run with valid user_cofiguration. Add all missing attributes to data_sources etc."
            )
            return

        LOG.info("Starting data descriptor.")

        try:

            # parse and validate user configurations
            user_config = UserConfig(
                USER_CONFIG_PATH, skip_validation=True
            ).parse_config()

            project_crs = user_config.project_crs

            # create osm network from user config osm pbf path

            # TODO: is this needed?
            network = OsmNetworkHandler(
                osm_pbf_file=user_config.osm_network.osm_pbf_file_path
            )

            network.convert_network_to_gdf()
            network_gdf = network.get_network_gdf()

            # project network to project crs to allow overlap checks
            network_in_project_crs = network
            network_in_project_crs.convert_network_to_gdf()

            network_in_project_crs.handle_crs(
                project_crs=project_crs, original_crs=network_gdf.crs
            )

            network_in_project_crs_gdf = network_in_project_crs.get_network_gdf()

            # HEADER
            self._write_new_line_to_data_description_text("\nDATA DESCRIPTION")
            self._write_new_line_to_data_description_text("\n=================\n")

            # OSM NETWORK CONFIGURATIONS

            self._write_new_line_to_data_description_text(
                "OSM NETWORK CONFIGURATIONS: \n"
            )

            self._write_new_line_to_data_description_text(
                f"CRS of the OSM network: {network_gdf.crs}",
            )

            self._write_new_line_to_data_description_text(
                f"Has invalid geometries: {has_invalid_geometries(network_gdf, 'network')}"
            )

            self._write_new_line_to_data_description_text("\n=================\n")

            # handle data sources

            self._write_new_line_to_data_description_text(
                "DATA SOURCES CONFIGURATIONS:"
            )

            data_handler = UserDataHandler()
            data_handler.populate_data_sources(data_sources=user_config.data_sources)

            for data_name, data_source in data_handler.data_sources.items():

                self._write_new_line_to_data_description_text("\n *** DATA SOURCE ***")

                if (
                    data_source.get_name() == DataTypes.Vector.value
                    or determine_file_type(data_source.get_filepath())
                    == DataTypes.Vector.value
                ):
                    LOG.info(f"processing vector data: {data_name}")

                    vector_data = load_vector_data(data_source.get_filepath())

                    vector_data_crs = vector_data.crs
                    vector_data_length = len(vector_data)

                    # get all possible data_columns (only numerical columns are valid data columns)
                    vector_data_columns = vector_data.select_dtypes(
                        include=["int", "float"]
                    ).columns

                    # filter out numerical geometry related values for obvious reasons
                    vector_data_columns = [
                        column
                        for column in vector_data_columns
                        if not any(
                            keyword in column
                            for keyword in [
                                "geometry",
                                "latitude",
                                "lattitude",
                                "longitude",
                            ]
                        )
                    ]

                    # get min and max values from vector data using the data column
                    min_value = vector_data[data_source.get_data_column()].min()
                    max_value = vector_data[data_source.get_data_column()].max()

                    # get all possible layers from the vector data
                    vector_data_all_possible_layers = list_vector_data_layers(
                        data_source.get_filepath()
                    )

                    # get all possible invalid geometries
                    data_has_invalid_geometries = has_invalid_geometries(
                        vector_data, data_name
                    )

                    self._write_new_line_to_data_description_text(
                        f"Data name: {data_name}",
                    )

                    self._write_new_line_to_data_description_text(
                        f"Data CRS: {vector_data_crs}",
                    )

                    self._write_new_line_to_data_description_text(
                        f"Data length: {vector_data_length}",
                    )

                    self._write_new_line_to_data_description_text(
                        f"Data column used: {data_source.get_data_column()}",
                    )

                    self._write_new_line_to_data_description_text(
                        f"All possible data columns: {vector_data_columns}",
                    )

                    self._write_new_line_to_data_description_text(
                        f"Min value ({data_source.get_data_column()}): {min_value}",
                    )

                    self._write_new_line_to_data_description_text(
                        f"Max value ({data_source.get_data_column()}): {max_value}",
                    )

                    self._write_new_line_to_data_description_text(
                        f"Possible layers: {vector_data_all_possible_layers}",
                    )

                    self._write_new_line_to_data_description_text(
                        f"Has invalid geometries: {data_has_invalid_geometries}",
                    )

                    vector_data_in_project_crs = handle_gdf_crs(
                        name=data_name,
                        gdf=vector_data,
                        target_crs=project_crs,
                        original_crs=data_source.get_original_crs(),
                    )

                    # create buffer for geometries
                    vector_data_in_project_crs = create_buffer_for_geometries(
                        "data_name", vector_data_in_project_crs, 5
                    )

                    data_and_network_overlap = (
                        check_if_vector_data_and_network_extends_overlap(
                            vector_data_in_project_crs, network_in_project_crs_gdf
                        )
                    )

                    self._write_new_line_to_data_description_text(
                        f"Vector data and network extends overlap: {data_and_network_overlap}",
                    )

                elif (
                    data_source.get_data_type() == DataTypes.Raster.value
                    or determine_file_type(data_source.get_filepath())
                    == DataTypes.Raster.value
                ):
                    LOG.info(f"processing raster data: {data_name}")

                    raster_path = (
                        apply_custom_processing_function(
                            data_source,
                        )
                        if data_source.get_custom_processing_function()
                        else data_source.get_filepath()
                    )

                    crs, min, max, count, nan_count = describe_raster_data(raster_path)

                    self._write_new_line_to_data_description_text(
                        f"Data name: {data_name}",
                    )

                    self._write_new_line_to_data_description_text(f"Data CRS: {crs}")

                    self._write_new_line_to_data_description_text(
                        f"Min value: {min}",
                    )

                    self._write_new_line_to_data_description_text(
                        f"Max value: {max}",
                    )

                    self._write_new_line_to_data_description_text(
                        f"Count (non-NaN): {count}",
                    )

                    self._write_new_line_to_data_description_text(
                        f"NaN count: {nan_count}",
                    )

                    if check_raster_file_crs(raster_path) != user_config.project_crs:
                        LOG.info(
                            f"Raster not in project crs. Reprojecting {raster_path} to project crs: {user_config.project_crs}"
                        )
                        # TODO: confeihin
                        reprojected_raster_filepath = raster_path.replace(
                            ".tif", "_reprojected.tif"
                        )

                        reproject_raster_to_crs(
                            input_raster_filepath=raster_path,
                            output_raster_filepath=reprojected_raster_filepath,
                            target_crs=user_config.project_crs,
                            original_crs=data_source.get_original_crs(),
                            new_raster_resolution=data_source.get_raster_cell_resolution(),
                        )

                        LOG.debug(
                            f"reprojected crs: {check_raster_file_crs(reprojected_raster_filepath)}"
                        )
                        LOG.debug(
                            f"original raster crs: {check_raster_file_crs(raster_path)}"
                        )

                        # use reprojected file if it was created or exists
                        if os.path.exists(reprojected_raster_filepath):
                            raster_path = reprojected_raster_filepath

                    data_and_network_overlap = (
                        check_if_raster_and_network_extends_overlap(
                            raster_path, network_in_project_crs_gdf
                        )
                    )

                    self._write_new_line_to_data_description_text(
                        f"Raster data and network extends overlap: {data_and_network_overlap}",
                    )

            if save_to_file:
                save_file_path = os.path.join(
                    DATA_CACHE_DIR_PATH, LOGS_CACHE_DIR_NAME, DESCRIPTOR_FILE_NAME
                )
                LOG.info(f"Saving data description to file: {save_file_path}")
                # will override the file if it exists
                with open(save_file_path, "w") as file:
                    file.write(self.data_description_text)
            else:
                LOG.info("Logging data description to console.")
                LOG.info(self.data_description_text)

        except PipeLineRuntimeError as e:
            LOG.error(f"Data descriptor failed with error {e}.")
            raise e

        LOG.info("Data descriptor finished.")
