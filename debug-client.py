#!/usr/bin/env python

# Basically just sits and listens to signals indefinitely

import asyncio
import websockets
from websockets.exceptions import InvalidHandshake
from protocol import Mode, get_mode_description, COMMUNICATION_PORT, REMOTE_ADDR
from basiclog import log, log_nt
import os
import argparse
import json

args = argparse.ArgumentParser(description="Listens for all broadcasts from a sensor server.")
args.add_argument("-r", "--remote", action="store_true", help=f"Use this flag to connect to a remote server at {REMOTE_ADDR}. If not, localhost is used.")
args.add_argument("-t", "--transmit-mode", action="store_true", help="Use this flag to transmit commands to the server.")
args = args.parse_args()

SERVER_ADDR = REMOTE_ADDR if args.remote else "localhost" 
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
    while True:
        command = input("> ")
        if command == "exit":
            log("Closing connection...")
            break
        await websocket.send(command)

async def listen_mode(websocket):
    log("Listening for broadcasted signals...")
    while True:
        data = await websocket.recv()
        data = json.dumps(json.loads(data), indent=2)
        log(f"Recieved:\n{data}")
    

async def main():
    try:
        async with websockets.connect(f"ws://{SERVER_ADDR}:{COMMUNICATION_PORT}") as websocket:
            log(f"Connection established to server at {SERVER_ADDR}.")
            if(args.transmit_mode):
                await transmission_mode(websocket)
            else:
                await listen_mode(websocket)
        log("Connection closed.")
    except websockets.exceptions.ConnectionClosed:
        log("Connection closed by server.")
    except ConnectionRefusedError as e:
        log("Connection refused by server. Check the server's status (and/or HOST LOCATION) and try again.")
    except TimeoutError as e:
        log("Connection timed out. Check the server's status (and/or HOST LOCATION) and try again.")
    except OSError as e:
        log("Connection failed due to TCP connection failure. Likely a network or system issue. Below is the full error:")
        print(e.strerror)
    except InvalidHandshake:
        log("Connection failed due to an invalid handshake. This shouldn't happen. ...corrupted network path?")
    except Exception as e:
        log(f"An unexpected exception of type {type(e)} was raised with message:")
        print(e)


asyncio.run(main())
