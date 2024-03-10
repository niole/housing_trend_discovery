from pydantic import BaseModel
from pydantic_extra_types.coordinate import Latitude, Longitude

class LatLng(BaseModel):
    lat: Latitude
    lng: Longitude

class Area(BaseModel):
    query: str
    address: str
    county: str
    ne_bound: LatLng
    sw_bound: LatLng
    location: LatLng

class Location(BaseModel):
    address: str
    county: str
    location: LatLng
