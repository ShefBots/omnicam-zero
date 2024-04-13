#!/usr/bin/env python

import asyncio
from datetime import datetime
import random
import websockets
from enum import Enum

class Mode(Enum):
    TIME = 0
    RANDOM = 1

CONNECTIONS = set()

# Registers a new connection (of which there should only be one)
async def register(websocket):
    CONNECTIONS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CONNECTIONS.remove(websocket)

#async def echo(websocket):
#    async for message in websocket:
#        print(f"Recieved message:\n{message}")
#        await websocket.send(message)

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
        message = "{\ndatetime:\""+time+"\"\n}"
        print(f"[{time}] Transmitting time...")
        websockets.broadcast(CONNECTIONS, message)
        await asyncio.sleep(random.random() * 2 + 1)

asyncio.run(launch_server())
