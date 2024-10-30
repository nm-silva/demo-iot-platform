"""
This module contains the database manager class, which is responsible for managing the database
connection and operations.
"""

import os
import logging
from db.errors import (
    DatabaseConnectionError,
    DatabaseInsertionError,
    DatabaseQueryError,
    DatabaseUpdateError,
    DatabaseDeletionError,
)
from typing import Dict, List, Optional, Tuple, Union
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db.models import (
    Base,
    SensorMetadata,
    SensorLiveData,
    SwitchMetadata,
    SwitchLiveData,
)
from devices.sensors.sensor import Sensor
from devices.switches.switch import Switch

DB_URL = "sqlite:///resources/database.db"

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self) -> None:
        self.db_url = DB_URL
        self._init_db()
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session: Optional[Session] = None

    def _init_db(self) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.join(current_dir, "..", "resources")
        db_path = os.path.join(resources_dir, "database.db")
        os.makedirs(resources_dir, exist_ok=True)

        if not os.path.exists(db_path):
            logger.info("Database file created successfully")
        else:
            logger.info("Database file already exists")

        self.db_url = f"sqlite:///{db_path}"

    def connect(self) -> None:
        if self.session is None:
            self.session = self.Session()
            logger.info("Database session started")

    def disconnect(self) -> None:
        if self.session:
            self.session.close()
            self.session = None
            logger.info("Database session closed")

    def insert_sensor_metadata(self, device: Sensor) -> None:
        self.connect()
        if self.session is None:
            raise DatabaseConnectionError("Database session not started")
        try:
            sensor = (
                self.session.query(SensorMetadata).filter_by(name=device.name).first()
            )
            if sensor is not None:
                logger.info(f"Sensor metadata '{device.name}' already exists")
                return None
            sensor = SensorMetadata(
                name=device.name,
                min_data=device.min_data,
                max_data=device.max_data,
                sample_rate=device.sample_rate,
            )
            self.session.add(sensor)
            self.session.commit()
            logger.info(f"Sensor metadata '{device.name}' inserted successfully")
        except Exception as e:
            self.session.rollback()
            raise DatabaseInsertionError(
                f"Failed to insert sensor metadata '{device.name}': {e}"
            )

    def insert_sensor_live_data(
        self,
        name: str,
        data: Tuple[Union[int, float, None], Union[int, float, None], int],
    ) -> None:
        self.connect()
        if self.session is None:
            raise DatabaseConnectionError("Database session not started")
        try:
            value, prev_value, timestamp = data
            sensor = SensorLiveData(
                name=name,
                value=value,
                prev_value=prev_value,
                timestamp=timestamp,
            )
            self.session.add(sensor)
            self.session.commit()
            logger.info(f"Sensor live data '{name}' inserted successfully")
        except Exception as e:
            self.session.rollback()
            raise DatabaseInsertionError(
                f"Failed to insert sensor live data '{name}': {e}"
            )

    def insert_switch_metadata(self, device: Switch) -> None:
        self.connect()
        if self.session is None:
            raise DatabaseConnectionError("Database session not started")
        try:
            switch = (
                self.session.query(SwitchMetadata).filter_by(name=device.name).first()
            )
            if switch is not None:
                logger.info(f"Switch metadata '{device.name}' already exists")
                return None
            switch = SwitchMetadata(name=device.name, type=device.type)
            self.session.add(switch)
            self.session.commit()
            logger.info(f"Switch metadata '{device.name}' inserted successfully")
        except Exception as e:
            self.session.rollback()
            raise DatabaseInsertionError(
                f"Failed to insert switch metadata '{device.name}': {e}"
            )

    def insert_switch_live_data(
        self, name: str, data: Tuple[Union[bool, None], int]
    ) -> None:
        self.connect()
        if self.session is None:
            raise DatabaseConnectionError("Database session not started")
        try:
            value, timestamp = data
            switch = SwitchLiveData(name=name, value=value, timestamp=timestamp)
            self.session.add(switch)
            self.session.commit()
            logger.info(f"Switch live data '{name}' inserted successfully")
        except Exception as e:
            self.session.rollback()
            raise DatabaseUpdateError(
                f"Failed to insert switch live data '{name}': {e}"
            )

    def get_all_sensor_metadata(self) -> List[Dict[str, object]]:
        self.connect()
        if self.session is None:
            raise DatabaseConnectionError("Database session not started")
        try:
            sensors = self.session.query(SensorMetadata).all()
            processed_data = []
            for sensor in sensors:
                processed_data.append(
                    {
                        "name": sensor.name,
                        "min_data": sensor.min_data,
                        "max_data": sensor.max_data,
                        "sample_rate": sensor.sample_rate,
                    }
                )
            return processed_data
        except Exception as e:
            raise DatabaseQueryError(f"Failed to retrieve sensor metadata: {e}")

    def get_all_switch_metadata(self) -> List[Dict[str, object]]:
        self.connect()
        if self.session is None:
            raise DatabaseConnectionError("Database session not started")
        try:
            switches = self.session.query(SwitchMetadata).all()
            processed_data = []
            for switch in switches:
                processed_data.append(
                    {
                        "name": switch.name,
                        "type": switch.type,
                    }
                )
            return processed_data  # type: ignore
        except Exception as e:
            raise DatabaseQueryError(f"Failed to retrieve switch metadata: {e}")

    def delete_device(self, name: str) -> None:
        self.connect()
        if self.session is None:
            raise DatabaseConnectionError("Database session not started")
        try:
            # Delete sensor metadata and live data
            sensor_metadata = (
                self.session.query(SensorMetadata).filter_by(name=name).first()
            )
            if sensor_metadata:
                self.session.delete(sensor_metadata)
                self.session.query(SensorLiveData).filter_by(name=name).delete()
                logger.info(
                    f"Sensor '{name}' metadata and live data deleted successfully"
                )

            # Delete switch metadata and live data
            switch_metadata = (
                self.session.query(SwitchMetadata).filter_by(name=name).first()
            )
            if switch_metadata:
                self.session.delete(switch_metadata)
                self.session.query(SwitchLiveData).filter_by(name=name).delete()
                logger.info(
                    f"Switch '{name}' metadata and live data deleted successfully"
                )

            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to delete device '{name}': {e}")
            raise DatabaseDeletionError(f"Failed to delete device '{name}': {e}")

    def close(self) -> None:
        self.disconnect()
        self.engine.dispose()
        logger.info("Database connection closed")
