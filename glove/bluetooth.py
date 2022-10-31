import asyncio
import bleak

async def run():
    devices = await bleak.BleakScanner.discover()
    for d in devices:
        print(d)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())