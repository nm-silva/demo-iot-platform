"""
This module contains the device manager class, to manage multiple devices.
"""

from app.ws_utils import notify_sensor_ws, notify_switch_ws
from devices.sensors.sensor import Sensor
from devices.switches.switch import Switch
from devices.switches.passive_switch import PassiveSwitch
from devices.errors import (
    DeviceNotFoundError,
    DeviceTypeError,
    DeviceAlreadyExistsError,
)
from devices.utils import get_sensor_data_with_timeout
from db.manager import DatabaseManager
from typing import Optional, Tuple, Union, Dict
import logging

logger = logging.getLogger(__name__)


class DeviceManager:
    """
    This class represents a device manager, which can manage multiple devices.
    """

    def __init__(self, db_path: str) -> None:
        self._devices: Dict[str, Union[Sensor, Switch]] = {}
        self._db_manager: DatabaseManager = DatabaseManager(db_path=db_path)
        self._db_manager.connect()
        self._load_devices()

    def __del__(self) -> None:
        self._db_manager.close()

    def _load_devices(self) -> None:
        """
        This method loads devices from the database.
        """
        sensors = self._db_manager.get_all_sensor_metadata()
        switches = self._db_manager.get_all_switch_metadata()

        for sensor in sensors:
            self.add_device(
                Sensor(
                    name=sensor["name"],  # type: ignore
                    min=sensor["min_data"],  # type: ignore
                    max=sensor["max_data"],  # type: ignore
                    sample_rate=sensor["sample_rate"],  # type: ignore
                )
            )

        for switch in switches:
            if switch["type"] == "passive_switch":
                self.add_device(PassiveSwitch(switch["name"]))  # type: ignore
            else:
                self.add_device(Switch(switch["name"]))  # type: ignore

    @property
    def devices(self) -> Dict[str, Union[Sensor, Switch]]:
        """
        Returns a dict of all devices managed by the device manager.
        """
        return self._devices

    def add_device(self, device: Union[Sensor, Switch]) -> None:
        """
        Adds a device to the device manager.
        """
        if device.name in self._devices:
            raise DeviceAlreadyExistsError(
                f"Device with name '{device.name}' already exists."
            )

        self._devices[device.name] = device
        if isinstance(device, Sensor):
            self.enable_sensor(device.name)
            self._db_manager.insert_sensor_metadata(device)
        else:
            if isinstance(device, PassiveSwitch):
                self.enable_switch(device.name)
            self._db_manager.insert_switch_metadata(device)

    def remove_device(self, name: str) -> None:
        """
        Removes a device from the device manager.
        """
        if name in self._devices:
            device = self._devices[name]
            if isinstance(device, (Sensor, PassiveSwitch)):
                device.stop()
            del self._devices[name]
            self._db_manager.delete_device(name)
        else:
            raise DeviceNotFoundError(f"Device with name '{name}' not found.")

    def enable_sensor(self, name: str, type_check: bool = True) -> None:
        """
        Enables a sensor device managed by the device manager.
        """
        if name not in self._devices:
            raise DeviceNotFoundError(f"Device with name '{name}' not found.")

        device = self._devices[name]

        if not isinstance(device, Sensor):
            if type_check:
                raise DeviceTypeError(f"Device with name '{name}' is not a sensor.")
            return None
        device.update_callbacks.notify_sensor_ws = notify_sensor_ws  # type: ignore
        device.update_callbacks.update_sensor_live_data = (  # type: ignore
            self._db_manager.insert_sensor_live_data
        )
        device.start()

    def enable_all_sensors(self) -> None:
        """
        Enables all sensor devices managed by the device manager.
        """
        for device_name in self._devices.keys():
            self.enable_sensor(device_name)

    def enable_switch(self, name: str, type_check: bool = True) -> None:
        """
        Enables a switch device managed by the device manager.
        """
        if name not in self._devices:
            raise DeviceNotFoundError(f"Device with name '{name}' not found.")

        device = self._devices[name]

        if not isinstance(device, PassiveSwitch):
            if type_check:
                raise DeviceTypeError(
                    f"Device with name '{name}' is not a passive switch."
                )
            return None
        device.update_callbacks.notify_switch_ws = notify_switch_ws  # type: ignore
        device.update_callbacks.update_switch_live_data = (  # type: ignore
            self._db_manager.insert_switch_live_data
        )
        device.enable_switch()

    def enable_all_switches(self) -> None:
        """
        Enables all switch devices managed by the device manager.
        """
        for device_name in self._devices.keys():
            self.enable_switch(device_name, type_check=False)

    def set_switch(self, name: str, state: bool, type_check: bool = True) -> None:
        """
        Sets the state of a switch device managed by the device manager.
        """
        if name not in self._devices:
            raise DeviceNotFoundError(f"Device with name '{name}' not found.")

        if not isinstance(state, bool):
            raise ValueError("State must be a boolean.")

        device = self._devices[name]

        if not isinstance(device, Switch):
            if type_check:
                raise DeviceTypeError(f"Device with name '{name}' is not a switch.")
            return None

        if isinstance(device, PassiveSwitch):
            if type_check:
                raise DeviceTypeError(f"Device with name '{name}' is a passive switch.")
            return None

        device.set_state(state)

    def set_all_switches(self, state: bool) -> None:
        """
        Turns on all switches managed by the device manager.
        """
        for device_name in self._devices.keys():
            self.set_switch(device_name, state, type_check=False)

    def get_switch_state(
        self, name: str, type_check: bool = True
    ) -> Optional[Tuple[Union[bool, None], int]]:
        """
        Returns the state of a switch device managed by the device manager.
        """
        if name not in self._devices:
            raise DeviceNotFoundError(f"Device with name '{name}' not found.")

        device = self._devices[name]

        if not isinstance(device, Switch):
            if type_check:
                raise DeviceTypeError(f"Device with name '{name}' is not a switch.")
            return None

        return device.state

    def get_all_switch_states(self) -> Dict[str, Tuple[Union[bool, None], int]]:
        """
        Returns the state of all switch devices managed by the device manager.
        """
        states: Dict[str, Tuple[Union[bool, None], int]] = {}
        for device_name in self._devices.keys():
            value = self.get_switch_state(device_name, type_check=False)
            if value is not None:
                states[device_name] = value
        return states

    def get_sensor_data(
        self, name: str, type_check: bool = True
    ) -> Union[Tuple[Union[int, float, None], Union[int, float, None], int], None]:
        """
        Returns the data a sensor device managed by the device manager.
        """
        if name not in self._devices:
            raise DeviceNotFoundError(f"Device with name '{name}' not found.")

        device = self._devices[name]

        if not isinstance(device, Sensor):
            if type_check:
                raise DeviceTypeError(f"Device with name '{name}' is not a sensor.")
            return None

        try:
            return get_sensor_data_with_timeout(device, timeout=6)
        except TimeoutError:
            raise TimeoutError(f"Sensor '{name}' timed out.")

    def get_all_sensor_data(
        self,
    ) -> Dict[str, Tuple[Union[int, float, None], Union[int, float, None], int]]:
        """
        Returns the data of all sensor devices managed by the device manager.
        """
        data = {}
        for device_name in self._devices.keys():
            values = self.get_sensor_data(device_name, type_check=False)
            if values is not None:
                data[device_name] = values
        return data

    def set_sensor_sample_rate(self, name: str, sample_rate: int) -> None:
        """
        Sets the sample rate of a sensor device managed by the device manager.
        """
        if name not in self._devices:
            raise DeviceNotFoundError(f"Device with name '{name}' not found.")

        device = self._devices[name]

        if not isinstance(device, Sensor):
            raise DeviceTypeError(f"Device with name '{name}' is not a sensor.")

        device.set_sample_rate(sample_rate)
