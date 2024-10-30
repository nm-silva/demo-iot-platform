"""
This modules contains the switch class, to simulate a switching device (on/off).
"""

import time
from typing import Tuple
from devices.utils import SwitchType


class Switch:
    """
    This class represents a switch device, which can be turned on or off.
    """

    def __init__(self, name: str) -> None:
        self._state = False
        self._name = name
        self._latest_ts = int(time.time())
        self._type = SwitchType.active_switch

    def __str__(self) -> str:
        return str(
            {
                "name": self._name,
                "state": self._state,
                "type": self._type.name,
            }
        )

    @property
    def name(self) -> str:
        """
        Returns the name of the switch.
        """
        return self._name

    @property
    def type(self) -> SwitchType:
        """
        Returns the type of the switch.
        """
        return self._type

    @property
    def state(self) -> Tuple[bool, int]:
        """
        Returns True if the switch is on, False otherwise.
        """
        return (self._state, self._latest_ts)

    def set_state(self, state: bool) -> None:
        """
        Turns the switch on (True) or off (False).
        """
        self._state = state
        self._latest_ts = int(time.time())
