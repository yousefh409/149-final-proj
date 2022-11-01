import asyncio
from bleak import BleakScanner, BleakClient

async def echo(sender, data):
    print(int.from_bytes(data, "little"))

async def setup(address):
    async with BleakClient(address) as client:
        service = client.services.get_service("fff0")
        characteristic = service.get_characteristic("ccc0")
        
        await client.start_notify(characteristic, echo)
        await asyncio.sleep(30.0)
        await client.stop_notify(characteristic)
       
address = "d8:87:02:70:0b:13"
loop = asyncio.get_event_loop()
loop.run_until_complete(setup(address))