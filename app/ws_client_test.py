"""
This file is just for local websocket testing purposes.
"""

import asyncio
import websockets


async def listen_for_updates(path: str) -> None:
    uri = f"ws://localhost:5555/ws{path}"
    print(f"Connecting to {uri}")
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print(f"Connected to {uri}")
                while True:
                    message = await websocket.recv()
                    print(f"Received message on path {path}: {message}")
        except (
            websockets.ConnectionClosedError,
            websockets.InvalidURI,
            websockets.InvalidHandshake,
            OSError,
        ) as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)


async def main() -> None:
    await asyncio.gather(
        listen_for_updates("/sensors"),
        listen_for_updates("/switches"),
    )


if __name__ == "__main__":
    asyncio.run(main())
