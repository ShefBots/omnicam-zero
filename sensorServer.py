#!/usr/bin/env python

import asyncio
from datetime import datetime
import random
import websockets
from enum import Enum
import json

class Mode(Enum):
    TIME = 0
    RANDOM = 1

CONNECTIONS = set()
MODE = Mode.TIME

# Registers a new connection (of which there should only be one)
async def register(websocket):
    global MODE
    CONNECTIONS.add(websocket)
    try:
        await websocket.wait_closed()
        async for message in websocket:
            print(f"Recieved control command \"{message}\"")
            match message:
                case "R":
                    print("Switching to RANDOM mode...")
                    MODE = Mode.RANDOM
                case "T":
                    print("Switching to TIME mode...")
                    MODE = Mode.TIME
    finally:
        CONNECTIONS.remove(websocket)

async def launch_server():
    print("Launching websocket server...")
    async with websockets.serve(register, "localhost", 1337):
        print("Websocket server launched.")
        await main() # Launch the main task

# Handles the task of accquiring and processing visual data
async def main():
    while True:
        # Currently just transmits some test data
        time = str(datetime.now())
        match MODE:
            case Mode.TIME:
                print(f"[{time}] Transmitting time...")
                message = json.dumps({"datetime":time})
                websockets.broadcast(CONNECTIONS, message)
            case Mode.RANDOM:
                print(f"[{time}] Transmitting random number...")
                message = json.dumps({"random":random.random()})
                websockets.broadcast(CONNECTIONS, message)
        await asyncio.sleep(random.random() * 2 + 1)

asyncio.run(launch_server())
