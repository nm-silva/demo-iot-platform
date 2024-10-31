from typing import Union
import pytest
from devices.sensors.sensor import Sensor


@pytest.fixture
def sensor() -> Sensor:
    return Sensor(name="TestSensor")


@pytest.mark.parametrize(
    "sample_rate, expected",
    [
        (5, 5),
        (10, 10),
        (1, 1),
        (0, "raises"),
        (-1, "raises"),
    ],
    ids=[
        "valid_0",
        "valid_1",
        "valid_2",
        "invalid_0",
        "invalid_1",
    ],
)
def test_set_sample_rate(
    sensor: Sensor, sample_rate: int, expected: Union[int, str]
) -> None:
    if expected == "raises":
        with pytest.raises(ValueError):
            sensor.set_sample_rate(sample_rate)
    else:
        sensor.set_sample_rate(sample_rate)
        assert sensor._sample_rate == expected


@pytest.mark.parametrize(
    "initial_value, prev_value, latest_ts",
    [(50, 45, 1234567890), (-999999, 70, 1234567891), (None, 95, 1234567892)],
    ids=["standard", "corrupt_1", "corrupt_2"],
)
def test_read_data(
    sensor: Sensor, initial_value: int, prev_value: int, latest_ts: int
) -> None:
    sensor._value = initial_value
    sensor._prev_value = prev_value
    sensor._latest_ts = latest_ts
    value, prev_value, latest_ts = sensor.read_data()  # type: ignore
    assert value == initial_value
    assert prev_value == prev_value
    assert latest_ts == latest_ts


def test_stop(sensor: Sensor) -> None:
    sensor.stop()
    assert sensor._stop_event.is_set()
    assert not sensor._task


def test_start(sensor: Sensor) -> None:
    sensor.start()
    assert not sensor._stop_event.is_set()
    assert sensor._task
    assert not sensor._task.done()
    sensor.stop()


def test_get_name(sensor: Sensor) -> None:
    assert sensor.name == "TestSensor"


@pytest.mark.parametrize(
    "min_data, expected",
    [
        (None, 0),
        (1, 1),
        (-1, -1),
        (0.5, 0.5),
        (-0.5, -0.5),
    ],
    ids=[
        "default",
        "int_1",
        "int_2",
        "float_0",
        "float_1",
    ],
)
def test_get_min_data(min_data: Union[int, float], expected: Union[int, float]) -> None:
    if min_data is None:
        sensor = Sensor(name="TestSensor")
    else:
        sensor = Sensor(name="TestSensor", min=min_data)
    assert sensor.min_data == expected


@pytest.mark.parametrize(
    "max_data, expected",
    [
        (None, 100),
        (1, 1),
        (-1, -1),
        (0.5, 0.5),
        (-0.5, -0.5),
    ],
    ids=[
        "default",
        "int_1",
        "int_2",
        "float_0",
        "float_1",
    ],
)
def test_get_max_data(max_data: Union[int, float], expected: Union[int, float]) -> None:
    if max_data is None:
        sensor = Sensor(name="TestSensor")
    else:
        sensor = Sensor(name="TestSensor", max=max_data)
    assert sensor.max_data == expected


@pytest.mark.parametrize(
    "sample_rate, expected",
    [
        (None, 1),
        (1, 1),
        (5, 5),
        (0, "raises"),
        (-1, "raises"),
    ],
    ids=[
        "default",
        "valid_1",
        "valid_2",
        "invalid_0",
        "invalid_1",
    ],
)
def test_get_sample_rate(
    sample_rate: Union[int, None], expected: Union[int, str]
) -> None:
    if expected == "raises":
        with pytest.raises(ValueError):
            sensor = Sensor(name="TestSensor", sample_rate=sample_rate)  # type: ignore
    else:
        if sample_rate is None:
            sensor = Sensor(name="TestSensor")
        else:
            sensor = Sensor(name="TestSensor", sample_rate=sample_rate)
        assert sensor.sample_rate == expected
