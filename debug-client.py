#!/usr/bin/env python

# Basically just sits and listens to signals indefinitely

import asyncio
from websockets.sync.client import connect
import os

SERVER_ADDR = "localhost"

if os.path.exists("target.config"):
    print("Target config found.")
    SERVER_ADDR = "192.168.22.1"
else:
    print("No target config found. Assuming localhost...")

with connect(f"ws://{SERVER_ADDR}:1337") as websocket:
    while True:
        print(f"Recieved:\n{websocket.recv()}")
