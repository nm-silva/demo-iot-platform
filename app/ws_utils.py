# Importing required libraries
import asyncio
from typing import Any, Dict, List
from fastapi import WebSocket
from typing import Tuple, Union

from app.messages.responses import (
    GetSensorDataResponse,
    GetSwitchStateResponse,
)

connections: Dict[str, List[WebSocket]] = {"/sensors": [], "/switches": []}


# Function to broadcast messages to a specified path
async def broadcast(path: str, message: Dict[str, Any]) -> None:
    if path in connections:
        for connection in connections[path]:
            await connection.send_text(str(message))


# Callback functions for external data push to each path
def notify_sensor_ws(
    name: str, data: Tuple[Union[int, float, None], Union[int, float, None], int]
) -> None:
    response = GetSensorDataResponse(name, data)
    asyncio.create_task(broadcast("/sensors", response.to_dict()))


def notify_switch_ws(name: str, data: Tuple[Union[bool, None], int]) -> None:
    response = GetSwitchStateResponse(name, data)
    asyncio.create_task(broadcast("/switches", response.to_dict()))
