#!/usr/bin/env python

# Basically just sits and listens to signals indefinitely

import asyncio
from websockets.sync.client import connect
from protocol import Mode
import os
import argparse

args = argparse.ArgumentParser(description="Listens for all broadcasts from a sensor server.")
args.add_argument("-r", "--remote", action="store_true", help="Use this flag to connect to a remote server at 192.168.22.1. If not, localhost is used.")
args.add_argument("-s", "--send", type=Mode, default=None, help="Send a control signal at start. Specified using the string types of the protocol Mode class (i.e. {','.join([str(m.value) for m in Mode][:-1])} or {str(Mode.STOP.value)})")
args = args.parse_args()

SERVER_ADDR = "192.168.22.1" if args.remote else "localhost" 
print(f"Searching for server target at {SERVER_ADDR}...")

# Send the control signal if specified
if args.send:
    with connect(f"ws://{SERVER_ADDR}:1337") as websocket:
        print(f"Connected to send {args.send} to server at {SERVER_ADDR}...")
        print(f"Sending control signal {args.send}...")
        websocket.send(args.send.value)

with connect(f"ws://{SERVER_ADDR}:1337") as websocket:
    print(f"Connected to server at {SERVER_ADDR}.")
    while True:
        print(f"Recieved:\n{websocket.recv()}")

