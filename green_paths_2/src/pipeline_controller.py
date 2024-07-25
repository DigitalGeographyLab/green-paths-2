""" TODO """

from green_paths_2.src.database_controller import DatabaseController
from .config import GP2_DB_PATH, SEGMENT_STORE_TABLE, USER_CONFIG_PATH
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


@time_logger
def handle_pipelines(pipeline_name: str, use_exposure_cache: bool = False):
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
        user_config = UserConfig(USER_CONFIG_PATH).parse_config()
        data_handler = UserDataHandler()
        data_handler.populate_data_sources(data_sources=user_config.data_sources)
        db_controller = DatabaseController(GP2_DB_PATH)

        if pipeline_name == "preprocessing":
            osm_network_gdf = handle_osm_network_process(user_config)
            preprocessing_pipeline(osm_network_gdf, data_handler, user_config)
        elif pipeline_name == "routing":
            routing_pipeline(data_handler, user_config)
        elif pipeline_name == "analysing":
            exposure_analysing_pipeline(user_config)
        elif pipeline_name == "all":

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
