""" Main module for the exposure analysing pipeline."""

from ..exposure_analysing.process_path_batches import (
    process_exposure_results_as_batches,
)

from ...src.database_controller import DatabaseController
from ...src.exposure_analysing.exposure_db_controller import (
    ExposureDbController,
)
from ...src.exposure_analysing.exposures_calculator import (
    ExposuresCalculator,
)

from ..config import (
    ANALYSING_KEY,
    KEEP_GEOMETRY_KEY,
    NAME_KEY,
    OUTPUT_RESULTS_TABLE,
)

from ..exposure_analysing.exposure_data_handlers import (
    save_exposure_results_to_file,
)
from ..green_paths_exceptions import PipeLineRuntimeError
from ..preprocessing.user_config_parser import UserConfig
from ..timer import time_logger

from ..logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


def init_exposure_handlers(db_handler: DatabaseController = None):
    """Initialize exposure analysing handlers."""
    if not db_handler:
        db_handler = DatabaseController()
    exposure_db_controller = ExposureDbController(db_handler)
    exposure_calculator = ExposuresCalculator()

    return db_handler, exposure_db_controller, exposure_calculator


def get_data_names(user_config: UserConfig):
    """Get data names from user config."""
    return [data.get(NAME_KEY) for data in user_config.data_sources]


@time_logger
def exposure_analysing_pipeline(user_config: UserConfig):
    """
    Run the exposure analysing pipeline.

    Parameters
    ----------
    user_config : UserConfig
        User configuration object.

    Raises
    ------
    PipeLineRuntimeError
        If the exposure analysing pipeline fails.
    """
    LOG.info("\n\n\nStarting analysing pipeline\n\n\n")

    try:
        db_handler, exposure_db_controller, exposure_calculator = (
            init_exposure_handlers()
        )

        # get data names as list so that we can loop each different data source
        data_names = get_data_names(user_config=user_config)

        keep_geometries = user_config.get_nested_attribute(
            [ANALYSING_KEY, KEEP_GEOMETRY_KEY], default=False
        )

        process_exposure_results_as_batches(
            db_handler=db_handler,
            exposure_db_controller=exposure_db_controller,
            exposure_calculator=exposure_calculator,
            user_config=user_config,
            data_names=data_names,
            keep_geometries=keep_geometries,
        )

        save_exposure_results_to_file(db_handler, user_config, keep_geometries)

        LOG.info("Analysing pipeline finished.")
    except PipeLineRuntimeError as e:
        LOG.error(f"Analysing pipeline failed with error: {e}")
        raise e
