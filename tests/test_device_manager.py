import time
import pytest
from typing import Union
from devices.errors import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
    DeviceTypeError,
)
from devices.manager import DeviceManager
from devices.sensors.sensor import Sensor
from devices.switches.passive_switch import PassiveSwitch
from devices.switches.switch import Switch


@pytest.mark.parametrize(
    "device, expected",
    [
        (Sensor(name="TestSensor"), Sensor(name="TestSensor")),
        (
            Sensor(name="TestSensor2", min=5, max=10, sample_rate=5),
            Sensor(name="TestSensor2", min=5, max=10, sample_rate=5),
        ),
        (Switch(name="TestSwitch"), Switch(name="TestSwitch")),
        (
            PassiveSwitch(name="TestPassiveSwitch"),
            PassiveSwitch(name="TestPassiveSwitch"),
        ),
        (Sensor(name="TestSensor"), DeviceAlreadyExistsError),
        (Switch(name="TestSwitch"), DeviceAlreadyExistsError),
        (PassiveSwitch(name="TestPassiveSwitch"), DeviceAlreadyExistsError),
    ],
    ids=[
        "valid_sensor",
        "valid_sensor_custom",
        "valid_switch",
        "valid_passive_switch",
        "existing_sensor",
        "existing_switch",
        "existing_passive_switch",
    ],
)
def test_add_device(
    device: Union[Sensor, Switch],
    expected: Union[Sensor, Switch, DeviceAlreadyExistsError],
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    if isinstance(expected, type) and issubclass(expected, DeviceAlreadyExistsError):
        device_manager.add_device(device)
        with pytest.raises(DeviceAlreadyExistsError):
            device_manager.add_device(device)
            assert device.name not in device_manager.devices
    else:
        device_manager.add_device(device)
        assert expected.name in device_manager.devices  # type: ignore
        if isinstance(expected, Sensor):
            # check that the correct min, max and sample_rate match the expected values
            assert device_manager.devices[expected.name].min_data == expected.min_data  # type: ignore
            assert device_manager.devices[expected.name].max_data == expected.max_data  # type: ignore
            assert (
                device_manager.devices[expected.name].sample_rate  # type: ignore
                == expected.sample_rate
            )
        elif isinstance(expected, Switch):
            assert device_manager.devices[expected.name].type == expected.type  # type: ignore
            assert device_manager.devices[expected.name].state == expected.state  # type: ignore


def test_load_devices(
    tmp_path: pytest.TempPathFactory,
) -> None:
    # init device manager and add new devices
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(Sensor(name="TestSensor"))
    device_manager.add_device(Switch(name="TestSwitch"))

    # overwrite device manager with new instance, previous devices should be loaded (from db)
    device_manager = DeviceManager(db_path=str(db_file))
    assert "TestSensor" in device_manager.devices
    assert "TestSwitch" in device_manager.devices


def test_get_devices(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    test_sensor = Sensor(name="TestSensor")
    test_switch = Switch(name="TestSwitch")
    device_manager.add_device(test_sensor)
    device_manager.add_device(test_switch)
    devices = device_manager.devices
    assert devices == {"TestSensor": test_sensor, "TestSwitch": test_switch}


def test_remove_device(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(Sensor(name="TestSensor"))
    device_manager.add_device(Switch(name="TestSensor2"))
    device_manager.add_device(PassiveSwitch(name="TestPassiveSwitch"))
    device_manager.add_device(Sensor(name="TestSwitch"))
    device_manager.remove_device("TestSensor2")
    device_manager.remove_device("TestPassiveSwitch")
    assert "TestSensor2" not in device_manager.devices
    assert "TestPassiveSwitch" not in device_manager.devices
    with pytest.raises(DeviceNotFoundError):
        device_manager.remove_device("TestSensor2")
    with pytest.raises(DeviceNotFoundError):
        device_manager.remove_device("TestPassiveSwitch")
    assert "TestSensor" in device_manager.devices
    assert "TestSwitch" in device_manager.devices


def test_enable_sensor(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(Sensor(name="TestSensor"))
    device_manager.enable_sensor("TestSensor")
    assert device_manager.devices["TestSensor"]._task is not None  # type: ignore


def test_enable_all_sensors(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(Sensor(name="TestSensor"))
    device_manager.add_device(Sensor(name="TestSensor2"))
    device_manager.add_device(Sensor(name="TestSensor3"))
    device_manager.enable_all_sensors()
    assert device_manager.devices["TestSensor"]._task is not None  # type: ignore
    assert device_manager.devices["TestSensor2"]._task is not None  # type: ignore
    assert device_manager.devices["TestSensor3"]._task is not None  # type: ignore


def test_enable_switch(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(PassiveSwitch(name="TestSwitch"))
    device_manager.add_device(Switch(name="TestSwitch2"))
    device_manager.enable_switch("TestSwitch")
    assert device_manager.devices["TestSwitch"]._task is not None  # type: ignore
    with pytest.raises(DeviceTypeError):
        device_manager.enable_switch("TestSwitch2")


def test_enable_all_switches(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(PassiveSwitch(name="TestSwitch"))
    device_manager.add_device(PassiveSwitch(name="TestSwitch2"))
    device_manager.add_device(PassiveSwitch(name="TestSwitch3"))
    device_manager.add_device(Switch(name="TestSwitch4"))
    device_manager.enable_all_switches()
    assert device_manager.devices["TestSwitch"]._task is not None  # type: ignore
    assert device_manager.devices["TestSwitch2"]._task is not None  # type: ignore
    assert device_manager.devices["TestSwitch3"]._task is not None  # type: ignore


def test_set_switch(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(Switch(name="TestSwitch"))
    device_manager.set_switch("TestSwitch", state=True)
    assert device_manager.devices["TestSwitch"].state[0] is True  # type: ignore
    device_manager.set_switch("TestSwitch", state=False)
    assert device_manager.devices["TestSwitch"].state[0] is False  # type: ignore
    with pytest.raises(DeviceNotFoundError):
        device_manager.set_switch("TestSwitch2", state=True)
    device_manager.add_device(PassiveSwitch(name="TestSwitch2"))
    with pytest.raises(DeviceTypeError):
        device_manager.set_switch("TestSwitch2", state=True)
    with pytest.raises(DeviceTypeError):
        device_manager.set_switch("TestSwitch2", state=False)


def test_set_all_switches(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(Switch(name="TestSwitch"))
    device_manager.add_device(Switch(name="TestSwitch2"))
    device_manager.add_device(Switch(name="TestSwitch3"))
    device_manager.set_all_switches(state=True)
    assert device_manager.devices["TestSwitch"].state[0] is True  # type: ignore
    assert device_manager.devices["TestSwitch2"].state[0] is True  # type: ignore
    assert device_manager.devices["TestSwitch3"].state[0] is True  # type: ignore
    device_manager.set_all_switches(state=False)
    assert device_manager.devices["TestSwitch"].state[0] is False  # type: ignore
    assert device_manager.devices["TestSwitch2"].state[0] is False  # type: ignore
    assert device_manager.devices["TestSwitch3"].state[0] is False  # type: ignore


def test_get_switch_state(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(Switch(name="TestSwitch"))
    device_manager.add_device(PassiveSwitch(name="TestSwitch2"))
    assert device_manager.get_switch_state("TestSwitch")[0] is False
    assert device_manager.get_switch_state("TestSwitch2")[0] is False
    device_manager.set_switch("TestSwitch", state=True)
    assert device_manager.get_switch_state("TestSwitch")[0] is True
    with pytest.raises(DeviceTypeError):
        device_manager.set_switch("TestSwitch2", state=True)
    assert device_manager.get_switch_state("TestSwitch2")[0] is False


def test_get_all_switch_states(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(Switch(name="TestSwitch"))
    device_manager.add_device(PassiveSwitch(name="TestSwitch2"))
    switch_states = device_manager.get_all_switch_states()
    for data in switch_states.values():
        assert data[0] is False
    device_manager.set_switch("TestSwitch", state=True)
    switch_states = device_manager.get_all_switch_states()
    assert switch_states["TestSwitch"][0] is True
    assert switch_states["TestSwitch2"][0] is False
    with pytest.raises(DeviceTypeError):
        device_manager.set_switch("TestSwitch2", state=True)


def test_get_sensor_data(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(Sensor(name="TestSensor"))
    device_manager.add_device(Sensor(name="TestSensor2", min=5, max=10, sample_rate=5))

    # sleep for generating some data...
    time.sleep(5)
    devices = device_manager.devices
    for device in devices.values():
        device_data = device_manager.get_sensor_data(device.name)
        assert isinstance(device_data, tuple)
        assert isinstance(device_data[0], (int, float, type(None)))
        assert isinstance(device_data[1], (int, float, type(None)))
        assert isinstance(device_data[2], int)


def test_get_all_sensor_data(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(Sensor(name="TestSensor"))
    device_manager.add_device(Sensor(name="TestSensor2", min=5, max=10, sample_rate=5))

    # sleep for generating some data...
    time.sleep(5)
    sensor_data = device_manager.get_all_sensor_data()
    for data in sensor_data.values():
        assert isinstance(data, tuple)
        assert isinstance(data[0], (int, float, type(None)))
        assert isinstance(data[1], (int, float, type(None)))
        assert isinstance(data[2], int)


def test_set_sensor_sample_rate(
    tmp_path: pytest.TempPathFactory,
) -> None:
    db_file = tmp_path / "test_database.db"  # type: ignore
    device_manager = DeviceManager(db_path=str(db_file))
    device_manager.add_device(Sensor(name="TestSensor"))
    device_manager.add_device(Sensor(name="TestSensor2", min=5, max=10, sample_rate=5))

    device_manager.set_sensor_sample_rate("TestSensor", 5)
    assert device_manager.devices["TestSensor"].sample_rate == 5  # type: ignore
    device_manager.set_sensor_sample_rate("TestSensor2", 10)
    assert device_manager.devices["TestSensor2"].sample_rate == 10  # type: ignore
    with pytest.raises(DeviceNotFoundError):
        device_manager.set_sensor_sample_rate("TestSensor3", 5)
    with pytest.raises(ValueError):
        device_manager.set_sensor_sample_rate("TestSensor", -1)
    with pytest.raises(ValueError):
        device_manager.set_sensor_sample_rate("TestSensor", 0.1)