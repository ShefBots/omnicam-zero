#!/usr/bin/env python

import asyncio
from websockets.sync.client import connect

SERVER_ADDR = "localhost"
#SERVER_ADDR = "192.168.22.1"

def recieve_data():
    with connect(f"ws://{SERVER_ADDR}:1337") as websocket:
        for i in range(5):
            print(f"Recieved:\n{websocket.recv()}")
        #websocket.send("Hello world!")
        #message = websocket.recv()
        #print(f"Received: {message}")

recieve_data()

#transmit_modechange():

