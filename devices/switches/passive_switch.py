import asyncio
import logging
from typing import Optional
import numpy as np

from devices.switches.switch import Switch
from devices.utils import SwitchType
from app.ws_utils import notify_switch_ws

SAMPLE_RATE_MIN = 5
SAMPLE_RATE_MAX = 60

logger = logging.getLogger(__name__)


class PassiveSwitch(Switch):
    """
    This class represents a passive switch device, which cannot be turned on or off by the user.
    E.g. PIR sensor, light sensor, door sensor, etc.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._state = False
        self._type = SwitchType.passive_switch
        self._stop_event = asyncio.Event()
        self._task: Optional[asyncio.Task[None]] = None

    def __del__(self) -> None:
        self.stop()

    def stop(self) -> None:
        """
        Stops the passive switch.
        """
        logger.info(f"Stopping passive switch '{self._name}'.")
        self._stop_event.set()
        if self._task:
            self._task.cancel()

    async def _data_generator(self) -> None:
        """
        Changes the state of the switch every SAMPLE_RATE_MIN to SAMPLE_RATE_MAX seconds in an
        infinite loop.
        """
        try:
            while not self._stop_event.is_set():
                self._state = not self._state
                notify_switch_ws(self._name, self._state)
                await asyncio.sleep(np.random.randint(SAMPLE_RATE_MIN, SAMPLE_RATE_MAX))
        except asyncio.CancelledError:
            logger.info(f"Data generator for '{self._name}' was cancelled.")
        finally:
            logger.info(f"Data generator for '{self._name}' has stopped.")

    def enable_switch(self) -> None:
        """
        Enables the passive switch.
        """
        logger.info(f"Enabling passive switch '{self._name}'.")
        loop = asyncio.get_event_loop()
        self._task = loop.create_task(self._data_generator())

    def set_state(self, state: bool) -> None:
        """
        Turns the switch on (True) or off (False).
        """
        raise NotImplementedError(
            "Passive switches cannot be turned on or off by the user."
        )
