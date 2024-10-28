import logging
from app.messages.responses import (
    GetAllSensorDataResponse,
    GetAllSwitchStatesResponse,
    GetSensorDataResponse,
    GetSwitchStateResponse,
    GetAllDevicesResponse,
)
from devices.manager import DeviceManager
from devices.switches.passive_switch import PassiveSwitch
from devices.sensors.sensor import Sensor
from devices.switches.switch import Switch
from devices.utils import SwitchType
from typing import Union
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from app.ws_utils import connections


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = FastAPI()
device_manager = DeviceManager()


@app.websocket("/ws/{path}")
async def websocket_endpoint(websocket: WebSocket, path: str) -> None:
    if f"/{path}" not in connections:
        logging.debug(f"Rejecting connection on invalid path: /{path}")
        await websocket.close(code=403)
        return

    await websocket.accept()
    connections[f"/{path}"].append(websocket)
    logging.debug(f"Client connected on path: /{path}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logging.debug(f"Client disconnected from path: /{path}")
        connections[f"/{path}"].remove(websocket)


@app.get("/get_all_devices")
async def get_all_devices() -> JSONResponse:
    try:
        devices = device_manager.devices
        processed_devices = {
            device_name: str(data) for device_name, data in devices.items()
        }
        response = GetAllDevicesResponse(processed_devices)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(status_code=200, content=response.to_dict())


@app.put("/add_sensor")
async def add_sensor(
    name: str = Query(..., description="Name of the sensor"),
    min: Union[float, int] = Query(0, description="Minimum data value"),
    max: Union[float, int] = Query(100, description="Maximum data value"),
    sample_rate: int = 1,
) -> JSONResponse:
    try:
        sensor = Sensor(name=name, min=min, max=max, sample_rate=sample_rate)
        device_manager.add_device(sensor)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(status_code=200, content={"message": "Sensor added."})


@app.put("/set_sensor_sample_rate")
async def set_sensor_sample_rate(
    name: str = Query(..., description="Name of the sensor"),
    sample_rate: int = Query(..., description="New sample rate"),
) -> JSONResponse:
    try:
        device_manager.set_sensor_sample_rate(name, sample_rate)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(status_code=200, content={"message": "Sample rate set."})


@app.put("/add_switch")
async def add_switch(
    name: str = Query(..., description="Name of the switch"),
    type: SwitchType = Query(..., description="Type of the switch"),
) -> JSONResponse:
    try:
        switch: Union[Switch, PassiveSwitch]
        if type == SwitchType.passive_switch:
            switch = PassiveSwitch(name=name)
        else:
            switch = Switch(name=name)
        device_manager.add_device(switch)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(status_code=200, content={"message": "Switch added."})


@app.delete("/remove_device")
async def remove_device(
    name: str = Query(..., description="Name of the device")
) -> JSONResponse:
    try:
        device_manager.remove_device(name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(status_code=200, content={"message": "Device removed."})


@app.get("/get_sensor_data")
async def get_sensor_data(
    name: str = Query(..., description="Name of the sensor")
) -> JSONResponse:
    try:
        data = device_manager.get_sensor_data(name)
        response = GetSensorDataResponse(name, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(status_code=200, content=response.to_dict())


@app.get("/get_all_sensor_data")
async def get_all_sensor_data() -> JSONResponse:
    try:
        data = device_manager.get_all_sensor_data()
        response = GetAllSensorDataResponse(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(status_code=200, content=response.to_dict())


@app.put("/set_switch")
async def set_switch(
    name: str = Query(..., description="Name of the switch"),
    state: bool = Query(..., description="Bool state of the switch"),
) -> JSONResponse:
    try:
        device_manager.set_switch(name, state)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(status_code=200, content={"message": "Switch state set."})


@app.put("/set_all_switches")
async def set_all_switches(
    state: bool = Query(..., description="Bool state of the switches")
) -> JSONResponse:
    try:
        device_manager.set_all_switches(state)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(
        status_code=200, content={"message": "All switches states set."}
    )


@app.get("/get_switch_state")
async def get_switch_state(
    name: str = Query(..., description="Name of the switch"),
) -> JSONResponse:
    try:
        state = device_manager.get_switch_state(name)
        response = GetSwitchStateResponse(name, state)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content=response.to_dict())


@app.get("/get_all_switch_states")
async def get_all_switch_states() -> JSONResponse:
    try:
        states = device_manager.get_all_switch_states()
        response = GetAllSwitchStatesResponse(states)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content=response.to_dict())
