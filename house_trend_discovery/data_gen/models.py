from pydantic import BaseModel
from pydantic_extra_types.coordinate import Latitude, Longitude
from house_trend_discovery.data_gen.create_db_engine import engine
import sqlalchemy as sa
from sqlalchemy import Uuid
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional, List
from geoalchemy2 import Geography

OrmBase = declarative_base()

class LatLng(BaseModel):
    lat: Latitude
    lng: Longitude

    class Config:
        orm_mode = True

class County(BaseModel):
    name: str
    state: str

    class Config:
        orm_mode = True

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

class PremiseDetails(BaseModel):
    assessment_urls: List[Optional[str]]
    premise_address: str
    year_assessed: int
    dollar_value: int
    county: County
    premise_location: LatLng

    parcel_number: Optional[str] = None
    sq_feet: Optional[int] = None
    year_built: Optional[int] = None
    bed_count: Optional[int] = None
    bath_count: Optional[float] = None
    failure_reason: Optional[str] = None

    class Config:
        orm_mode = True

# SQLAlchemy models

class PremiseDetailsModel(OrmBase):
    __tablename__ = 'premise_details'

    id = sa.Column('id', Uuid, primary_key=True)
    assessment_urls = sa.Column('assessment_urls', sa.String())
    premise_address = sa.Column('premise_address', sa.String())
    year_assessed = sa.Column('year_assessed', sa.Integer())
    dollar_value = sa.Column('dollar_value', sa.Integer())

    premise_location = sa.Column('premise_location', Geography('POINT'))

#PremiseDetailsModel.__table__.drop(engine)
PremiseDetailsModel.__table__.create(engine)
