"""
This module contains the classes for all server responses
"""

from typing import Any, Dict, Union, Tuple


class Response:
    def __init__(self) -> None:
        self.type = ""

    def to_dict(self) -> Dict[str, str]:
        return self.__dict__

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Response":
        return cls(**data)


class GetAllDevicesResponse(Response):
    def __init__(self, devices: Dict[str, Any]):
        self.type = "get_all_devices_response"
        self.devices = devices


class GetAllSwitchStatesResponse(Response):
    def __init__(self, states: Dict[str, Tuple[Union[bool, None], int]]):
        self.type = "get_all_switch_states_response"
        self.states = states


class GetSwitchStateResponse(Response):
    def __init__(self, name: str, data: Tuple[Union[bool, None], int]):
        self.type = "get_switch_state_response"
        self.name = name
        self.data = data


class GetAllSensorDataResponse(Response):
    def __init__(
        self,
        sensors: dict[
            str, Tuple[Union[int, float, None], Union[int, float, None], int]
        ],
    ):
        self.type = "get_all_sensor_data_response"
        self.sensors = sensors


class GetSensorDataResponse(Response):
    def __init__(
        self,
        name: str,
        data: Union[Tuple[Union[int, float, None], Union[int, float, None], int], None],
    ):
        self.type = "get_sensor_data_response"
        self.name = name
        self.data = data
