import concurrent.futures
import logging
from typing import Tuple, Union
from enum import Enum
from devices.sensors.sensor import Sensor

logger = logging.getLogger(__name__)


class SwitchType(str, Enum):
    active_switch = "active_switch"
    passive_switch = "passive_switch"


def get_sensor_data_with_timeout(
    sensor: Sensor, timeout: int = 5
) -> Tuple[Union[int, float, None], Union[int, float, None], int]:
    """
    Reads data from a sensor with a timeout.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(sensor.read_data)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            future.cancel()
            raise TimeoutError(f"Sensor '{sensor.name}' timed out.")
