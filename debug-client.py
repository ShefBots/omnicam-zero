#!/usr/bin/env python

# Basically just sits and listens to signals indefinitely

import asyncio
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

async def transmission_mode(writer):
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
            break
        writer.write(command.encode())
        await writer.drain()

    log("Closing connection...")
    writer.close()
    await writer.wait_closed()
    log("Connection closed.")

async def listen_mode(reader):
    log("Listening for broadcasted signals...")
    while True:
        data = await reader.read(1024)
        if not data:
            break
        data = json.dumps(json.loads(data.decode()), indent=2)
        log(f"Recieved:\n{data}")

    log("Connection closed by server.")

    

async def main():
    reader, writer = await asyncio.open_connection(SERVER_ADDR, COMMUNICATION_PORT)
    log(f"Connection established to server at {SERVER_ADDR}.")

    if(args.transmit_mode):
        await transmission_mode(writer)
    else:
        await listen_mode(reader)

asyncio.run(main())
