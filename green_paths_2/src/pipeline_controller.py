""" TODO """

from green_paths_2.src.config import USER_CONFIG_PATH
from green_paths_2.src.exposure_analysing.main import exposure_analysing_pipeline
from green_paths_2.src.osm_network_controller import handle_osm_network_process
from green_paths_2.src.preprocessing.main import preprocessing_pipeline
from green_paths_2.src.preprocessing.user_config_parser import UserConfig

from green_paths_2.src.preprocessing.user_data_handler import UserDataHandler
from green_paths_2.src.routing.main import routing_pipeline

from green_paths_2.src.logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


# TODO: make better exception?


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
    Exception
        If pipeline fails.
    """
    try:
        user_config = UserConfig(USER_CONFIG_PATH).parse_config()
        data_handler = UserDataHandler()
        data_handler.populate_data_sources(data_sources=user_config.data_sources)

        if pipeline_name == "preprocessing":
            osm_network_gdf = handle_osm_network_process(user_config)
            preprocessing_pipeline(osm_network_gdf, data_handler, user_config)
        elif pipeline_name == "routing":
            routing_pipeline(data_handler, user_config)
        elif pipeline_name == "analysing":
            exposure_analysing_pipeline(user_config)
        elif pipeline_name == "all":
            if use_exposure_cache:
                LOG.info("Using exposure cache, skipping preprocessing.")
                routing_pipeline(data_handler, user_config)
                LOG.info("\n\n\n * * * \n\n\n")
                exposure_analysing_pipeline(user_config)
            else:
                osm_network_gdf = handle_osm_network_process(user_config)
                preprocessing_pipeline(osm_network_gdf, data_handler, user_config)
                LOG.info("\n\n\n * * * \n\n\n")
                routing_pipeline(data_handler, user_config)
                LOG.info("\n\n\n * * * \n\n\n")
                exposure_analysing_pipeline(user_config)
    except Exception as e:
        LOG.error(f"Pipeline failed with error: {e}")
        raise e
