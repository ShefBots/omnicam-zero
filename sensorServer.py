#!/usr/bin/env python

import asyncio
from datetime import datetime
import random
import websockets
from enum import Enum
import json
import os

from protocol import Mode, SLEEP_TIME

CONNECTIONS = set()
MODE = Mode.TIME
SERVER_ADDR = "localhost"

if os.path.exists("local.config"):
    print("Local config found.")
    SERVER_ADDR = "192.168.22.1"
else:
    print("No local config found. Assuming localhost...")

# Registers a new connection (of which there should only be one)
async def register(websocket):
    global MODE
    CONNECTIONS.add(websocket)
    try:
        await websocket.wait_closed()
        async for message in websocket:
            print(f"Recieved control command \"{message}\"")
            match message:
                case Mode.RANDOM.value:
                    print("Switching to RANDOM mode...")
                    MODE = Mode.RANDOM
                case Mode.TIME.value:
                    print("Switching to TIME mode...")
                    MODE = Mode.TIME
                case Mode.STOP.value:
                    print("Stopping...")
                    exit()
    finally:
        CONNECTIONS.remove(websocket)

async def launch_server():
    print("Launching websocket server...")
    async with websockets.serve(register, SERVER_ADDR, 1337):
        print("Websocket server launched.")
        await main() # Launch the main task

# Handles the task of accquiring and processing visual data
async def main():
    while True:
        # Currently just transmits some test data
        time = str(datetime.now())
        match MODE:
            case Mode.TIME:
                print(f"[{time}] Broadcasting time...")
                await asyncio.sleep(random.random() * 2 + 1)
                message = json.dumps({"datetime":time})
                if MODE == Mode.TIME:
                    websockets.broadcast(CONNECTIONS, message)
            case Mode.RANDOM:
                print(f"[{time}] Broadcasting random number...")
                await asyncio.sleep(random.random() * 2 + 1)
                message = json.dumps({"random":random.random()})
                if MODE == Mode.RANDOM:
                    websockets.broadcast(CONNECTIONS, message)
            case Mode.PAUSE:
                await asyncio.sleep(SLEEP_TIME)

asyncio.run(launch_server())
