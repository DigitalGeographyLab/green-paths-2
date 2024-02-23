""" Parse user configuration file. """

import os
import yaml
from green_paths_2.src.data_utilities import determine_file_type
from green_paths_2.src.preprocessing.spatial_operations import crs_uses_meters
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.preprocessing.preprocessing_exceptions import (
    ConfigDataError,
    ConfigError,
)
from green_paths_2.src.preprocessing.data_types import DataSourceModel, DataTypes


LOG = setup_logger(__name__, LoggerColors.PURPLE.value)

# TODO: add checks for raster resolution...


class UserConfig:
    def __init__(self) -> None:
        pass

    def _load_config(self, config_path: str) -> dict:
        """
        Load user configuration from the given path.

        :param config_path: Path to the configuration file.
        :return: A dictionary containing the user configuration.
        """
        LOG.info(f"Reading configuration file from {config_path}")
        # read config yaml
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        return config

    def _validate_config(self, config: dict) -> None:
        """
        Validate the user configuration.
        :param config: A dictionary containing the user configuration.
        """
        LOG.info("Validating user config")
        self.validate_crs(config)
        self.validate_osm_pbf_network_file(config)
        self.validate_data_sources(config)

    def parse_config(self, config_path: str):
        """
        Parse config file and populate attributes.

        :param config_path: Path to the configuration file.
        """
        try:
            config = self._load_config(config_path)
            self._validate_config(config)
            self.set_attributes(config)
        # handle possible errors
        except FileNotFoundError:
            raise ConfigError(f"Configuration file not found at {config_path}")
        except yaml.YAMLError:
            raise ConfigError("Error parsing YAML configuration file.")
        return self

    def set_attributes(self, config: dict) -> None:
        """Set valid attributes from the given configuration."""
        for key, value in config.items():
            if isinstance(value, dict):
                # create a sub-config for nested dictionaries
                sub_config = UserConfig()
                sub_config.set_attributes(value)
                setattr(self, key, sub_config)
            # TODO: handle list?
            # elif isinstance(value, list):
            #     # if list, process each element in list
            #     processed_list = self.process_list(value)
            #     setattr(self, key, processed_list)
            else:
                # plain value
                setattr(self, key, value)

    def validate_osm_pbf_network_file(self, config: dict) -> None:
        """
        Validate osm_pdb_path from the given configuration.

        :param osm_pdb_path: Path to the osm_pdb file.
        """
        osm_pbf_path = config.get("osm_network").get("osm_pbf_file_path")

        if not osm_pbf_path or not os.path.exists(osm_pbf_path):
            raise ConfigError(
                f"Didn't find osm network pbf file with provided user confs. Path was {osm_pbf_path}"
            )
        # TODO: lisää tähän joku checki mikä lataa ja kattoo onhan siel kamaa jne... et on osmid't ja kaikkee
        _, file_extension = os.path.splitext(osm_pbf_path)
        if file_extension.lower() != ".pbf":
            raise ConfigError(
                f"Invalid osm_pdb_path in data config file. Should be X.osm.pbf Path was {osm_pbf_path}"
            )

    def validate_crs(self, config: dict) -> None:
        """
        Parse crs from the given configuration.

        :param config: A dictionary containing configuration data.
        """
        if not config.get("project_crs"):
            raise ConfigError("Invalid or missing project crs configuration.")

        # TODO: validate that the crs is valid crs

        if not crs_uses_meters(config.get("project_crs")):
            raise ConfigError(
                "Invalid project crs. Project crs should use meters as units. Most of projected CRS's use meters as units, opposed to geographic CRS's which use degrees."
            )

    def validate_data_sources(self, config: dict) -> list[dict[str, str]]:
        """
        Parse data sources from the given configuration.

        :param config: A dictionary containing configuration data.
        :return: A list of dictionaries, each containing the data name, filepath, and type.
        """
        data_sources_config = config.get("data_sources", [])
        for data in data_sources_config:
            name = data.get(DataSourceModel.Name.value)
            filepath = data.get(DataSourceModel.Filepath.value)
            data_type = data.get(DataSourceModel.Datatype.value) or determine_file_type(
                filepath
            )
            data_column = data.get(DataSourceModel.Datacolumn.value)
            raster_cell_resolution = data.get(
                DataSourceModel.Rastercellresolution.value
            )
            original_crs = data.get(DataSourceModel.Originalcrs.value)
            columns_of_interest = data.get(DataSourceModel.Columnsofinterest.value)
            save_raster_file = data.get(DataSourceModel.Saverasterfile.value)

            # validate optional data source attributes if provided
            # skip validating those optional attributes which are not provided
            if data_column and not isinstance(data_column, str):
                raise ConfigDataError(
                    "Invalid data column configuration. Should be string. This optional attribute can be left empty."
                )

            if raster_cell_resolution and not isinstance(raster_cell_resolution, int):
                raise ConfigDataError(
                    "Invalid raster cell resolution configuration. Should be integer. This optional attribute can be left empty."
                )

            if original_crs and not (
                isinstance(original_crs, int) or isinstance(original_crs, str)
            ):
                raise ConfigDataError(
                    "Invalid original crs configuration. Should be integer or string. This optional attribute can be left empty."
                )

            # test if columns of interest is list of strings
            if (
                columns_of_interest and not (isinstance(columns_of_interest, list))
            ) or (
                columns_of_interest
                and not all(isinstance(column, str) for column in columns_of_interest)
            ):
                raise ConfigDataError(
                    "Invalid columns of interest configuration. Should be list of strings. This optional attribute can be left empty."
                )

            if save_raster_file and not isinstance(save_raster_file, bool):
                raise ConfigDataError(
                    "Invalid save raster file configuration. Should be boolean. This optional attribute can be left empty."
                )

            if (
                not name
                or not filepath
                or data_type not in [dt.value for dt in DataTypes]
            ):
                raise ConfigDataError("Invalid data source configuration.")
