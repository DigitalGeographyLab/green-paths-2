import sys
import sqlite3
import traceback
import uuid
import logging

from contextlib import asynccontextmanager

from .network_builder_singleton import network_builder_instance as network_builder
from .redis_client_singleton import redis_client

from .aqi_updater import AQIUpdater
from ..exposure_analysing.process_path_batches import (
    process_exposure_results_as_batches,
)
from ..exposure_analysing.main import (
    get_data_names,
    init_exposure_handlers,
)

from fastapi import BackgroundTasks

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    EdgeFeatureCollection,
    PathFeatureCollection,
    RouteRequest,
    RouteResponse,
)
from ..config import (
    ANALYSING_KEY,
    API_EXPOSURES_NAME_MAPPING,
    DESTINATION_CSV_NAME,
    KEEP_GEOMETRY_KEY,
    ORIGIN_CSV_NAME,
    OUTPUT_RESULTS_TABLE,
    PROJECT_CRS_KEY,
    PROJECT_KEY,
    ROUTING_RESULTS_TABLE,
    SEGMENT_STORE_TABLE,
    TRAVEL_TIMES_TABLE,
    HElSINKI_CITY_KEY,
)
from ..database_controller import DatabaseController
from ..routing.main import (
    handle_routing_and_saving_processes,
)

from .api_utility_engine import (
    build_custom_cost_networks,
    convert_segments_to_features,
    create_path_feature,
    filter_edges_based_on_pathid,
    filter_too_similar_paths,
    get_individual_segments_using_routing_results,
    save_csv,
)


# Set up logger to print to the terminal
def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)  # Send log output to terminal
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)
    return logger


# Initialize logger
logger = setup_logger(__name__)

# TODO: this should be set to the IP and/or domain of the server
# atm we dont know the domain, so leaving this as wildcard
# as the server's security group should handle the access by only the allowed IP's / domains


aqi_updater = AQIUpdater()
db_controller = DatabaseController()

executors = {"default": ThreadPoolExecutor(1)}  # Limit to 1

scheduler = BackgroundScheduler(executors=executors)
scheduler.add_job(aqi_updater.fetch_and_update_aqi_data_hourly_job, "interval", hours=1)
scheduler.start()


# Using lifespan to handle startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        networks_initialized = network_builder.get_build_networks_initialized()
        if not networks_initialized:
            network_builder.init_preprocessing_and_custom_cost_networks(
                db_controller, aqi_updater
            )
        else:
            logger.info("Custom cost networks already initialized")

        yield

    except Exception as e:
        logger.error(f"Error during lifespan startup: {e}")
        logger.error(traceback.format_exc())  # This will log the full traceback
    finally:
        # Ensure scheduler is stopped during shutdown
        scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.router.lifespan_context = lifespan

# Configure CORS settings
# TODO: allow_origins might need to be changed to the actual domain of the frontend for security reasons

# add cors middleware for making request from same origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ENDPOINTS


