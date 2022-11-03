import asyncio
from bleak import BleakScanner, BleakClient

async def accelx(sender, data):
    int_data = int.from_bytes(data, "little")
    print("Ax: ", int_data)
    
async def accely(sender, data):
    int_data = int.from_bytes(data, "little")
    print("Ay: ", int_data)
    
async def accelz(sender, data):
    int_data = int.from_bytes(data, "little")
    print("Az: ", int_data)
    
async def gyrox(sender, data):
    int_data = int.from_bytes(data, "little")
    print("Gx: ", int_data)
    
async def gyroy(sender, data):
    int_data = int.from_bytes(data, "little")
    print("Gy: ", int_data)
    
async def gyroz(sender, data):
    int_data = int.from_bytes(data, "little")
    print("Gz: ", int_data)
    
async def flex0(sender, data):
    int_data = int.from_bytes(data, "little")
    print("flex0: ", int_data)
    
async def flex1(sender, data):
    int_data = int.from_bytes(data, "little")
    print("flex1: ", int_data)
    
async def flex2(sender, data):
    int_data = int.from_bytes(data, "little")
    print("flex2: ", int_data)
    
async def flex3(sender, data):
    int_data = int.from_bytes(data, "little")
    print("flex3: ", int_data)

async def setup(address):
    async with BleakClient(address) as client:
        service = client.services.get_service("fff0")
        
        characteristic = service.get_characteristic("aaa1")
        await client.start_notify(characteristic, accelx)
        characteristic = service.get_characteristic("aaa2")
        await client.start_notify(characteristic, accely)
        characteristic = service.get_characteristic("aaa3")
        await client.start_notify(characteristic, accelz)
        
        characteristic = service.get_characteristic("bbb1")
        await client.start_notify(characteristic, gyrox)
        characteristic = service.get_characteristic("bbb2")
        await client.start_notify(characteristic, gyroy)
        characteristic = service.get_characteristic("bbb3")
        await client.start_notify(characteristic, gyroz)
        
        characteristic = service.get_characteristic("ccc0")
        await client.start_notify(characteristic, flex0)
        characteristic = service.get_characteristic("ccc1")
        await client.start_notify(characteristic, flex1)
        characteristic = service.get_characteristic("ccc2")
        await client.start_notify(characteristic, flex2)
        characteristic = service.get_characteristic("ccc3")
        await client.start_notify(characteristic, flex3)
        
        await asyncio.sleep(30.0)
        characteristics = service.characteristics
        for k in characteristics:
            await client.stop_notify(characteristics[k])
        
async def destroy(address):
    async with BleakClient(address) as client:
        service = client.services.get_service("fff0")
        characteristics = service.characteristics
        for k in characteristics:
            await client.stop_notify(characteristics[k])

def main():
    address = "d8:87:02:70:0b:13"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup(address))

if __name__ == "__main__":  
    main()
