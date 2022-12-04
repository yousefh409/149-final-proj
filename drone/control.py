# import logging
import logging
import sys
import time
from threading import Event
import numpy as np

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.commander import Commander

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

def offstate(commander):
    print('OFF')
    commander.send_stop_setpoint()

def onstate(commander, velocity):
    vx, vy, vz = velocity
    print(f'{vx:.2f} {vy:.2f} {vz:.2f}')
    commander.send_velocity_world_setpoint(vx, vy, vz, 0.0)

def errorstate():
    print('Unreachable state')
    exit(-1)

def getvelocity(state):
    # velocity array for controlling the drone
    v = np.array([0.0, 0.0, 0.0])

    # max velocity of the drone
    maxvel = 0.05

    if state == 1:
        v[0] += 1
    if state == 2:
        v[0] -= 1
    if state == 3:
        v[1] -= 1
    if state == 4:
        v[1] += 1
    if state == 5:
        v[2] += 1
    if state == 6:
        v[2] -= 1

    # Normalizing the velocity to be porportional to the max velocity of the drone
    return v / np.linalg.norm(v) * maxvel

async def main(address, cf: Crazyflie):
    # Fill the following variables with the sensor reading from the glove
    flex0_reading = None
    flex1_reading = None
    flex2_reading = None
    flex3_reading = None
    accel_x_reading = None
    accel_y_reading = None
    accel_z_reading = None
    gyro_x_reading = None
    gyro_y_reading = None
    gyro_z_reading = None
    state = 0
    commander = Commander(cf)

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
            flex0_reading = service.get_characteristic('ccc0')
            await client.start_notify(flex0_reading, flex0)

            flex1_reading = service.get_characteristic('ccc1')
            await client.start_notify(flex1_reading, flex1)

            flex2_reading = service.get_characteristic('ccc2')
            await client.start_notify(flex2_reading, flex2)

            flex3_reading = service.get_characteristic('ccc3')
            await client.start_notify(flex3_reading, flex3)

            accel_x_reading = service.get_characteristic('aaa1')
            await client.start_notify(accel_x_reading, accelx)

            accel_y_reading = service.get_characteristic('aaa2')
            await client.start_notify(accel_y_reading, accely)

            accel_z_reading = service.get_characteristic('aaa3')
            await client.start_notify(accel_z_reading, accelz)

            gyro_x_reading = service.get_characteristic('bbb1')
            await client.start_notify(gyro_x_reading, gyrox)

            gyro_y_reading = service.get_characteristic('bbb2')
            await client.start_notify(gyro_y_reading, gyroy)
            
            gyro_z_reading = service.get_characteristic('bbb3')
            await client.start_notify(gyro_z_reading, gyroz)

            # waits 15 seconds
            # await asyncio.sleep(5.0)

            # for (charuuid) in table:
            #     await client.stop_notify(charuuid)

        # state 1 : Make the drone Ascend
        #          Spiderman web shooting and the hand is moved up
        if not flex0_reading < 60 and flex1_reading > 100 and flex2_reading > 200 and not flex3_reading < 60 and accel_z_reading < 200:
            state = 1
        
        # state 2: Make the drone Descend
        #         All four fingers are bent
        if flex0_reading > 100 and flex1_reading > 100 and flex2_reading > 200 and flex3_reading > 100:
            state = 2

        # state 3: Make the drone go Straight
        if flex0_reading > 100 and flex1_reading > 100 and flex2_reading > 200 and flex3_reading > 100 and accel_z_reading < 200:
            
            state = 3

        # state 4: Make the drone go Backwards
        if :
            state = 4

        # state 5: Make the drone go left
        if accel_x_reading > 800:
            state = 5

        # state 6: Make the drone go right
        if accel_x_reading < 250 :
            state = 6

        # state 7: Turn off the drone
            state = 7

        # set the velocity to perform the appropiate action
        v = getvelocity(state)

        # Sending the drone to the correct state
        if state == 1:
            onstate(commander, v)
        elif state == 2:
            onstate(commander, v)
        elif state == 3:
            onstate(commander, v)
        elif state == 4:
            onstate(commander, v)
        elif state == 5:
            onstate(commander, v)
        elif state == 6:
            onstate(commander, v)
        elif state == 7:
            offstate(commander)
        else:
            errorstate()

        # iterate again after some time
        time.sleep(0.1)



if __name__ == '__main__':
    # URI to the Crazyflie to connect to
    uri = 'radio://0/10/250K/E7E7E7E7E7'
    deck_attached_event = Event()
    logging.basicConfig(level=logging.ERROR)
    cflib.crtp.init_drivers()

    address = "d8:87:02:70:0b:13"
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        asyncio.run(main(address, scf.cf))
