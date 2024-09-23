from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from typing import List, Tuple

from shapely.geometry import MultiLineString, LineString


# EDGE SEGMENTS MODELS


class SegmentProperties(BaseModel):
    path_id: Optional[str] = Field(None)

    # this allows adding "extra" properties dynamically
    class Config:
        extra = "allow"


class EdgeFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: SegmentProperties

    # class Config:
    #     arbitrary_types_allowed = True


class EdgeFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[EdgeFeature]


# (FULL) PATH MODELS


class PathProperties(BaseModel):
    path_id: Optional[str] = Field(None)
    # travel_time: Optional[float] = Field(None)
    # length: Optional[float] = Field(None)

    # this allows adding "extra" properties dynamically
    class Config:
        extra = "allow"


class PathFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: PathProperties

    # class Config:
    #     arbitrary_types_allowed = True


class PathFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[PathFeature]


# REQUEST AND RESPONSE MODELS


# TODO: make take list of string if multiple cities supported
class BuildNetworksRequest(BaseModel):
    city: str


class RouteRequest(BaseModel):
    city: str
    exposure: str
    transportMode: str
    origin: Tuple[float, float]
    destination: Tuple[float, float]


class RouteResponse(BaseModel):
    city: str
    transportMode: str
    exposure: str
    latest_aqi_file_timestamp: str
    edge_FC: EdgeFeatureCollection
    path_FC: PathFeatureCollection
