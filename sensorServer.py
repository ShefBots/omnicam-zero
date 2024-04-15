#!/usr/bin/env python

import argparse
import asyncio
import random
from datetime import datetime
from enum import Enum
import json
import os

import detectors.minesweeperDetector as minesweeperDetector
from protocol import Mode, MODE_STRINGS, COMMUNICATION_PORT
from basiclog import log

args = argparse.ArgumentParser(description="Launches a socket server that transmits task-specific sensor data data.")
args.add_argument("-m", "--mode", type=Mode, default=Mode.TIME, help=f"The mode to start the server in. Specified using the string types of the protocol Mode class (i.e. {', '.join([str(m.value) for m in Mode][:-1])} or {str(Mode.STOP.value)})")
args.add_argument("-r", "--remote", action="store_true", help="Use this flag to host a server at 192.168.22.1 (on the Pi Zero). If not, it is hosted on localhost.")
args = args.parse_args()

SERVER_ADDR = "192.168.22.1" if args.remote else "localhost" 

mode = args.mode
active_connections = {} # reader/writer pair for each connection, as named by it's peername
connections_made = asyncio.Event() # Tracks whether there are any connections

async def launch_server():
    print(f"Starting server in mode {mode} on {SERVER_ADDR}...")
    server = await asyncio.start_server(register, SERVER_ADDR, COMMUNICATION_PORT)
    log("Server started.")
    async with server:
        await asyncio.gather(server.serve_forever(), transmission_loop())

# Registers a new connection (of which there should only be one)
async def register(reader, writer):
    global mode, active_connections, connections_made # TODO

    peername = writer.get_extra_info('peername')
    active_connections[peername] = (reader, writer)
    connections_made.set()
    log(f"New connection from {peername}")

    # Recieve loop
    try:
        while True:
            if writer.is_closing() or reader.at_eof():
                continue

            data = await reader.read(100)
            if not data:
                break
            data = data.decode()
            log(f"Received \"{data}\" from {peername}")
            if data not in MODE_STRINGS:
                log(f"Invalid mode \"{data}\" recieved from {peername}.")
                continue
            mode = Mode(data)

    except:
        log(f"Connection with {peername} reset.")
    finally:
        log(f"Closing connection with {peername}")
        active_connections.pop(peername, None)
        if(len(active_connections) == 0):
            connections_made.clear()
        writer.close()
        await writer.wait_closed()


# Handles the task of accquiring and processing visual data
async def transmission_loop():
    global active_connections, mode
    tasks = {
                Mode.TIME: get_time_data,
                Mode.RANDOM: get_random_number,
                Mode.TASK_MINESWEEPER: get_minesweeper_data
            }
    while True:
        # Only transmit if there are active connections
        await connections_made.wait()

        # Get the currently required data
        mode_at_start = mode
        log(f"Starting {mode} operation...")
        data = f"{json.dumps(await tasks[mode]())}\n".encode() # Also adds line-end to indicate end of data
        log("\tOperation finished, transmitting...")

        # For each active connection, transmit it (assuming the mode hasn't changed when we reach it)
        for _, writer in active_connections.values():
            if mode_at_start != mode:
                log("\tMode changed while calculating or transmitting. Discarding data.")
                break
            if not writer.is_closing(): # Also make sure the connection is still open
                writer.write(data)
                await writer.drain()
            else:
                log("\tConnection is in the process of closing. Discarding data.")

async def get_time_data():
    await asyncio.sleep(random.random() * 2 + 1) # Simulate processing delay
    return {"datetime":str(datetime.now())}

async def get_random_number():
    await asyncio.sleep(random.random() * 2 + 1) # Simulate processing delay
    return {"random":random.random()}
    
async def get_minesweeper_data():
    data = minesweeperDetector.get_data()
    #await asyncio.sleep(1)
    return data
    

asyncio.run(launch_server())
