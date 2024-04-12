""" Module for routing with R5py. """

from ..config import (
    ALLOW_MISSING_DATA_DEFAULT,
    NORMALIZED_DATA_SUFFIX,
)

import geopandas as gpd

from ..preprocessing.data_types import DataSourceModel, TravelModes
from ..preprocessing.user_config_parser import UserConfig
from ..routing.routing_utilities import set_environment_and_import_r5py
from ..timer import time_logger

from ..logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.BLUE.value)


set_environment_and_import_r5py()

# import r5py
from r5py import (
    CustomCostTransportNetwork,
    TravelTimeMatrixComputer,
)


@time_logger
def init_travel_time_matrix_computer(
    custom_cost_transport_network: CustomCostTransportNetwork,
    origins: gpd.GeoDataFrame,
    destinations: gpd.GeoDataFrame,
    transport_mode: list[TravelModes],
):
    """Route with TravelTimeMatrixComputer."""
    LOG.info("Initing TravelTimeMatrixComputer")

    travel_time_matrix_computer_custom_cost = TravelTimeMatrixComputer(
        custom_cost_transport_network,
        origins=origins,
        destinations=destinations,
        transport_modes=transport_mode,
    )

    LOG.info("Finished initing TravelTimeMatrixComputer")
    return travel_time_matrix_computer_custom_cost


@time_logger
def route_travel_time_matrix_computer(
    travel_time_matrix_computer,
):
    LOG.info("Initing TravelTimeMatrixComputer")
    travel_time_matrix_computer_results = (
        travel_time_matrix_computer.compute_travel_times()
    )
    LOG.info("Finished routing with TravelTimeMatrixComputer")

    return travel_time_matrix_computer_results


def _build_custom_cost_networks_params(
    exposure_dict: dict, routing_config: dict
) -> tuple:
    """
    Populate the parameters for building custom cost networks.

    Parameters
    ----------
    routing_config : dict
        The routing configuration.

    Returns
    -------
    tuple
        The names, sensitivities, cost data and allow_missing_data dictionaries.
    """
    names = []
    sensitivities = []
    custom_cost_segment_weight_factors = []
    allow_missing_datas = []

    for exposure_confs in routing_config.exposure_parameters:
        exposure_name = exposure_confs.get(DataSourceModel.Name.value)
        exposure_name_normalized = f"{exposure_name}{NORMALIZED_DATA_SUFFIX}"
        names.append(exposure_name)
        sensitivities.append(exposure_confs.get(DataSourceModel.Sensitivity.value))
        custom_cost_segment_weight_factors.append(
            exposure_dict.get(exposure_name_normalized)
        )
        allow_missing_datas.append(
            exposure_confs.get(
                DataSourceModel.AllowMissingData.value, ALLOW_MISSING_DATA_DEFAULT
            )
        )

    return names, sensitivities, custom_cost_segment_weight_factors, allow_missing_datas


@time_logger
def build_custom_cost_network(
    osm_segmented_network_path: str, exposure_dict: dict, routing_config: dict
):
    """
    Build custom cost network.

    Parameters
    ----------
    osm_segmented_network_path : str
        The path to the segmented OSM network.
    exposure_dict : dict
        The exposure dictionary.
    user_config : dict
        The user configuration.

    Returns
    -------
    CustomCostTransportNetwork
        The custom cost transport network.
    """
    LOG.info("Building custom cost networks")

    names, sensitivities, custom_cost_segment_weight_factors, allow_missing_data = (
        _build_custom_cost_networks_params(exposure_dict, routing_config)
    )

    LOG.info(
        f"Data names: {names}. Using sensitivities: {sensitivities}. Using allow_missing_data: {allow_missing_data}"
    )

    # convert all keys in custom_cost_segment_weight_factors list to str
    custom_cost_segment_weight_factors = [
        {str(k): v for k, v in d.items()} for d in custom_cost_segment_weight_factors
    ]

    custom_cost_transport_network = CustomCostTransportNetwork(
        osm_pbf=osm_segmented_network_path,
        names=names,
        sensitivities=sensitivities,
        custom_cost_segment_weight_factors=custom_cost_segment_weight_factors,
        allow_missing_osmids=allow_missing_data,
    )
    LOG.info("Finished building network")

    return custom_cost_transport_network
