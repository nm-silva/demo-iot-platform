from typing import Union
import pytest
from devices.switches.switch import Switch
from devices.switches.passive_switch import PassiveSwitch


@pytest.fixture
def switch() -> Switch:
    return Switch(name="TestSwitch")


@pytest.fixture
def passive_switch() -> PassiveSwitch:
    return PassiveSwitch(name="TestPassiveSwitch")


@pytest.mark.parametrize(
    "state, expected",
    [(True, True), (False, False), (1, "raises"), (None, "raises"), ("True", "raises")],
    ids=[
        "valid_0",
        "valid_1",
        "invalid_0",
        "invalid_1",
        "invalid_2",
    ],
)
def test_set_state(
    switch: Switch, state: Union[bool, None], expected: Union[bool, str]
) -> None:
    if expected == "raises":
        with pytest.raises(ValueError):
            switch.set_state(state)  # type: ignore
    else:
        switch.set_state(state)  # type: ignore
        assert switch.state[0] == expected


def test_enable_passive_switch(passive_switch: PassiveSwitch) -> None:
    passive_switch.enable_switch()
    assert not passive_switch._stop_event.is_set()
    assert passive_switch._task
    assert not passive_switch._task.done()
    passive_switch.stop()


def test_get_switch_name(switch: Switch) -> None:
    assert switch.name == "TestSwitch"


def test_get_switch_type(switch: Switch) -> None:
    assert switch.type == "active_switch"


def test_get_passive_switch_state(passive_switch: PassiveSwitch) -> None:
    assert passive_switch.type == "passive_switch"
