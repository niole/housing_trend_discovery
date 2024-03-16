from pydantic import BaseModel
from pydantic_extra_types.coordinate import Latitude, Longitude
from typing import Optional, List

class LatLng(BaseModel):
    lat: Latitude
    lng: Longitude

class County(BaseModel):
    name: str
    state: str

class Area(BaseModel):
    query: str
    address: str
    county: County
    ne_bound: LatLng
    sw_bound: LatLng
    location: LatLng

class Location(BaseModel):
    address: str
    county: County
    location: LatLng

class PremiseScrapeResult(BaseModel):
    assessment_urls: List[Optional[str]]
    premise_address: str
    year_assessed: int
    dollar_value: int
    parcel_number: Optional[str] = None
    sq_feet: Optional[int] = None
    year_built: Optional[int] = None
    bed_count: Optional[int] = None
    bath_count: Optional[float] = None
    failure_reason: Optional[str] = None

class PremiseDetails(PremiseScrapeResult):
    county: County
    premise_location: LatLng
