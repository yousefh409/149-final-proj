from bleak import BleakClient
import asyncio

def accelx(sender, data):
    int_data = int.from_bytes(data, "little")
    print("Ax: ", int_data)
    
def accely(sender, data):
    int_data = int.from_bytes(data, "little")
    print("Ay: ", int_data)
    
def accelz(sender, data):
    int_data = int.from_bytes(data, "little")
    print("Az: ", int_data)
    
def gyrox(sender, data):
    int_data = int.from_bytes(data, "little")
    print("Gx: ", int_data)
    
def gyroy(sender, data):
    int_data = int.from_bytes(data, "little")
    print("Gy: ", int_data)
    
def gyroz(sender, data):
    int_data = int.from_bytes(data, "little")
    print("Gz: ", int_data)
    
def flex0(sender, data):
    int_data = int.from_bytes(data, "little")
    print("flex0: ", int_data)
    
def flex1(sender, data):
    int_data = int.from_bytes(data, "little")
    print("flex1: ", int_data)
    
def flex2(sender, data):
    int_data = int.from_bytes(data, "little")
    print("flex2: ", int_data)
    
def flex3(sender, data):
    int_data = int.from_bytes(data, "little")
    print("flex3: ", int_data)


async def main(address):
    async with BleakClient(address) as client:
        table = { 'aaa1' : accelx,
                 'aaa2' : accely,
                 'aaa3' : accelz,
                 'bbb1' : gyrox,
                 'bbb2' : gyroy,
                 'bbb3' : gyroz,
                 'ccc0' : flex0,
                 'ccc1' : flex1,
                 'ccc2' : flex2,
                 'ccc3' : flex3 }

        service = client.services.get_service("fff0")
        if service is not None:
            # start_notifies
            for (charuuid, fn) in table.items():
                characteristic = service.get_characteristic(charuuid)
                if not characteristic:
                    continue
                await client.start_notify(characteristic, fn)

            # waits 15 seconds
            await asyncio.sleep(5.0)

            for (charuuid) in table:
                await client.stop_notify(charuuid)

if __name__ == "__main__":  
    address = "d8:87:02:70:0b:13"
    asyncio.run(main(address))
