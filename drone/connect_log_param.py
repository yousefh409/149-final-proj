# import logging
import logging
import sys
import time
from threading import Event
import keyboard
import numpy as np

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.commander import Commander

def getvelocity():
    v = np.array([0.0, 0.0, 0.0])
    maxvel = 0.05

    if keyboard.is_pressed('w'):
        v[0] += 1
    if keyboard.is_pressed('s'):
        v[0] -= 1
    if keyboard.is_pressed('a'):
        v[1] -= 1
    if keyboard.is_pressed('d'):
        v[1] += 1
    if keyboard.is_pressed('space'):
        v[2] += 1
    if keyboard.is_pressed('enter'):
        v[2] -= 1

    return v / np.linalg.norm(v) * maxvel


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


def command(cf: Crazyflie):
    commander = Commander(cf)
    state = 0

    while True:
        # updates state
        if keyboard.is_pressed('backspace'):
            state = 0
        elif keyboard.is_pressed('space'):
            state = 1

        # executes function based on state.
        if state == 0:
            offstate(commander)
        elif state == 1:
            onstate(commander, getvelocity())
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
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        command(scf.cf)