@app.post("/route/")
async def calculate_routes(request: RouteRequest, background_tasks: BackgroundTasks):
    try:
        if not network_builder.get_build_networks_initialized():
            logger.error("Custom cost networks not initialized.")
            raise HTTPException(
                status_code=500,
                detail="Custom cost networks not initialized. Try again in a minute!",
            )

        logger.info(f"Received request: {request}, routing starting...")
        # Save CSV files in the static directory
        logger.info("Init OD's from the request")
        origin_csv_success = save_csv(
            request.origin[0], request.origin[1], ORIGIN_CSV_NAME, 0
        )
        destination_csv_success = save_csv(
            request.destination[0], request.destination[1], DESTINATION_CSV_NAME, 1
        )
        logger.info("Inited OD's successfully")

        if not origin_csv_success or not destination_csv_success:
            return HTTPException(
                status_code=500, detail="Failed to process OD coordinates files."
            )

        all_edge_FC = []
        all_path_FC = []
        output_table_all_columns = set()

        db_handler = DatabaseController()

        _, exposure_db_controller, exposure_calculator = init_exposure_handlers(
            db_handler
        )

        logger.info("Inited exposure handlers successfully")

        # TODO: this should maybe be a class?
        # Filter the configs and custom cost networks for the requested city and exposure
        city_exposure_filtered_configs = {
            key: value
            for key, value in network_builder.get_configs().items()
            if key.lower().startswith(
                f"{request.city.lower()}/{request.exposure.lower()}/"
            )
        }

        # Flag for only getting the travel times once
        no_travel_times = False

        logger.info("Looping through the API configs for given exposure")
        logger.info(f"all configs keys: {city_exposure_filtered_configs.keys()}")

        custom_cost_networks_instance = (
            network_builder.get_custom_cost_networks().copy()
        )

        # create unique user id
        user_id = str(uuid.uuid4())

        # loop all configs and their custom cost networks
        for config_key, config_object in city_exposure_filtered_configs.items():
            logger.info(f"Routing for config: {config_key}")
            current_network = custom_cost_networks_instance[config_key]
            # empty the travel times for the network
            current_network.reset_base_travel_times()

            try:
                handle_routing_and_saving_processes(
                    db_handler=db_handler,
                    user_config=config_object,
                    custom_cost_transport_network=current_network,
                    no_travel_times=no_travel_times,
                    transportMode=request.transportMode,
                    user_id=user_id,
                )
            except:
                raise HTTPException(
                    status_code=500, detail="GP2 SERVER ROUTING FAILED."
                )

            no_travel_times = True

            # get data names as list so that we can loop each different data source
            data_names = get_data_names(user_config=config_object)

            keep_geometries = config_object.get_nested_attribute(
                [ANALYSING_KEY, KEEP_GEOMETRY_KEY], default=False
            )

            project_crs = config_object.get_nested_attribute(
                [PROJECT_KEY, PROJECT_CRS_KEY], default=False
            )

            # emptying the table after each loop to only have a single output results in table
            if db_handler.check_table_exists(OUTPUT_RESULTS_TABLE):
                db_handler.empty_table(OUTPUT_RESULTS_TABLE, user_id=user_id)

            try:
                new_columns_added_db = process_exposure_results_as_batches(
                    db_handler=db_handler,
                    exposure_db_controller=exposure_db_controller,
                    exposure_calculator=exposure_calculator,
                    user_config=config_object,
                    data_names=data_names,
                    keep_geometries=keep_geometries,
                    existing_columns=output_table_all_columns,
                    user_id=user_id,
                    combine_geometries=False,
                )

            except Exception as e:
                logger.error(f"GP2 SERVER EXPOSURE ANALYSING FAILED: {e}")
                raise HTTPException(
                    status_code=500, detail="GP2 SERVER EXPOSURE ANALYSING FAILED."
                )

            if new_columns_added_db:
                output_table_all_columns.update(new_columns_added_db)

            # EDGES

            edge_exposure_data_name = API_EXPOSURES_NAME_MAPPING[request.exposure]

            edge_rows = get_individual_segments_using_routing_results(
                db_handler=db_handler,
                data_name=edge_exposure_data_name,
                user_id=user_id,
            )

            current_path_edge_FC = convert_segments_to_features(
                segments_data=edge_rows,
                data_name=edge_exposure_data_name,
                path_id=config_key,
                source_crs=project_crs,
            )

            all_edge_FC.extend(current_path_edge_FC)

            # PATH

            path_output_results, _ = db_handler.get_all(
                OUTPUT_RESULTS_TABLE, column_names=True, user_id=user_id
            )

            current_path_FC = create_path_feature(
                path_output_result=path_output_results[0],
                path_id=config_key,
                exposure=request.exposure,
                source_crs=project_crs,
            )

            if current_path_FC:
                all_path_FC.append(current_path_FC)

            # sort the path features by time, fastest first
            all_path_FC = sorted(
                all_path_FC, key=lambda x: getattr(x.properties, "Time", float("inf"))
            )

        try:
            # filter out path feature that have too similar geometry
            logger.info(f"total number of paths before filtering: {len(all_path_FC)}")
            filtered_path_fc = filter_too_similar_paths(all_path_FC=all_path_FC)
            logger.info(
                f"total number of paths after filtering: {len(filtered_path_fc)}"
            )

            # filter edges base on kept paths
            filtered_edge_FC = filter_edges_based_on_pathid(
                all_path_FC=filtered_path_fc, all_edge_FC=all_edge_FC
            )
        except Exception as e:
            logger.error(f"Error in filtering paths and edges: {e}")
            logger.info("Will just return all paths and edges")
            filtered_path_fc = all_path_FC
            filtered_edge_FC = all_edge_FC

        # empty the tables after routing with user-id
        background_tasks.add_task(
            db_handler.empty_table, ROUTING_RESULTS_TABLE, user_id=user_id
        )
        background_tasks.add_task(
            db_handler.empty_table, OUTPUT_RESULTS_TABLE, user_id=user_id
        )

        # latest build aqi file timestamp
        latest_aqi_build_timestamp = (
            redis_client.get("latest_build_aqi_timestamp") or ""
        )

        return RouteResponse(
            city=request.city,
            transportMode=request.transportMode,
            exposure=request.exposure,
            latest_aqi_file_timestamp=latest_aqi_build_timestamp,
            edge_FC=EdgeFeatureCollection(features=filtered_edge_FC),
            path_FC=PathFeatureCollection(features=filtered_path_fc),
        )

    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            # Handle the specific database lock error
            raise HTTPException(
                status_code=503,
                detail="Too many concurrent users, try again in a few seconds.",
            )
        else:
            raise HTTPException(status_code=500, detail="Database operation failed.")
    except HTTPException as http_exc:
        logger.error(f"HTTPException occurred: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unhandled exception in calculate_routes: {e}")
        raise HTTPException(
            status_code=500,
            detail=e.args[0] if e.args else "Unhandled exception in calculate_routes",
        )


# Running the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
