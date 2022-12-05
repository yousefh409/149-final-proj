# import logging
import logging
import time
from threading import Event
import keyboard
import numpy as np

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.commander import Commander

from bleak import BleakClient
import asyncio
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.commander import Commander


# predefined states
OFF = 0
ON = 1

# current state
STATE = OFF
NEXTSTATE = OFF

# state variables (obtained values from bluetooth)
init_accel = np.array([0, 0, 0])
init_gyro = np.array([0, 0, 0])
init_flex = np.array([0, 0, 0])

accel = np.array([0, 0, 0])
gyro = np.array([0, 0, 0])
flex = np.array([0, 0, 0, 0])


# bluetooth
def accelx(sender, data):
    accel[0] = int.from_bytes(data, "little")
    print("Ax: ", accel[0])

def accely(sender, data):
    accel[1] = int.from_bytes(data, "little")
    print("Ay: ", accel[0])

def accelz(sender, data):
    accel[2] = int.from_bytes(data, "little")
    print("Az: ", accel[2])

def gyrox(sender, data):
    gyro[0] = int.from_bytes(data, "little")
    print("Gx: ", gyro[0])

def gyroy(sender, data):
    gyro[1] = int.from_bytes(data, "little")
    print("Gy: ", gyro[1])

def gyroz(sender, data):
    gyro[2] = int.from_bytes(data, "little")
    print("Gz: ", gyro[2])

def flex0(sender, data):
    flex[0] = int.from_bytes(data, "little")
    print("flex0: ", flex[0])

def flex1(sender, data):
    flex[1] = int.from_bytes(data, "little")
    print("flex1: ", flex[1])

def flex2(sender, data):
    flex[2] = int.from_bytes(data, "little")
    print("flex2: ", flex[2])

def flex3(sender, data):
    flex[3] = int.from_bytes(data, "little")
    print("flex3: ", flex[3])


# util functions
def calculate_rpy(rpy_readings):
    """Convert readings into physical values for rpy"""
    # TODO - FIX
    return rpy_readings


# state functions
def offstate(commander):
    global NEXTSTATE
    if keyboard.is_pressed('backspace'):
        NEXTSTATE = OFF
    elif keyboard.is_pressed('space'):
        NEXTSTATE = ON
    commander.send_stop_setpoint()

def onstate(commander):
    global NEXTSTATE
    if keyboard.is_pressed('backspace'):
        NEXTSTATE = OFF
        return

    thrust = 0.0 # TODO - calculate from gesture
    curr_rpy = calculate_rpy(accel)
    init_rpy = calculate_rpy(init_accel)
    r, p, y = np.subtract(curr_rpy, init_rpy)

    print(f'{r:.2f} {p:.2f} {y:.2f}')
    commander.send_setpoint(r, p, y, thrust)

def errorstate():
    exit(-1)


def command(cf: Crazyflie):
    commander = Commander(cf)
    global STATE

    while True:
        # executes function based on state.
        if STATE == OFF:
            offstate(commander)
            print('OFFSTATE')
        elif STATE == ON:
            onstate(commander)
            print('ONSTATE')
        else:
            print('ERRORSTATE')
            errorstate()

        # iterate again after some time
        STATE = NEXTSTATE
        time.sleep(0.1)


async def bluetooth(address):
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
                if characteristic is not None:
                    await client.start_notify(characteristic, fn)

            # waits 15 seconds
            await asyncio.sleep(5.0)

            for (charuuid) in table:
                await client.stop_notify(charuuid)


if __name__ == '__main__':
    # initialize bluetooth async
    address = "d8:87:02:70:0b:13"
    asyncio.run(bluetooth(address))

    # URI to the Crazyflie to connect to
    uri = 'radio://0/10/250K/E7E7E7E7E7'
    deck_attached_event = Event()
    logging.basicConfig(level=logging.ERROR)
    cflib.crtp.init_drivers()
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        command(scf.cf)
