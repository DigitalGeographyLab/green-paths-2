from celery import Celery

import logging

logger = logging.getLogger(__name__)

# Set up Celery app with Redis
celery_app = Celery("tasks", broker="redis://localhost:6379/0")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@celery_app.task
def run_aqi_preprocessing():
    from .network_builder_singleton import network_builder_instance

    try:
        network_builder_instance.build_networks_and_possible_preprocessing_in_background()
        logging.info("Finished AQI preprocessing task.")
    except Exception as e:
        logging.error(f"Failed to run AQI preprocessing task. Error: {e}")
