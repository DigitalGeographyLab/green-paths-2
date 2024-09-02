""" Endpoints for the API """

# from fastapi import APIRouter
# from http.client import HTTPException
# import logging
# from green_paths_api import app, configs, custom_cost_networks

# from .green_paths_api import DESTINATION_CSV_NAME, ORIGIN_CSV_NAME, save_csv
# from .models import RouteRequest
# from ..config import OUTPUT_RESULTS_TABLE, ROUTING_RESULTS_TABLE, SEGMENT_STORE_TABLE
# from ..database_controller import DatabaseController
# from ..routing.main import (
#     handle_routing_and_saving_processes,
# )

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# router = APIRouter()


# @app.post("/route/")
# async def calculate_routes(app, request: RouteRequest):
#     logger.info(f"Received request: {request}, routing starting...")
#     # Save CSV files in the static directory
#     logger.info("Init OD's from the request")
#     origin_csv_success = save_csv(request.origin[0], request.origin[1], ORIGIN_CSV_NAME)
#     destination_csv_success = save_csv(
#         request.destination[0], request.destination[1], DESTINATION_CSV_NAME
#     )

#     if not origin_csv_success or not destination_csv_success:
#         return HTTPException(
#             status_code=500, detail="Failed to process OD coordinates files."
#         )

#     db_handler = DatabaseController()

#     logger.info("Empty tables: routing_results and output_results")
#     db_handler.empty_table(ROUTING_RESULTS_TABLE)
#     db_handler.empty_table(OUTPUT_RESULTS_TABLE)

#     for config_key, config_object in configs.items():
#         logger.info(f"Routing for config: {config_key}")
#         # loop all configs and their custom cost networks
#         handle_routing_and_saving_processes(
#             db_handler=db_handler,
#             user_config=config_object,
#             custom_cost_transport_network=custom_cost_networks[config_key],
#         )
#         logger.info(f"Routing success for {config_key}")

#     # get all routing results...
#     # need to get all geometries from the current run...

#     # get all output db
#     logger.info("Getting all output results from db")
#     all_test = db_handler.get_all(OUTPUT_RESULTS_TABLE)
#     logger.info(f"all_test: {all_test}")

#     return {
#         "city": request.city,
#         "exposures": all_test,
#     }


# app.include_router(router)

# Simulated response
# return {
#     "city": request.city,
#     "exposures": request.exposures,
#     "origin": request.origin,
#     "destination": request.destination,
#     "route": "Simulated route data",
# }

# @app.post("/get_routes/", response_model=RouteResponse)
# async def get_routes(
#     city: str, origin: Tuple[float, float], destination: Tuple[float, float]
# ):
#     segments = generate_segments()
#     path_geometry = generate_path_geometry()

#     edge_FC = FeatureCollection(features=segments)
#     path_FC = PathFeatureCollection(features=[path_geometry])

#     return RouteResponse(
#         city=city,
#         origin=origin,
#         destination=destination,
#         edge_FC=edge_FC,
#         path_FC=path_FC,
#     )
