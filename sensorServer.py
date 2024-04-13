#!/usr/bin/env python

import asyncio
from websockets.server import serve

async def echo(websocket):
    async for message in websocket:
        print(f"Recieved message:\n{message}")
        await websocket.send(message)

async def main():
    async with serve(echo, "localhost", 1337):
        print("Running socket server...")
        await asyncio.Future()  # run forever

asyncio.run(main())
