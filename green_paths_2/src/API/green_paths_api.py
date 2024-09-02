from contextlib import asynccontextmanager
from ..exposure_analysing.process_path_batches import (
    process_exposure_results_as_batches,
)
from ..exposure_analysing.main import (
    get_data_names,
    init_exposure_handlers,
)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Tuple
import logging
from .models import (
    BuildNetworksRequest,
    EdgeFeatureCollection,
    PathFeatureCollection,
    RouteRequest,
    RouteResponse,
)
from ..config import (
    ANALYSING_KEY,
    DESTINATION_CSV_NAME,
    KEEP_GEOMETRY_KEY,
    ORIGIN_CSV_NAME,
    OUTPUT_RESULTS_TABLE,
    PROJECT_CRS_KEY,
    PROJECT_KEY,
    ROUTING_RESULTS_TABLE,
)
from ..database_controller import DatabaseController
from ..routing.main import (
    handle_routing_and_saving_processes,
)

from .api_utility_engine import (
    build_custom_cost_networks,
    convert_segments_to_features,
    create_path_feature,
    get_individual_segments_using_routing_results,
    save_csv,
)


import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configure CORS settings
allowed_cors_origins = [
    "http://localhost:3000",
]

custom_cost_networks = {}
configs = {}


# Using lifespan to handle startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # TODO: replace the preprocessing_data with street network data build...
        global config_path
        global custom_cost_networks
        global configs

        # TODO: tee paremiin, ehkä support muita kaupunkeja...
        # täsä pitäs loopata ihan kaikki läpi mitä on...
        city = "hki"

        custom_cost_networks, configs = build_custom_cost_networks(city_name=city)
        logger.info(f"Created {len(custom_cost_networks)} custom cost networks")
        logger.info(f"Custom cost networks: {custom_cost_networks.keys()}")
        logger.info("Success in lifespan")
    except Exception as e:
        logger.info(f"Error during lifespan startup: {e}")

    yield
    # Cleanup if necessary here (runs on shutdown)


app = FastAPI(lifespan=lifespan)
app.router.lifespan_context = lifespan

# add cors middleware for making request from same origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ENDPOINTS


@app.post("/build_networks/")
async def build_networks(request: BuildNetworksRequest):
    """
    Endpoint to build custom cost networks for a specified city.
    """
    logger.info("STARTING TO BUILD CUSTOM COST NETWORKS")

    # Build custom cost networks based on the request's city parameter
    global custom_cost_networks, configs
    try:
        custom_cost_networks, configs = build_custom_cost_networks(request.city)
        logger.info(
            f"Finished building {len(custom_cost_networks)} custom cost networks"
        )
        logger.info(f"Custom cost networks created: {custom_cost_networks.keys()}")

        return {"status": "success", "networks_built": len(custom_cost_networks)}
    except Exception as e:
        logger.error(f"Error during network building: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to build custom cost networks."
        )


@app.post("/route/")
async def calculate_routes(request: RouteRequest):
    try:
        logger.info(f"Received request: {request}, routing starting...")
        # Save CSV files in the static directory
        logger.info("Init OD's from the request")
        origin_csv_success = save_csv(
            request.origin[0], request.origin[1], ORIGIN_CSV_NAME, 0
        )
        destination_csv_success = save_csv(
            request.destination[0], request.destination[1], DESTINATION_CSV_NAME, 1
        )

        if not origin_csv_success or not destination_csv_success:
            return HTTPException(
                status_code=500, detail="Failed to process OD coordinates files."
            )

        all_edge_FC = []
        all_path_FC = []
        output_table_all_columns = set()

        db_handler = DatabaseController()

        logger.info("Empty tables: routing_results and output_results")
        db_handler.empty_table(ROUTING_RESULTS_TABLE)
        db_handler.empty_table(OUTPUT_RESULTS_TABLE)

        _, exposure_db_controller, exposure_calculator = init_exposure_handlers(
            db_handler
        )

        for config_key, config_object in configs.items():
            logger.info(f"Routing for config: {config_key}")
            # loop all configs and their custom cost networks

            try:
                handle_routing_and_saving_processes(
                    db_handler=db_handler,
                    user_config=config_object,
                    custom_cost_transport_network=custom_cost_networks[config_key],
                )
            except:
                raise HTTPException(
                    status_code=500, detail="GP2 SERVER ROUTING FAILED."
                )

            # get data names as list so that we can loop each different data source
            data_names = get_data_names(user_config=config_object)

            keep_geometries = config_object.get_nested_attribute(
                [ANALYSING_KEY, KEEP_GEOMETRY_KEY], default=False
            )

            project_crs = config_object.get_nested_attribute(
                [PROJECT_KEY, PROJECT_CRS_KEY], default=False
            )

            # emptying the table after each loop to only have a single output results in table
            db_handler.empty_table(OUTPUT_RESULTS_TABLE)

            try:
                new_columns_added_db = process_exposure_results_as_batches(
                    db_handler=db_handler,
                    exposure_db_controller=exposure_db_controller,
                    exposure_calculator=exposure_calculator,
                    user_config=config_object,
                    data_names=data_names,
                    keep_geometries=keep_geometries,
                    existing_columns=output_table_all_columns,
                )

            except:
                raise HTTPException(
                    status_code=500, detail="GP2 SERVER EXPOSURE ANALYSING FAILED."
                )

            if new_columns_added_db:
                output_table_all_columns.update(new_columns_added_db)

            # EDGES

            # get the normalized values for the segments, for visualization purposes in GUI
            normalized_data_names = [name + "_normalized" for name in data_names]

            edge_rows = get_individual_segments_using_routing_results(
                db_handler=db_handler, data_names=normalized_data_names
            )

            current_path_edge_FC = convert_segments_to_features(
                segments_data=edge_rows,
                data_names=normalized_data_names,
                path_id=config_key,
                source_crs=project_crs,
            )

            all_edge_FC.extend(current_path_edge_FC)

            # PATH

            path_output_results, _ = db_handler.get_all(
                OUTPUT_RESULTS_TABLE, column_names=True
            )

            current_path_FC = create_path_feature(
                path_output_result=path_output_results[0],
                path_id=config_key,
                source_crs=project_crs,
            )

            if current_path_FC:
                all_path_FC.append(current_path_FC)

        return RouteResponse(
            city=request.city,
            edge_FC=EdgeFeatureCollection(features=all_edge_FC),
            path_FC=PathFeatureCollection(features=all_path_FC),
        )

    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}")
        raise e(f"HTTP Exception: {e.detail}")
    except Exception as e:
        logger.error(f"Unhandled exception in calculate_routes: {e}")
        raise HTTPException(status_code=500, detail="GREEN PAHTS SERVER UNKNOWN ERROR.")


# ROOPE TODO: should this be done in frontend? i guess!
def geocode_address_to_lat_long(address: str) -> Tuple[float, float]:
    """TODO"""
    return True


# Running the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
