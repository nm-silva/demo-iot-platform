"""
This module contains the device manager class, to manage multiple devices.
"""

from devices.sensors.sensor import Sensor
from devices.switches.switch import Switch
from devices.switches.passive_switch import PassiveSwitch
from devices.errors import (
    DeviceNotFoundError,
    DeviceTypeError,
    DeviceAlreadyExistsError,
)
from devices.utils import get_sensor_data_with_timeout
from typing import Tuple, Union, Dict
import logging

logger = logging.getLogger(__name__)


class DeviceManager:
    """
    This class represents a device manager, which can manage multiple devices.
    """

    def __init__(self) -> None:
        self._devices: Dict[str, Union[Sensor, Switch]] = {}

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
        if isinstance(device, PassiveSwitch):
            self.enable_switch(device.name)

    def remove_device(self, name: str) -> None:
        """
        Removes a device from the device manager.
        """
        if name in self._devices:
            device = self._devices[name]
            if isinstance(device, (Sensor, PassiveSwitch)):
                device.stop()
            del self._devices[name]
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

    def get_switch_state(self, name: str, type_check: bool = True) -> Union[bool, None]:
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

    def get_all_switch_states(self) -> Dict[str, Union[bool, None]]:
        """
        Returns the state of all switch devices managed by the device manager.
        """
        states: Dict[str, Union[bool, None]] = {}
        for device_name in self._devices.keys():
            value = self.get_switch_state(device_name, type_check=False)
            if value is not None:
                states[device_name] = value
        return states

    def get_sensor_data(
        self, name: str, type_check: bool = True
    ) -> Union[Tuple[Union[int, float, None], Union[int, float, None]], None]:
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
    ) -> Dict[str, Tuple[Union[int, float, None], Union[int, float, None]]]:
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
