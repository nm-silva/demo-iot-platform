"""
This module contains the sensor class, to simulate a sensor device producing data.
"""

import time
import numpy as np
import logging
import asyncio
from typing import Optional, Union, Tuple
from app.ws_utils import notify_sensor_ws

logger = logging.getLogger(__name__)

DELAY_STANDARD = 5
DELAY_MAX = 30


class Sensor:
    """
    This class represents a sensor device, which can produce data.
    """

    def __init__(
        self,
        name: str,
        min: Union[float, int] = 0,
        max: Union[float, int] = 100,
        sample_rate: int = 1,
    ) -> None:
        self._name = name
        self._value: Union[int, float, None] = float(np.median([min, max]))
        self._prev_value: Union[int, float, None] = None
        self._min_data = min
        self._max_data = max
        self._sample_rate = sample_rate
        self._stop_event = asyncio.Event()
        self._task: Optional[asyncio.Task[None]] = None

    @property
    def name(self) -> str:
        """
        Returns the name of the sensor.
        """
        return self._name

    @property
    def min_data(self) -> Union[int, float]:
        """
        Returns the minimum data value the sensor can produce.
        """
        return self._min_data

    @property
    def max_data(self) -> Union[int, float]:
        """
        Returns the maximum data value the sensor can produce.
        """
        return self._max_data

    def _apply_random_corruption(
        self, original_value: Union[int, float]
    ) -> Union[int, float, None]:
        """
        Simulates random data corruption based on a probability.
        """
        if np.random.choice([True, False], p=[0.01, 0.99]):
            logger.warning(f"Data corruption for sensor '{self._name}'.")
            return None
        elif np.random.choice([True, False], p=[0.01, 0.99]):
            logger.warning(f"Data corruption for sensor '{self._name}'.")
            return -999999
        else:
            return original_value

    async def _data_generator(self) -> None:
        """
        Generates data for the sensor using random changes.
        """
        try:
            while not self._stop_event.is_set():
                if self._value is not None and self._value != -999999:
                    self._prev_value = self._value
                change = np.random.choice(
                    [(-0.01 * self._max_data), 0, (0.01 * self._max_data)]
                )
                if self._value is not None and self._value != -999999:
                    self._value = self._apply_random_corruption(
                        float(np.clip(self._value + change, self._min_data, self._max_data))
                    )
                else:
                    self._value = float(
                        np.clip(self._prev_value + change, self._min_data, self._max_data)
                    )
                notify_sensor_ws(self._name, (self._value, self._prev_value))
                await asyncio.sleep(self._sample_rate)
        except asyncio.CancelledError:
            logger.info(f"Data generator for sensor '{self._name}' was cancelled.")
        finally:
            logger.info(f"Data generator for sensor '{self._name}' has stopped.")

    def __str__(self) -> str:
        """
        Returns a string representation of the sensor in dictionary form.
        """
        return str(
            {
                "name": self._name,
                "value": self._value,
                "prev_value": self._prev_value,
                "min_data": self._min_data,
                "max_data": self._max_data,
                "sample_rate": self._sample_rate,
            }
        )

    def __del__(self) -> None:
        """
        Stops the sensor data generation when the object is deleted.
        """
        self.stop()

    def start(self) -> None:
        """
        Starts the sensor data generation.
        """
        loop = asyncio.get_event_loop()
        self._task = loop.create_task(self._data_generator())

    def stop(self) -> None:
        """
        Stops the sensor data generation.
        """
        logger.info(f"Stopping sensor '{self._name}'.")
        self._stop_event.set()
        if self._task:
            self._task.cancel()

    def set_sample_rate(self, sample_rate: int) -> None:
        """
        Sets the sample rate of the sensor, lowest possible at 1.
        """
        if sample_rate < 1:
            raise ValueError("Sample rate must be at least 1.")
        self._sample_rate = sample_rate

    def read_data(self) -> Tuple[Union[int, float, None], Union[int, float, None]]:
        """
        Returns the data produced by the sensor with a 1% chance of data delay.
        """
        # create a 1% chance of adding DELAY_STANDARD before returning the data
        if np.random.choice([True, False], p=[0.01, 0.99]):
            logger.warning(f"Data delay_min for sensor '{self._name}'.")
            time.sleep(DELAY_STANDARD)
        # create a 1% chance of adding DELAY_MAX before returning the data
        if np.random.choice([True, False], p=[0.01, 0.99]):
            logger.warning(f"Data delay_max for sensor '{self._name}'.")
            time.sleep(DELAY_MAX)
        return self._value, self._prev_value
