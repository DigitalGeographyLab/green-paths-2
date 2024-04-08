""" Parse user configuration file. """

import os
import yaml
from green_paths_2.src.config import DEFAULT_CONFIGURATION_VALUES
from green_paths_2.src.data_utilities import determine_file_type
from green_paths_2.src.preprocessing.spatial_operations import crs_uses_meters
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.green_paths_exceptions import (
    ConfigDataError,
    ConfigError,
)
from green_paths_2.src.preprocessing.data_types import (
    DataSourceModel,
    DataTypes,
    RoutingComputers,
    TravelModes,
)


LOG = setup_logger(__name__, LoggerColors.PURPLE.value)

# TODO: add checks for raster resolution...


class UserConfig:
    def __init__(self, config_path: str, skip_validation: bool = False) -> None:
        """Initialize UserConfig object.

        Parameters
        ----------
        config_path : str
            Path to the configuration file.
        skip_validation : bool
            Skip validation of the configuration file. Default is False.
            Should be used only for testing purposes and in Describer.
        """
        self.config_path = config_path
        self.skip_validation = skip_validation
        self.data_source_names = []

    def parse_config(self):
        """
        Parse config file and populate attributes.

        Parameters
        ----------
        config_path : str
            Path to the configuration file.
        """
        try:
            config = self._load_config(self.config_path)
            if not self.skip_validation:
                self.validate_config(config)
            self.set_attributes(config)
            self.set_defaults()
        except FileNotFoundError:
            LOG.error(f"Configuration file not found at {self.config_path}. Exiting!")
            exit(1)
        except yaml.YAMLError:
            LOG.error(
                "Error parsing YAML configuration file, please check the formatting of the file. Use e.g. yamllint or some online tool to check the file. Exiting!"
            )
            exit(1)
        return self

    def _load_config(self, config_path: str) -> dict:
        """
        Load user configuration from the given path.

        Parameters
        ----------
        config_path : str
            Path to the configuration file.

        Returns
        -------
        dict
            A dictionary containing the user configuration.
        """
        LOG.info(f"Reading configuration file from {config_path}")
        # read config yaml
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        return config

    def validate_config(self, config: dict) -> None:
        """
        Validate the user configuration.

        Parameters
        ----------
        config : dict
            A dictionary containing the user configuration.
        """
        LOG.info("Validating user config")
        self._validate_crs(config)
        self._validate_project_configs(config)
        self._validate_osm_pbf_network_file(config)
        self._validate_data_sources(config)
        self._validate_routing_config(config)
        self._validate_analysing_config(config)

    def set_attributes(self, config: dict) -> None:
        """
        Set valid attributes from the given configuration.

        Parameters
        ----------
        config : dict
            A dictionary containing the user configuration.

        """
        for key, value in config.items():
            if isinstance(value, dict):
                # create a sub-config for nested dictionaries
                sub_config = UserConfig(self.config_path)
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

    def set_defaults(self):
        """
        Update configuration with default values for any keys not provided by the user.
        """
        for key, default_value in DEFAULT_CONFIGURATION_VALUES.items():
            if not hasattr(self, key):
                setattr(self, key, default_value)

    def _validate_project_configs(self, config: dict) -> None:
        """Validate project configurations."""
        save_to_cache = config.get("save_to_cache")
        if save_to_cache and not isinstance(save_to_cache, bool):
            raise ConfigError(
                "Invalid save to cache config, should be bool, True or False."
            )

    def _validate_osm_pbf_network_file(self, config: dict) -> None:
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
        LOG.info("OSM PBF configurations validated.")

    def _validate_crs(self, config: dict) -> None:
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

        LOG.info("CRS configurations validated.")

    def _validate_data_sources(self, config: dict) -> None:
        """
        Parse data sources from the given configuration.

        :param config: A dictionary containing configuration data.
        :return: A list of dictionaries, each containing the data name, filepath, and type.
        """
        data_sources_config = config.get("data_sources", [])
        if not data_sources_config:
            raise ConfigError(
                "Invalid or missing data sources configuration. See that atleast one data source is provided in user_config.yaml."
            )

        for data in data_sources_config:
            # init all the values using enum names
            name = data.get(DataSourceModel.Name.value)
            self.data_source_names.append(name)
            filepath = data.get(DataSourceModel.Filepath.value)
            data_type = data.get(DataSourceModel.Datatype.value)
            data_column = data.get(DataSourceModel.Datacolumn.value)
            data_buffer = data.get(DataSourceModel.DataBuffer.value)
            min_data_value = data.get(DataSourceModel.MinDataValue.value)
            max_data_value = data.get(DataSourceModel.MaxDataValue.value)
            good_exposure = data.get(DataSourceModel.GoodExposure.value)
            raster_cell_resolution = data.get(
                DataSourceModel.Rastercellresolution.value
            )
            original_crs = data.get(DataSourceModel.Originalcrs.value)
            columns_of_interest = data.get(DataSourceModel.Columnsofinterest.value)
            save_raster_file = data.get(DataSourceModel.Saverasterfile.value)

            # see if given dataType is what expected
            determined_data_type = determine_file_type(filepath)
            # print heavy errors if the data type is not what expected
            # we don't want to crash though because the determined data type might not be correct
            if data_type and determined_data_type and data_type != determined_data_type:
                LOG.warning("\n")
                LOG.warning("! ! !")
                LOG.warning(
                    "Data type in config file does not match determined file extension."
                )
                LOG.warning("IF THE DATATYPE IS WRONG, IT WILL CAUSE ERRORS LATER ON.")
                LOG.warning("! ! !")
                LOG.warning("\n")

            # if data type not given, use the determined
            if not data_type:
                data_type = determined_data_type

            # data name
            if not name or not isinstance(name, str):
                raise ConfigDataError("Invalid or missing data name configuration.")

            # filepath
            if not filepath or not os.path.exists(filepath):
                raise ConfigDataError(f"Invalid or missing filepath configuration.")

            #  data type, mandatory (but if missing, try to determine from file extension)
            if data_type not in [dt.value for dt in DataTypes]:
                raise ConfigDataError(
                    f"Invalid or not supported datatype configuration."
                )

            # data column for vector data, mandatory
            if data_type == DataTypes.Vector.value and not data_column:
                raise ConfigDataError(
                    "Invalid or missing data column configuration for vector data."
                )

            # data column for raster data, optional
            if data_column == DataTypes.Raster.value and (
                data_column and not isinstance(data_column, str)
            ):
                raise ConfigDataError(
                    "Invalid data column configuration. Should be string. This optional attribute can be left empty. If provided, it should be string."
                )

            # data buffer, optional
            if data_buffer and not isinstance(data_buffer, int):
                raise ConfigDataError(
                    "Invalid data buffer configuration. Should be integer. This optional attribute can be left empty, if provided, it should be integer."
                )

            # min normalized, mandatory
            if min_data_value is None or (not isinstance(min_data_value, (int, float))):
                raise ConfigDataError(
                    "Invalid min normalized configuration. Should be float or integer."
                )

            # max normalized, mandatory
            if not max_data_value or not (
                isinstance(max_data_value, int) or isinstance(max_data_value, float)
            ):
                raise ConfigDataError(
                    "Invalid max normalized configuration. Should be float or integer."
                )

            if min_data_value >= max_data_value:
                raise ConfigDataError(
                    "Invalid min normalized and max normalized configuration. Max normalized should be greater than min normalized."
                )

            # good exposure, mandatory
            if not good_exposure and not isinstance(good_exposure, bool):
                raise ConfigDataError(
                    "Invalid or missing good exposure configuration. Should be boolean."
                )

            # raster cell resolution, mandatory for vector data, optional for raster data

            # for vector data, mandatory
            if data_type == DataTypes.Vector.value and (
                not raster_cell_resolution
                or not isinstance(raster_cell_resolution, int)
            ):
                raise ConfigDataError(
                    "Invalid or missing raster cell resolution configuration for vector data. Should be integer. Mandatory for vector data. if provided, it should be integer."
                )

            # for raster data, optional
            if (
                data_type == DataTypes.Raster.value
                and raster_cell_resolution
                and not isinstance(raster_cell_resolution, int)
            ):
                raise ConfigDataError(
                    "Invalid raster cell resolution configuration. Should be integer. Optional for raster data."
                )

            # original crs, optional
            if original_crs and not (
                isinstance(original_crs, int) or isinstance(original_crs, str)
            ):
                raise ConfigDataError(
                    "Invalid original crs configuration. Should be integer or string. This optional attribute can be left empty. If provided, it should be integer or string."
                )

            # columns of interest, optional
            if (
                columns_of_interest and not (isinstance(columns_of_interest, list))
            ) or (
                columns_of_interest
                and not all(isinstance(column, str) for column in columns_of_interest)
            ):
                raise ConfigDataError(
                    "Invalid columns of interest configuration. Should be list of strings. This optional attribute can be left empty. If provided, it should be list of strings."
                )

            # save raster file, optional
            if save_raster_file and not isinstance(save_raster_file, bool):
                raise ConfigDataError(
                    "Invalid save raster file configuration. Should be boolean. This optional attribute can be left empty. If provided, it should be boolean."
                )

        LOG.info("Data sources configurations validated.")

    def _validate_routing_config(self, config: dict) -> None:
        """
        Validate routing configurations.

        :param config: A dictionary containing configuration data.
        """
        routing_config = config.get("routing", {})
        if not routing_config:
            raise ConfigError(
                "Invalid or missing routing configuration. See that atleast one data source is provided in user_config.yaml."
            )

        computer: str = routing_config.get(DataSourceModel.Computer.value)
        transport_mode: str = routing_config.get(DataSourceModel.TransportMode.value)
        od_pairs_path: str = routing_config.get(
            DataSourceModel.Origins_destinations.value
        )
        exposure_parameters: list[dict] = routing_config.get(
            DataSourceModel.ExposureParameters.value
        )

        if (
            not computer
            or not isinstance(computer, str)
            or computer not in [rc.value for rc in RoutingComputers]
        ):
            raise ConfigDataError(
                "Invalid or missing computer configuration in routing parameters. Should be matrix or detailed."
            )

        if (
            not transport_mode
            or not isinstance(transport_mode, str)
            or transport_mode not in [tm.value for tm in TravelModes]
        ):
            raise ConfigDataError(
                "Invalid or missing travel mode configuration in routing parameters. Should be walking or cycling."
            )

        if (
            not od_pairs_path
            or not isinstance(od_pairs_path, str)
            or not os.path.exists(od_pairs_path)
        ):
            raise ConfigDataError(
                "Invalid or missing od pairs path configuration in routing parameters."
            )

        for exposure_param in exposure_parameters:
            name = exposure_param.get(DataSourceModel.Name.value)
            sensitivity = exposure_param.get(DataSourceModel.Sensitivity.value)
            allow_missing_data = exposure_param.get(
                DataSourceModel.AllowMissingData.value
            )
            if not name or not isinstance(name, str):
                raise ConfigDataError(
                    "Invalid or missing exposure parameter name configuration."
                )

            preprocessing_data_sources_names = [
                data.get(DataSourceModel.Name.value)
                for data in config.get("data_sources")
            ]

            if name not in preprocessing_data_sources_names:
                raise ConfigDataError(
                    "Routing Exposure parameter name not found in Preprocessing data sources. Check that the name matches with the data source name."
                )
            if not sensitivity or not isinstance(sensitivity, (int, float)):
                raise ConfigDataError(
                    "Invalid sensitivity configuration in routing parameters. Should be float or integer."
                )
            if allow_missing_data and not isinstance(allow_missing_data, bool):
                raise ConfigDataError(
                    "Invalid allow missing data configuration in routing parameters. Should be boolean if set."
                )
            LOG.info("Routing configuration validated.")

    def _validate_analysing_config(self, config: dict) -> None:
        """
        Validate analysing configurations.

        :param config: A dictionary containing configuration data.
        """
        analysing_config = config.get("analysing", {})

        if not analysing_config:
            return

        cumulative_ranges = analysing_config.get(DataSourceModel.CumulativeRanges.value)

        if not cumulative_ranges:
            return

        cumulative_keys_valid = [
            key for key in cumulative_ranges.keys() if key in self.data_source_names
        ]

        if not cumulative_keys_valid:
            raise ConfigDataError(
                "Invalid cumulative ranges in analysing parameters. No valid data source names found, cumulative values might have keys that aren't datasources."
            )

        for data_name in self.data_source_names:
            cumulative_ranges_data = cumulative_ranges.get(data_name)
            if not cumulative_ranges_data:
                # not all data sources might have cumulative ranges
                continue

            if cumulative_ranges_data:

                if not isinstance(cumulative_ranges_data, list):
                    raise ConfigDataError(
                        "Invalid cumulative ranges in analysing parameters. Should be list of float or integers."
                    )

                for range_value_pair in cumulative_ranges_data:
                    if not isinstance(range_value_pair, list):
                        raise ConfigDataError(
                            "Invalid cumulative ranges in analysing parameters. Should be list of float or integers."
                        )
                    for single_range_value in range_value_pair:
                        if not isinstance(single_range_value, (int, float)):
                            raise ConfigDataError(
                                "Invalid cumulative ranges in analysing parameters. Should be list of float or integers."
                            )

            LOG.info("Analysing configuration validated.")

        keep_geometry: bool = analysing_config.get(DataSourceModel.KeepGeometry.value)

        if keep_geometry and not isinstance(keep_geometry, bool):
            raise ConfigDataError(
                "Invalid keep_geometry in analysing parameters. Should be boolean True or False."
            )
