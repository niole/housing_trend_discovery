from pydantic import BaseModel
from pydantic_extra_types.coordinate import Latitude, Longitude
from house_trend_discovery.data_gen.create_db_engine import engine
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import Uuid, Column, ForeignKey
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

class CountyModel(OrmBase):
    __tablename__ = 'county'
    id = Column('id', Uuid, primary_key=True)
    name: Mapped[str]
    state: Mapped[str]

class AssessmentUrlModel(OrmBase):
    __tablename__ = 'assessment_urls'
    id = Column('id', Uuid, primary_key=True)
    premise_id = Column(Uuid, ForeignKey('premise_details.id', ondelete="CASCADE"))
    url: Mapped[str]

class PremiseDetailsModel(OrmBase):
    __tablename__ = 'premise_details'

    id = Column('id', Uuid, primary_key=True)
    assessment_urls: Mapped[List["AssessmentUrlModel"]] = relationship(
        cascade="all,delete,delete-orphan", back_populates="premise_details", passive_deletes=True
    )
    premise_address: Mapped[str]
    year_assessed: Mapped[int]
    dollar_value: Mapped[int]
    county: Mapped["CountyModel"]  = relationship(
        cascade="all,delete,delete-orphan", back_populates="premise_details", passive_deletes=True
    )
    premise_location = Column('premise_location', Geography('POINT'))

    parcel_number: Mapped[Optional[str]] = None
    sq_feet: Mapped[Optional[int]] = None
    year_built: Mapped[Optional[int]] = None
    bed_count: Mapped[Optional[int]] = None
    bath_count: Mapped[Optional[float]] = None
    failure_reason: Mapped[Optional[str]] = None

CountyModel.__table__.drop(engine)
AssessmentUrlModel.__table__.drop(engine)
PremiseDetailsModel.__table__.drop(engine)

PremiseDetailsModel.__table__.create(engine)
CountyModel.__table__.create(engine)
AssessmentUrlModel.__table__.create(engine)
