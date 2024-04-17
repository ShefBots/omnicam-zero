#!/usr/bin/env python

import argparse
import asyncio
import websockets
import random
from datetime import datetime
from enum import Enum
import json
import os
import traceback

import detectors.minesweeperDetector as minesweeperDetector
from protocol import Mode, MODE_STRINGS, COMMUNICATION_PORT, REMOTE_ADDR, MODE_IDENTIFIER_INDICATOR
import protocol
from basiclog import log

args = argparse.ArgumentParser(description="Launches a socket server that transmits task-specific sensor data data.")
args.add_argument("-m", "--mode",
                  type=Mode, default=Mode.TIME,
                  choices=list(Mode),
                  help=f"The mode to start the server in. Specified using the string types of the protocol Mode class. Defaults to 'T'",
)
args.add_argument("-r", "--remote",
                  action="store_true",
                  help=f"Use this flag to host a server at {REMOTE_ADDR} (on the Pi Zero). If not, it is hosted on localhost and placeholder data will be used instead of camera data."
)
args.add_argument("-p", "--explain-mode-protocols",
                  action="store_true",
                  help="Prints out descriptions of the data that each transmission mode produces."
)
args = args.parse_args()

if args.explain_mode_protocols:
    print("Modes:")
    for mode in [m for m in Mode]:
        title = f"{mode} ({mode.value})" 
        print(title)
        print("=" * len(title))
        print(protocol.get_mode_description(mode))
        print(protocol.get_mode_data_format(mode))
        print()
    exit()

SERVER_ADDR = REMOTE_ADDR if args.remote else "localhost" 

mode = args.mode
connectiongs = set()
#connectiongs = {} # reader/writer pair for each connection, as named by it's peername
active_connections = asyncio.Event() # Tracks whether there are any connections

async def launch_server():
    log(f"Starting server in mode {mode} on {SERVER_ADDR}...")
    #server = await asyncio.start_server(register, SERVER_ADDR, COMMUNICATION_PORT)
    server = await websockets.serve(register, SERVER_ADDR, COMMUNICATION_PORT)
    log("Server started.")
    async with server:
        await asyncio.gather(server.serve_forever(), transmission_loop())

# Registers a new connection (of which there should only be one)
async def register(websocket):
    global mode, connectiongs, active_connections

    connectiongs.add(websocket)
    active_connections.set()
    peername = websocket.remote_address
    log(f"New connection from {peername}.")

    # Recieve loop
    try:
        while True:
            data = await websocket.recv()
            log(f"Received \"{data}\" from {peername}")
            if data not in MODE_STRINGS:
                log(f"Invalid mode \"{data}\" recieved from {peername}.")
                continue
            mode = Mode(data)
    except websockets.exceptions.ConnectionClosed:
        # Raised when recv() is called and the connection is closed
        log(f"Connection from {peername} closed by client.")

    try:
        await websocket.wait_closed()
    finally:
        connectiongs.remove(websocket)
        if(len(connectiongs) == 0):
            active_connections.clear()


# Handles the task of accquiring and processing visual data
async def transmission_loop():
    global connectiongs, mode
    tasks = {
                Mode.TIME: get_time_data,
                Mode.RANDOM: get_random_number,
                Mode.TASK_MINESWEEPER: get_minesweeper_data
            }

    try:
        while True:
            # Only transmit if there are active connections
            await active_connections.wait()

            # Get the currently required data
            mode_at_start = mode
            log(f"Starting {mode} operation...")
            data = await tasks[mode]()
            data[MODE_IDENTIFIER_INDICATOR] = mode_at_start.value
            data = f"{json.dumps(data)}"
            log("\tOperation finished, transmitting...")

            # Broadcast the data to all active connections if the mode is still the same
            if(mode_at_start == mode):
                websockets.broadcast(connectiongs, data)
    except Exception as e:
        log("ERROR: CRITICAL EXCEPTION IN TRANSMISSION LOOP:")
        log(traceback.format_exc())

async def get_time_data():
    await asyncio.sleep(random.random() * 2 + 1) # Simulate processing delay
    return {"datetime":str(datetime.now())}

async def get_random_number():
    await asyncio.sleep(random.random() * 2 + 1) # Simulate processing delay
    return {"random":random.random()}
    
async def get_minesweeper_data():
    data = minesweeperDetector.get_data()
    await asyncio.sleep(0.01) # TODO: WITHOUT THIS, THE SERVER CRASHES
    return data
    

asyncio.run(launch_server())
