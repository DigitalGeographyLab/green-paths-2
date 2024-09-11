""" Handle execution of different pipelines. """

from ..src.database_controller import DatabaseController
from .config import (
    ALL_PIPELINE_NAME,
    ANALYSING_PIPELINE_NAME,
    PREPROCESSING_PIPELINE_NAME,
    ROUTING_PIPELINE_NAME,
    SEGMENT_STORE_TABLE,
    USER_CONFIG_PATH,
)
from .exposure_analysing.main import exposure_analysing_pipeline
from .green_paths_exceptions import PipeLineRuntimeError
from .osm_network_controller import handle_osm_network_process
from .preprocessing.main import preprocessing_pipeline
from .preprocessing.user_config_parser import UserConfig

from .preprocessing.user_data_handler import UserDataHandler
from .routing.main import routing_pipeline

from .logging import setup_logger, LoggerColors
from .timer import time_logger

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


def init_config_and_data_handler(config_path: str = None) -> tuple:
    """
    Initialize user config and data handler.

    Parameters
    ----------
    config_path : str
        Path to the user config file.

    Returns
    -------
    UserConfig
        User config object.
    UserDataHandler
        User data handler object.
    """
    config_path = config_path if config_path else USER_CONFIG_PATH
    user_config = UserConfig(config_path).parse_config()
    data_handler = UserDataHandler()
    data_handler.populate_data_sources(data_sources=user_config.data_sources)
    return user_config, data_handler


@time_logger
def handle_pipelines(
    pipeline_name: str, config_path: str = None, use_exposure_cache: bool = False
):
    """
    Master function to handle different pipelines.

    Parameters
    ----------
    pipeline_name : str
        Name of the pipeline to be executed. Options are "preprocessing", "routing" and "all".
    use_exposure_cache : bool
        If True, use exposure cache if found from data/cache directory.
        This will be only used if pipeline_name is "all".

    Raises
    ------
    PipeLineRuntimeError
        If pipeline fails.
    """
    try:
        user_config, data_handler = init_config_and_data_handler(config_path)

        db_controller = DatabaseController()

        if pipeline_name == PREPROCESSING_PIPELINE_NAME:
            osm_network_gdf = handle_osm_network_process(user_config)
            preprocessing_pipeline(osm_network_gdf, data_handler, user_config)
        elif pipeline_name == ROUTING_PIPELINE_NAME:
            routing_pipeline(data_handler, user_config)
        elif pipeline_name == ANALYSING_PIPELINE_NAME:
            exposure_analysing_pipeline(user_config)
        elif pipeline_name == ALL_PIPELINE_NAME:

            skip_preprocessing = False
            if use_exposure_cache:
                # make sure that the segment_store table has values
                if db_controller.get_row_count(SEGMENT_STORE_TABLE) > 0:
                    skip_preprocessing = True
                    LOG.info("Using exposure cache, skipping preprocessing.")
                else:
                    LOG.info(
                        "Used -uc (use cache) flag, but nothing found from db segemnt_store, so will process preprocessing pipeline"
                    )

            if not skip_preprocessing:
                osm_network_gdf = handle_osm_network_process(user_config)
                preprocessing_pipeline(osm_network_gdf, data_handler, user_config)
                LOG.info("\n\n\n * * * \n\n\n")

            routing_pipeline(data_handler, user_config)

            LOG.info("\n\n\n * * * \n\n\n")
            exposure_analysing_pipeline(
                user_config,
            )
    except PipeLineRuntimeError as e:
        LOG.error(f"Pipeline controller failed with error: {e}")
        raise e
