from bleak import BleakClient
import asyncio

bt = {
    "Ax" : -1,
    "Ay" : -1,
    "Az" : -1,
    "f0" : -1,
    "f1" : -1,
    "f2" : -1,
    "f3" : -1,
}

def accelx(sender, data):
    bt['Ax'] = int.from_bytes(data, byteorder="little", signed=True)

def accely(sender, data):
    bt['Ay'] = int.from_bytes(data, byteorder="little", signed=True)
    
def accelz(sender, data):
    bt['Az'] = int.from_bytes(data, byteorder="little", signed=True)

def flex0(sender, data):
    bt['f0'] = int.from_bytes(data, "little")

def flex1(sender, data):
    bt['f1'] = int.from_bytes(data, "little")

def flex2(sender, data):
    bt['f2'] = int.from_bytes(data, "little")

def flex3(sender, data):
    bt['f3'] = int.from_bytes(data, "little")


async def main(address):
    async with BleakClient(address) as client:
        table = { 'aaa1' : accelx,
                 'aaa2' : accely,
                 'aaa3' : accelz,
                 'ccc0' : flex0,
                 'ccc1' : flex1,
                 'ccc2' : flex2,
                 'ccc3' : flex3 }

        service = client.services.get_service("fff0")
        if service is not None:
            # start_notifies
            for (charuuid, fn) in table.items():
                characteristic = service.get_characteristic(charuuid)
                if characteristic is not None:
                    await client.start_notify(characteristic, fn)
        return

if __name__ == "__main__":  
    address = "68:a2:25:0d:75:60"
    asyncio.run(main(address))
