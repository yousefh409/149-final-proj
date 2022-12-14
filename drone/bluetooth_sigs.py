from bleak import BleakClient
import asyncio
import json
import sys
import numpy as np

# bit mask to determine bluetooth signal validity.
AX_SHIFT = 1 << 0
AY_SHIFT = 1 << 1
AZ_SHIFT = 1 << 2
F0_SHIFT = 1 << 3
F1_SHIFT = 1 << 4
F2_SHIFT = 1 << 5
F3_SHIFT = 1 << 6
ALLVALID = AX_SHIFT | AY_SHIFT | AZ_SHIFT | F0_SHIFT | F1_SHIFT | F2_SHIFT | F3_SHIFT

# other variables
ACCEL_THRESHOLD = 250

vars = {
    'valid' : 0,
    'Ax' : 0,
    'Ay' : 0,
    'Az' : 0,
    'f0' : False,
    'f1' : False,
    'f2' : False,
    'f3' : False,
}

shifts = {
    'Ax' : AX_SHIFT,
    'Ay' : AY_SHIFT,
    'Az' : AZ_SHIFT,
    'f0' : F0_SHIFT,
    'f1' : F1_SHIFT,
    'f2' : F2_SHIFT,
    'f3' : F3_SHIFT,
}

# bluetooth
def accelx(_, data):
    vars['valid'] |= AX_SHIFT
    data = int.from_bytes(data, "little", signed=True)
    data = int(np.abs(data) > ACCEL_THRESHOLD) * np.sign(data)
    vars['Ax'] = int(data)

def accely(_, data):
    vars['valid'] |= AY_SHIFT
    data = int.from_bytes(data, "little", signed=True)
    data = int(np.abs(data) > ACCEL_THRESHOLD) * np.sign(data)
    vars['Ay'] = int(data)

def accelz(_, data):
    vars['valid'] |= AZ_SHIFT
    data = int.from_bytes(data, "little", signed=True)
    data = int(np.abs(data) > ACCEL_THRESHOLD) * np.sign(data)
    vars['Az'] = int(data)

# 760 - 460
def flex0(_, data):
    vars['valid'] |= F0_SHIFT
    data = int.from_bytes(data, "little", signed=True)
    vars['f0'] = data > (760 + 460) // 2

# 620 - 140
def flex1(_, data):
    vars['valid'] |= F1_SHIFT
    data = int.from_bytes(data, "little", signed=True)
    vars['f1'] = data > (620 + 140) // 2

# 380 - 80
def flex2(_, data):
    vars['valid'] |= F2_SHIFT
    data = int.from_bytes(data, "little", signed=True)
    vars['f2'] = data > (380 + 80) // 2

# 280 - 80
def flex3(_, data):
    vars['valid'] |= F3_SHIFT
    data = int.from_bytes(data, "little", signed=True)
    vars['f3'] = data > (280 + 80) // 2

async def bluetooth(address):
    async with BleakClient(address) as client:
        table = {
            'aaa1' : accelx,
            'aaa2' : accely,
            'aaa3' : accelz,
            'ccc0' : flex0,
            'ccc1' : flex1,
            'ccc2' : flex2,
            'ccc3' : flex3,
        }

        service = client.services.get_service("fff0")
        if service is not None:
            # start_notifies
            for (charuuid, fn) in table.items():
                characteristic = service.get_characteristic(charuuid)
                if characteristic is not None:
                    await client.start_notify(characteristic, fn)

            # Runs bluetooth indefinitely
            while True:
                print(json.dumps(vars))
                sys.stdout.flush()
                await asyncio.sleep(0.1)


def initbluetooth():
    # initialize bluetooth async
    address = "68:a2:25:0d:75:60"
    asyncio.run(bluetooth(address))

if __name__ == '__main__':
    initbluetooth()
