#!/usr/bin/env python

import asyncio
from websockets.sync.client import connect

#SERVER_ADDR = "localhost"
SERVER_ADDR = "192.168.22.1"

def hello():
    with connect(f"ws://{SERVER_ADDR}:1337") as websocket:
        websocket.send("Hello world!")
        message = websocket.recv()
        print(f"Received: {message}")

hello()
