""" TODO """

# Code is based on Green Paths 1 project: <URL tähän>
import certifi
import ssl
import requests

import os
from typing import Dict
import fiona
from geopandas import gpd
from dataclasses import dataclass
from enum import Enum
from requests import Request
from functools import partial

from src.logging import setup_logger

# TODO this isn't working... -> fix it
# says that incomplete data fetching XXX bytes... -> timeout?
# maybe alter this code to use some other approach? for fething like requests
# note: code mainly from GP1


# Set a longer timeout
os.environ["GDAL_HTTP_TIMEOUT"] = "100000"

# Use certifi's certificates for SSL requests
ssl._create_default_https_context = ssl._create_unverified_context

hsy_wfs_url = "https://kartta.hsy.fi/geoserver/wfs"

LOG = setup_logger(__name__)


@dataclass
class VegetationLayers:
    low_vegetation: gpd.GeoDataFrame
    low_vegetation_parks: gpd.GeoDataFrame = None
    trees_2_10m: gpd.GeoDataFrame = None
    trees_10_15m: gpd.GeoDataFrame = None
    trees_15_20m: gpd.GeoDataFrame = None
    trees_20m: gpd.GeoDataFrame = None


class HsyWfsLayerName(Enum):
    low_vegetation = "matala_kasvillisuus"
    low_vegetation_parks = "maanpeite_muu_avoin_matala_kasvillisuus_2018"
    trees_2_10m = "maanpeite_puusto_2_10m_2018"
    trees_10_15m = "maanpeite_puusto_10_15m_2018"
    trees_15_20m = "maanpeite_puusto_15_20m_2018"
    trees_20m = "maanpeite_puusto_yli20m_2018"


def __fetch_wfs_layer(
    url: str,
    layer: str,
    version: str = "1.0.0",
    request: str = "GetFeature",
) -> gpd.GeoDataFrame:
    params = dict(
        service="WFS",
        version=version,
        request=request,
        typeName=layer,
        outputFormat="json",
    )
    q = Request("GET", url, params=params).prepare().url
    return gpd.read_file(q)


def fetch_hsy_vegetation_layers(land_cover_cache_gpkg: str) -> VegetationLayers:
    fetch_wfs_layer = partial(__fetch_wfs_layer, hsy_wfs_url)
    fetched_layers = []
    if os.path.exists(land_cover_cache_gpkg):
        fetched_layers = fiona.listlayers(land_cover_cache_gpkg)
    LOG.info(f"Previously fetched layers: {fetched_layers}")

    layers: Dict[HsyWfsLayerName, gpd.GeoDataFrame] = {}

    for idx, layer_name in enumerate(HsyWfsLayerName):
        if layer_name.name in fetched_layers:
            LOG.info(
                f"Loading layer {idx+1}/{len(HsyWfsLayerName)}: {layer_name.name} from cache"
            )
            gdf = gpd.read_file(land_cover_cache_gpkg, layer=layer_name.name)
            layers[layer_name.name] = gdf
        else:
            LOG.info(
                f'Fetching WFS layer {idx+1}/{len(HsyWfsLayerName)}: {layer_name.name} from "{layer_name.value}"'
            )
            gdf = fetch_wfs_layer(layer_name.value)
            # gdf.drop(gdf.columns.difference(["geometry"]), 1, inplace=True)
            gdf.to_file(land_cover_cache_gpkg, layer=layer_name.name, driver="GPKG")
            layers[layer_name.name] = gdf

    LOG.info("Loaded all land cover layers")
    return VegetationLayers(**layers)


fetch_hsy_vegetation_layers("src/data/cache/and_cover_cache.gpkg")
