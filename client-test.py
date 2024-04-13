#!/usr/bin/env python

import asyncio
from websockets.sync.client import connect
import os

SERVER_ADDR = "localhost"

if os.path.exists("target.config"):
    print("Target config found.")
    SERVER_ADDR = "192.168.22.1"
else:
    print("No target config found. Assuming localhost...")

def recieve_data(n):
    with connect(f"ws://{SERVER_ADDR}:1337") as websocket:
        for i in range(n):
            print(f"Recieved:\n{websocket.recv()}")

def transmit_modechange(m):
    with connect(f"ws://{SERVER_ADDR}:1337") as websocket:
        websocket.send(m) # Transmit a switch to the 'RANDOM' mode.

recieve_data(2)
print("transmitting 'R'")
transmit_modechange("R")
recieve_data(2)
print("transmitting 'T'")
transmit_modechange("T")
recieve_data(2)
transmit_modechange("S")

