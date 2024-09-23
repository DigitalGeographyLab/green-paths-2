import zipfile
import requests
import os
import shutil

from ..config import LATEST_FETCH_AQI_TIMESTAMP_KEY
from .network_builder_singleton import network_builder_instance
from .redis_client_singleton import redis_client


import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


from datetime import datetime, timedelta, timezone

from .celery_worker import run_aqi_preprocessing

# example path:
# url = "https://enfusernow2.s3.eu-central-1.amazonaws.com/Finland/pks/allPollutants_2024-09-18T22.zip"


class AQIUpdater:

    def __init__(self):
        self.current_aqi_name = None
        self.aws_base_url = (
            "https://enfusernow2.s3.eu-central-1.amazonaws.com/Finland/pks/"
        )
        self.aqi_temp_dir_path = "green_paths_2/src/API/temp_aqis"
        self.gp2_aqi_data_dir = "green_paths_2/src/API/data/aqi"
        self.latest_file_timestamp = None
        self.aqi_data_master_name = "aqi_allpollutants_pks.nc"

    def get_latest_file_timestamp(self):
        return self.latest_file_timestamp

    def set_latest_file_timestamp(self, timestamp):
        self.latest_file_timestamp = timestamp

    def get_current_aqi_name(self):
        return self.current_aqi_name

    def set_current_aqi_name(self, aqi_name):
        self.current_aqi_name = aqi_name

    def set_latest_fetch_aqi_timestamp(self, timestamp):
        redis_client.set(LATEST_FETCH_AQI_TIMESTAMP_KEY, timestamp)

    def generate_timestamp_string(self, hours_ago=1):
        # Get current time and subtract hours_ago hours
        current_time = datetime.now(timezone.utc).astimezone() - timedelta(
            hours=hours_ago
        )
        # Format the string as 'YYYY-MM-DDTHH'
        timestamp_string = current_time.strftime("%Y-%m-%dT%H")
        return timestamp_string

    def download_aqi_file(self, url, output_path):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                logging.info(f"File downloaded successfully and saved to {output_path}")
            else:
                return False

            # Check if the file was downloaded successfully
            if os.path.exists(output_path):
                return True
            else:
                logging.info(
                    f"Failed to download file. Status code: {response.status_code}"
                )
                return False

        except Exception as e:
            return False

    def _fetch_aqi_zip_from_aws(self):
        timestamp = self.generate_timestamp_string()
        logging.info(f"Fetching AQI data from AWS for timestamp: {timestamp}")
        file_name = f"allPollutants_{timestamp}.zip"
        url = os.path.join(self.aws_base_url, file_name)
        output_path = os.path.join(self.aqi_temp_dir_path, file_name)
        aqi_zip_download_success = self.download_aqi_file(url, output_path)
        return aqi_zip_download_success, file_name, output_path, timestamp

    def _unzip_aqi_file(self, aqi_zip_path, aq_target_file_name):
        zip_archive = zipfile.ZipFile(rf"{aqi_zip_path}", "r")
        # loop over files in zip archive
        for file_name in zip_archive.namelist():
            if aq_target_file_name in file_name:
                zip_archive.extract(file_name, self.aqi_temp_dir_path)
                return file_name

    def move_and_replace_file(self, new_file_path, old_file_path):
        # Check if the destination file already exists
        if os.path.exists(old_file_path):
            logging.info(f"File {old_file_path} exists, replacing it.")

        # Move the file, and it will overwrite the old one if it exists
        shutil.move(new_file_path, old_file_path)
        logging.info(f"File moved to {old_file_path}")

    def clean_temp_aqi_files(self):
        # empty the temp directory, including .zip files
        for file in os.listdir(self.aqi_temp_dir_path):
            file_path = os.path.join(self.aqi_temp_dir_path, file)
            try:
                if os.path.isfile(file_path) and (
                    file.endswith(".zip") or not file.endswith(".zip")
                ):
                    os.unlink(file_path)
                    logging.info(f"Deleted {file_path}")
            except Exception as e:
                logging.info(f"Failed to delete {file_path}. Reason: {e}")

    def download_aqi_data_from_enfuser_aws(self):
        try:
            aqi_zip_download_success, aqi_file_name, aqi_zip_path, timestamp = (
                self._fetch_aqi_zip_from_aws()
            )

            if not aqi_zip_download_success:
                logging.info("Failed to download AQI data from Enfuser AWS.")
                return False, None

            current_aqi_name = self.get_current_aqi_name()

            if (
                current_aqi_name and current_aqi_name == aqi_file_name
            ) or timestamp == self.latest_file_timestamp:
                print("No new AQI data available.")
                return False, None

            # Unzip the downloaded file
            aqi_data_file_name = self._unzip_aqi_file(
                aqi_zip_path, aq_target_file_name="allPollutants"
            )

            latest_aqi_data_path = os.path.join(
                self.aqi_temp_dir_path, aqi_data_file_name
            )

            # move the data to replace the old aqi data
            old_aqi_master_data_path = os.path.join(
                self.gp2_aqi_data_dir, self.aqi_data_master_name
            )

            # move and replace the old aqi data with the new one
            self.move_and_replace_file(
                new_file_path=latest_aqi_data_path,
                old_file_path=old_aqi_master_data_path,
            )

            # remove the temp files
            self.clean_temp_aqi_files()

            self.set_latest_file_timestamp(timestamp)
            self.set_current_aqi_name(aqi_file_name)

            logging.info(f"Aqi data updated successfully {aqi_data_file_name}")
            return True, timestamp
        except Exception as e:
            logging.info(f"Failed to download and update AQI data. Error: {e}")
            return False, None

    def fetch_and_update_aqi_data_hourly_job(self, skip_preprocessing=False):
        # check if an update is still running to not start a new one
        # get the current status of the update from the network builder
        if network_builder_instance.get_update_in_progress():
            print(
                "Preprocessing and networks are currently updating, skipping AQI update."
            )
            return

        new_aqi_data_success, timestamp = self.download_aqi_data_from_enfuser_aws()
        self.set_latest_fetch_aqi_timestamp(timestamp)

        if new_aqi_data_success:
            logging.info(
                "Successfully downloaded new AQI data. Run preprocessing pipeline."
            )
            if not skip_preprocessing:

                # Trigger Celery task to run preprocessing in the background
                logging.info("Submitting task to Celery")
                result = run_aqi_preprocessing.delay()
                logging.info(f"Task submitted with ID: {result.id}")

            logging.info("new AQI data downloaded successfully")
        else:
            logging.info("Aqi data not updated, no new data or data fetch failed.")
