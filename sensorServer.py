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
                await checked_transmit(get_time_data, Mode.TIME)
            case Mode.RANDOM:
                await checked_transmit(get_random_number, Mode.RANDOM)
            case Mode.PAUSE:
                await asyncio.sleep(SLEEP_TIME)

async def checked_transmit(data_generator, mode):
    print(f"[{str(datetime.now())}] Starting {mode.value} operation...")
    data = await data_generator()
    # Only transmit if mode is still the requested mode
    print(f"[{str(datetime.now())}] \t Operation finished.")
    if MODE == mode:
        print(f"[{str(datetime.now())}] \t Transmitting.")
        websockets.broadcast(CONNECTIONS, data)
    else:
        print(f"[{str(datetime.now())}] \t Mode changed while calculating. Discarding data.")

async def get_time_data():
    await asyncio.sleep(random.random() * 2 + 1) # Simulate processing delay
    return json.dumps({"datetime":str(datetime.now())})

async def get_random_number():
    await asyncio.sleep(random.random() * 2 + 1) # Simulate processing delay
    return json.dumps({"random":random.random()})
    

asyncio.run(launch_server())
