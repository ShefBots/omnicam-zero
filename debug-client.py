#!/usr/bin/env python

# Basically just sits and listens to signals indefinitely

import asyncio
from websockets.sync.client import connect
import os
import argparse

args = argparse.ArgumentParser(description="Listens for all broadcasts from a sensor server.")
args.add_argument("-r", "--remote", action="store_true", help="Use this flag to connect to a remote server at 192.168.22.1. If not, localhost is used.")
args = args.parse_args()

SERVER_ADDR = "192.168.22.1" if args.remote else "localhost" 
print(f"Searching for server target at {SERVER_ADDR}...")

with connect(f"ws://{SERVER_ADDR}:1337") as websocket:
    print(f"Connected to server at {SERVER_ADDR}.")
    while True:
        print(f"Recieved:\n{websocket.recv()}")
