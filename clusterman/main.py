#!/usr/bin/env python

import asyncio, websockets
import ssl, pathlib
import json

async def consumer(message):
    x = json.loads(message)
    print(x)

async def hello(websocket, path):
    async for message in websocket:
        await consumer(message)

start_server = websockets.serve(hello, 'localhost', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()