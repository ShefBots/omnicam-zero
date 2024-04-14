#!/usr/bin/env python

import argparse
import asyncio
from datetime import datetime
import random
import websockets
from enum import Enum
import json
import os

import detectors.minesweeperDetector
from protocol import Mode, SLEEP_TIME

args = argparse.ArgumentParser(description="Launches a websocket server that transmits task-specific sensor data data.")
args.add_argument("-m", "--mode", type=Mode, default=Mode.PAUSE, help=f"The mode to start the server in. Specified using the string types of the protocol Mode class (i.e. {','.join([str(m.value) for m in Mode][:-1])} or {str(Mode.STOP.value)})")
args.add_argument("-r", "--remote", action="store_true", help="Use this flag to host a server at 192.168.22.1 (on the Pi Zero). If not, it is hosted on localhost.")
args = args.parse_args()

MODE = args.mode
SERVER_ADDR = "192.168.22.1" if args.remote else "localhost" 
print(f"Starting server in mode {MODE} on {SERVER_ADDR}...")

CONNECTIONS = set()

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
    tasks = {
                Mode.TIME: lambda: checked_transmit(get_time_data, Mode.TIME),
                Mode.RANDOM: lambda: checked_transmit(get_random_number, Mode.RANDOM),
                Mode.PAUSE: lambda: checked_transmit(be_low_power, Mode.PAUSE),
                Mode.TASK_MINESWEEPER: lambda: checked_transmit(get_minesweeper_data, Mode.TASK_MINESWEEPER)
            }
    #I wonder why the below doesn't work...
    #tasks = {
    #            Mode.TIME: get_time_data,
    #            Mode.RANDOM: get_random_number,
    #            Mode.PAUSE: be_low_power,
    #        }
    #tasks_2 = {tk:(lambda: checked_transmit(tasks[tk], tk)) for tk in tasks.keys()}
    while True:
        await tasks[MODE]()

async def checked_transmit(data_generator, mode):
    print(f"[{str(datetime.now())}] Starting {mode} operation...")
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

async def be_low_power():
    await asyncio.sleep(SLEEP_TIME)
    
async def get_minesweeper_data():
    data = minesweeperDetector.get_data()
    return json.dumps(data)
    

asyncio.run(launch_server())
