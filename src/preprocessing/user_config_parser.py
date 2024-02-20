""" Parse user configuration file. """

import os
import yaml
from preprocessing.spatial_operations import crs_uses_meters
from src.logging import setup_logger, LoggerColors
from src.preprocessing.preprocessing_exceptions import ConfigDataError, ConfigError
from src.preprocessing.data_types import DataSourceModel, DataTypes


LOG = setup_logger(__name__, LoggerColors.PURPLE.value)


class UserConfig:
    def __init__(self) -> None:
        pass

    def parse_config(self, config_path: str):
        """
        Parse config file and populate attributes.

        :param config_path: Path to the configuration file.
        """
        try:
            LOG.info(f"Reading configuration file from {config_path}")
            # read config yaml
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)

            LOG.info("Validating user config")
            # validate user_config
            self.validate_osm_pbf_network_file(config)
            self.validate_data_sources(config)
            self.validate_crs(config)
            # set all self class attributes from the config
            self.set_attributes(config)
        # handle possible errors
        except FileNotFoundError:
            raise ConfigError(f"Configuration file not found at {config_path}")
        except yaml.YAMLError:
            raise ConfigError("Error parsing YAML configuration file.")
        return self

    def set_attributes(self, config: dict) -> None:
        """Set self class attributes from the given configuration."""
        for key, value in config.items():
            if isinstance(value, dict):
                # create a sub-config for nested dictionaries
                sub_config = UserConfig()
                sub_config.set_attributes(value)
                setattr(self, key, sub_config)
            # elif isinstance(value, list):
            #     # if list, process each element in list
            #     processed_list = self.process_list(value)
            #     setattr(self, key, processed_list)
            else:
                # just set the plain value
                setattr(self, key, value)

    def validate_osm_pbf_network_file(self, config: dict) -> None:
        """
        Validate osm_pdb_path from the given configuration.

        :param osm_pdb_path: Path to the osm_pdb file.
        """
        osm_pbf_path = config.get("osm_network").get("osm_pbf_file_path")

        if not osm_pbf_path or not os.path.exists(osm_pbf_path):
            raise ConfigDataError(
                f"Didn't find osm network pbf file with provided user confs. Path was {osm_pbf_path}"
            )
        # TODO: lisää tähän joku checki mikä lataa ja kattoo onhan siel kamaa jne... et on osmid't ja kaikkee
        _, file_extension = os.path.splitext(osm_pbf_path)
        if file_extension.lower() != ".pbf":
            raise ConfigDataError(
                f"Invalid osm_pdb_path in data config file. Should be X.osm.pbf Path was {osm_pbf_path}"
            )

    def validate_crs(self, config: dict) -> None:
        """
        Parse crs from the given configuration.

        :param config: A dictionary containing configuration data.
        """
        if not config.get("project_crs"):
            raise ConfigDataError("Invalid or missing project crs configuration.")

        if not crs_uses_meters(config.get("project_crs")):
            raise ConfigDataError(
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
            data_type = data.get(DataSourceModel.Datatype.value)

            # TODO: laita tänne vlalidoinnit tolle datalle...

            # TODO: kato meneekö ees tänne jos kaatuu aikaisemmin
            if (
                not name
                or not filepath
                or data_type not in [dt.value for dt in DataTypes]
            ):
                raise ConfigDataError("Invalid data source configuration.")
