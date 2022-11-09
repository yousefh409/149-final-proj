# import logging
import logging
import sys
import time
from threading import Event
import keyboard

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.commander import Commander



def getvelocity():
    vx = 0.0
    vy = 0.0
    vz = 0.0
    maxvel = 0.05

    if keyboard.is_pressed('w'):
        print('w pressed')
        vx += 1
    if keyboard.is_pressed('s'):
        print('s pressed')
        vx -= 1
    if keyboard.is_pressed('a'):
        print('a pressed')
        vy -= 1
    if keyboard.is_pressed('d'):
        print('d pressed')
        vy += 1
    if keyboard.is_pressed('space'):
        print('space pressed')
        vz += 1
    if keyboard.is_pressed('enter'):
        print('enter pressed')
        vz -= 1

    v_squared = vx**2 + vy**2 + vz**2
    tolerance = 1e-5
    if (abs(v_squared) <= tolerance):
        return (0.0, 0.0, 0.0)
    else:
        # TODO - fix this
        return vx, vy, vz


def command(cf: Crazyflie):
    commander = Commander(cf)

    while True:
        if (keyboard.is_pressed('backspace')):
            print('Quitting')
            commander.send_stop_setpoint()
            break
        else:
            vx, vy, vz = getvelocity()
            commander.send_velocity_world_setpoint(vx, vy, vz, 0.0)
            time.sleep(0.1)

    return None


if __name__ == '__main__':
    # URI to the Crazyflie to connect to
    uri = 'radio://0/10/250K/E7E7E7E7E7'
    deck_attached_event = Event()
    logging.basicConfig(level=logging.ERROR)
    cflib.crtp.init_drivers()
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        command(scf.cf)
