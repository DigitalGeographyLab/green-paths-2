import threading
from .api_utility_engine import build_custom_cost_networks
from ..config import (
    LATEST_BUILD_AQI_TIMESTAMP_KEY,
    LATEST_FETCH_AQI_TIMESTAMP_KEY,
    UPDATE_IN_PROGRESS_KEY,
    HElSINKI_CITY_KEY,
)
from .redis_client_singleton import redis_client


import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class NetworkBuilder:
    def __init__(self):
        self.build_networks_initialized = False
        self.custom_cost_networks = {}
        self.configs = {}
        self.rlock = threading.RLock()

    def get_build_networks_initialized(self):
        return self.build_networks_initialized

    def get_custom_cost_networks(self):
        return self.custom_cost_networks

    def get_configs(self):
        return self.configs

    def get_update_in_progress(self):
        # Retrieve the status from Redis
        return redis_client.get(UPDATE_IN_PROGRESS_KEY) == b"True"

    # def get_latest_build_aqi_timestamp(self):
    #     return self.latest_build_aqi_timestamp

    def set_latest_build_aqi_timestamp(self, timestamp):
        redis_client.set(LATEST_BUILD_AQI_TIMESTAMP_KEY, timestamp)

    def get_latest_fetch_aqi_timestamp(self):
        return redis_client.get(LATEST_FETCH_AQI_TIMESTAMP_KEY) or "test"

    def set_update_in_progress(self, status):
        # Set the status in Redis
        redis_client.set(UPDATE_IN_PROGRESS_KEY, "True" if status else "False")

    def set_build_networks_initialized(self, build_networks_initialized):
        self.build_networks_initialized = build_networks_initialized

    def set_custom_cost_networks(self, custom_cost_networks):
        self.custom_cost_networks = custom_cost_networks

    def set_configs(self, configs):
        self.configs = configs

    def init_preprocessing_and_custom_cost_networks(self, db_controller, aqi_updater):
        if not self.build_networks_initialized:
            # todo: run only in prod...
            # db_controller.empty_table(SEGMENT_STORE_TABLE)
            # TODO: fetch the latest aqi data... do not run preprocessing
            aqi_updater.fetch_and_update_aqi_data_hourly_job(skip_preprocessing=True)

            self.set_update_in_progress(True)

            # never run preprocessing in background here! will preprocess with every config...
            # city name is hardcoded, should be modified to loop all cities if multiple city support ever needed
            custom_cost_networks, configs = build_custom_cost_networks(
                city_name=HElSINKI_CITY_KEY, preprocess_in_background=False
            )
            self.set_custom_cost_networks(custom_cost_networks)
            self.set_configs(configs)
            self.set_update_in_progress(False)

            logging.info(f"Created {len(custom_cost_networks)} custom cost networks")
            logging.info(f"Custom cost networks: {custom_cost_networks.keys()}")

            self.set_build_networks_initialized(True)
            logging.info("Success in lifespan")

    def build_networks_and_possible_preprocessing_in_background(self):
        logging.info("Building networks in background")
        try:
            self.set_update_in_progress(True)
            city = "helsinki"
            custom_cost_networks, configs_success = build_custom_cost_networks(
                city, preprocess_in_background=True
            )

            with self.rlock:
                if custom_cost_networks:
                    self.set_custom_cost_networks(custom_cost_networks)
                if configs_success:
                    self.set_configs(configs_success)

            latest_fetch_aqi_timestamp = self.get_latest_fetch_aqi_timestamp()
            self.set_latest_build_aqi_timestamp(latest_fetch_aqi_timestamp)

            print(f"Latest fetch aqi timestamp: {latest_fetch_aqi_timestamp}")

            logging.info(
                f"Finished building {len(self.custom_cost_networks)} custom cost networks"
            )
        except Exception as e:
            logging.info(f"Error during network building: {e}")
        finally:
            # Ensure update_in_progress is reset whether the task succeeds or fails
            self.set_update_in_progress(False)
