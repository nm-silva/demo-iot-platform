"""
This module contains the SQLAlchemy ORM models for the database tables.
"""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# Define the sensors and switches metadata tables
class SensorMetadata(Base):
    __tablename__ = "sensors_metadata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    min_data = Column(Float)
    max_data = Column(Float)
    sample_rate = Column(Float)


class SwitchMetadata(Base):
    __tablename__ = "switches_metadata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)


# Define the live data tables for sensors and switches
class SensorLiveData(Base):
    __tablename__ = "sensors_live_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=True)
    prev_value = Column(Float, nullable=True)
    timestamp = Column(Integer)


class SwitchLiveData(Base):
    __tablename__ = "switches_live_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    value = Column(Integer, nullable=True)
    timestamp = Column(Integer)
