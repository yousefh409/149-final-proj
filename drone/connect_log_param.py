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
TAKEOFF = 2
LAND = 3
# MOVE = 4

# hand states
DEFAULT = 0
ASCEND = 1
DESCEND = 2
CIRCLE = 3
CHACHA = 4
UNDEFINED = 9

# current state
STATE = OFF
NEXTSTATE = OFF

# state variables (obtained values from bluetooth)
init_accel = np.array([0, 0, 0])
init_flex = np.array([0, 0, 0])

accel = np.array([0, 0, 0])
flex = np.array([0, 0, 0, 0])

input_bool = {"Ax" : 0, "Ay" : 0, "Az" : 0, "flex0" : False, "flex1" : False, "flex2" : False, "flex3" : False}


# bluetooth
def accelx(sender, data):
    accel[0] = int.from_bytes(data, "little")
    print("Ax: ", accel[0])
    input_bool['Ax'] = int(np.abs(accel[0]) > 250) * np.sign(accel[0])

def accely(sender, data):
    accel[1] = int.from_bytes(data, "little")
    print("Ay: ", accel[0])
    input_bool['Ay'] = int(np.abs(accel[1]) > 250) * np.sign(accel[1])

def accelz(sender, data):
    accel[2] = int.from_bytes(data, "little")
    print("Az: ", accel[2])
    input_bool['Az'] = int(np.abs(accel[2]) > 250) * np.sign(accel[2])

def flex0(sender, data):
    flex[0] = int.from_bytes(data, "little")
    print("flex0: ", flex[0])
    input_bool['flex0'] = flex[0] < 100

def flex1(sender, data):
    flex[1] = int.from_bytes(data, "little")
    print("flex1: ", flex[1])
    input_bool['flex1'] = flex[1] < 100

def flex2(sender, data):
    flex[2] = int.from_bytes(data, "little")
    print("flex2: ", flex[2])
    input_bool['flex2'] = flex[2] < 100

def flex3(sender, data):
    flex[3] = int.from_bytes(data, "little")
    print("flex3: ", flex[3])
    input_bool['flex3'] = flex[3] < 200


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
        NEXTSTATE = TAKEOFF
    commander.send_stop_setpoint()

def onstate(commander):
    global NEXTSTATE

    r, p, y = 0, 0, 0
    
    if keyboard.is_pressed('space'):
        NEXTSTATE = LAND
    elif keyboard.is_pressed('backspace'):
        NEXTSTATE = OFF
        return
    # For Keyboard Use
    if keyboard.is_pressed('w'):
        p += 15
    if keyboard.is_pressed('a'):
        r -= 15
    if keyboard.is_pressed('s'):
        p -= 15
    if keyboard.is_pressed('d'):
        r += 15

    # For Glove use
    """
    if input_bool["Ay"] == 1:
        p += 15
    if input_bool["Ax"] == -1:
        r -= 15
    if input_bool["Ay"] == -1:
        p -= 15
    if input_bool["Ax"] == 1:
        r += 15
    """


    # thrust = 0.0 # TODO - calculate from gesture
    # curr_rpy = calculate_rpy(accel)
    # init_rpy = calculate_rpy(init_accel)
    # r, p, y = np.subtract(curr_rpy, init_rpy)

    thrust = 37500

    print(f'{r:.2f} {p:.2f} {y:.2f}')
    # print(thrust)
    commander.send_setpoint(r, p, y, thrust)
    # commander.send_velocity_world_setpoint(0, 0, 0.5, 0.0)

def takeoffstate(commander):
    global NEXTSTATE
    if keyboard.is_pressed('b'):
        NEXTSTATE = ON
    elif keyboard.is_pressed('backspace'):
        NEXTSTATE = OFF
        return

    r, p, y = 0, 0, 0
    thrust = 38000
    commander.send_setpoint(r, p, y, thrust)


def landstate(commander):
    global NEXTSTATE
    if keyboard.is_pressed('space'):
        NEXTSTATE = TAKEOFF
    if keyboard.is_pressed('backspace'):
        NEXTSTATE = OFF
        return

    r, p, y = 0, 0, 0
    thrust = 34000
    commander.send_setpoint(r, p, y, thrust)



def errorstate():
    exit(-1)

def handshape():
    # States based only on the flex sensors
    if not (input_bool['flex0'] or input_bool['flex1'] or input_bool['flex2'] or input_bool['flex3']):
        return DEFAULT
    elif not (input_bool['flex1'] or input_bool['flex2'] or input_bool['flex3']) and input_bool['flex0']:
        return ASCEND
    elif input_bool['flex0'] and input_bool['flex1'] and input_bool['flex2'] and input_bool['flex3']:
        return DESCEND
    elif not (input_bool['flex0'] or input_bool['flex1']) and input_bool['flex2'] and input_bool['flex3']:
        return CIRCLE
    else:
        return UNDEFINED


def command(cf: Crazyflie):
    commander = Commander(cf)
    commander.send_setpoint(0, 0, 0, 0)
    global STATE

    while True:
        # executes function based on state.
        if STATE == OFF:
            offstate(commander)
            print('OFFSTATE')
        elif STATE == ON:
            onstate(commander)
            print('ONSTATE')
        elif STATE == TAKEOFF:
            takeoffstate(commander)
            print('TAKEOFFSTATE')
        elif STATE == LAND:
            landstate(commander)
            print('LANDSTATE')
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
