#!/usr/bin/env python

# Basically just sits and listens to signals indefinitely

import asyncio
from websockets.sync.client import connect as sync_connect
import websockets
import threading
from protocol import Mode, get_mode_description, COMMUNICATION_PORT, REMOTE_ADDR
from basiclog import log, log_nt
import os
import argparse
import json

args = argparse.ArgumentParser(description="Listens for all broadcasts from a sensor server.")
args.add_argument("-r", "--remote",
                  action="store_true",
                  help=f"Use this flag to connect to a remote server at {REMOTE_ADDR}. If not, localhost is used."
)
args.add_argument("-t", "--transmit-mode",
                  action="store_true",
                  help="Use this flag to transmit commands to the server."
)
args = args.parse_args()

SERVER_ADDR = REMOTE_ADDR if args.remote else "localhost" 
print(f"Searching for server target at {SERVER_ADDR}...")

def transmission_mode(websocket):
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
            websocket.send(command)
    except websockets.exceptions.ConnectionClosed:
        log("Connection closed by server.")

    # Transmission loop's been left, leav the function and let connection collapse

def listen_mode(websocket):
    log("Listening for broadcasted signals...")
    try:
        while True:
            data = websocket.recv()
            data = json.dumps(json.loads(data), indent=2)
            log(f"Recieved:\n{data}")
    except websockets.exceptions.ConnectionClosed:
        # Raised when recv() is called and the connection is closed
        log("Connection closed by server.")

    # Transmission loop's been left, leav the function and let connection collapse
    

def main():
    try:
        with sync_connect(f"ws://{SERVER_ADDR}:{COMMUNICATION_PORT}") as websocket:
            log(f"Connection established to server at {SERVER_ADDR}.")
            if(args.transmit_mode):
                transmission_mode(websocket)
            else:
                listen_mode(websocket)
        log("Connection closed.")
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


main()
