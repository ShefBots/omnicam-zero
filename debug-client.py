#!/usr/bin/env python

# Basically just sits and listens to signals indefinitely

import asyncio
import websockets
from protocol import Mode, get_mode_description, COMMUNICATION_PORT
from basiclog import log, log_nt
import os
import argparse
import json

args = argparse.ArgumentParser(description="Listens for all broadcasts from a sensor server.")
args.add_argument("-r", "--remote", action="store_true", help="Use this flag to connect to a remote server at 192.168.22.1. If not, localhost is used.")
args.add_argument("-t", "--transmit-mode", action="store_true", help="Use this flag to transmit commands to the server.")
args = args.parse_args()

SERVER_ADDR = "192.168.22.1" if args.remote else "localhost" 
print(f"Searching for server target at {SERVER_ADDR}...")

async def transmission_mode(websocket):
    # Print transmit info
    log("Port opened for control signal transmission.")
    log_nt("Comands:")
    for m in Mode:
        log_nt(f"{m.value}: {get_mode_description(m)}")
    log_nt("exit: Close this debug client's connection.")
    log_nt()

    # Begin transmission loop
    try:
        while True:
            command = input("> ")
            if command == "exit":
                log("Closing connection...")
                break
            await websocket.send(command)
    except websockets.exceptions.ConnectionClosed:
        log("Connection closed by server.")

    # Transmission loop's been left, leav the function and let connection collapse

async def listen_mode(websocket):
    log("Listening for broadcasted signals...")
    try:
        while True:
            data = await websocket.recv()
            data = json.dumps(json.loads(data), indent=2)
            log(f"Recieved:\n{data}")
    except websockets.exceptions.ConnectionClosed:
        # Raised when recv() is called and the connection is closed
        log("Connection closed by server.")

    # Transmission loop's been left, leav the function and let connection collapse
    

async def main():
    async with websockets.connect(f"ws://{SERVER_ADDR}:{COMMUNICATION_PORT}") as websocket:
        log(f"Connection established to server at {SERVER_ADDR}.")
        if(args.transmit_mode):
            await transmission_mode(websocket)
        else:
            await listen_mode(websocket)
    log("Connection closed.")


asyncio.run(main())
