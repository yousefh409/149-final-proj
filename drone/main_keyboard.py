# import logging
import logging
import time
import keyboard
import numpy as np
import threading
import sys
from pygame import mixer
import random

from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
import cflib.crtp

import bluetooth_sigs as sigs
from bluetooth_sigs import vars as bt_vars

from subprocess import Popen, PIPE, STDOUT
import json

# hand states
OFF       = 0
ON        = 1
ASCEND    = 2
DESCEND   = 3
CIRCLE    = 4
CHACHA    = 5
UNDEFINED = 6

HAND_SIG = 0

# current state
STATE = OFF
NEXTSTATE = OFF

# other constant variables
MAX_VEL = 0.2 # 0.2 m/s

def handshape():
    if keyboard.is_pressed('backspace'):
        return OFF
    elif keyboard.is_pressed('1'):
        return ON
    elif keyboard.is_pressed('2'):
        return ASCEND
    elif keyboard.is_pressed('3'):
        return DESCEND
    elif keyboard.is_pressed('4'):
        return CHACHA
    elif keyboard.is_pressed('5'):
        return CIRCLE
    else:
        return UNDEFINED

# state functions
def offstate(cf: Crazyflie):
    cf.commander.send_stop_setpoint()

def onstate(cf: Crazyflie):
    r, p, y = 0, 0, 0
    
    # For Keyboard Use
    if keyboard.is_pressed('w'):
        p += 15
    if keyboard.is_pressed('a'):
        r -= 15
    if keyboard.is_pressed('s'):
        p -= 15
    if keyboard.is_pressed('d'):
        r += 15

    thrust = 37000
    cf.commander.send_setpoint(r, p, y, thrust)
    cf.param.set_value("flightmode.althold", "True")

def ascendstate(cf: Crazyflie):
    r, p, y = 0, 0, 0
    thrust = 42000
    cf.commander.send_setpoint(r, p, y, thrust)
    # cf.commander.send_velocity_world_setpoint(0.0, 0.0, MAX_VEL, 0.0)

def descendstate(cf: Crazyflie):
    r, p, y = 0, 0, 0
    thrust = 33500
    # cf.param.set_value("flightmode.althold", "False")
    cf.commander.send_setpoint(r, p, y, thrust)
    # cf.commander.send_velocity_world_setpoint(0.0, 0.0, -0.5*MAX_VEL, 0.0)

def chachastate(cf: Crazyflie):
    thrust = 37500
    # cf.param.set_value("flightmode.althold", "True")

    mixer.init()
    mixer.music.load("sounds/cha-cha-slide.mp3")
    mixer.music.play()

    # slide to the left
    r, p, y = 15, 0, 0
    cf.commander.send_setpoint(r, p, y, thrust)
    time.sleep(1.45)
    
    # slide to the right
    r, p, y = -15, 0, 0
    cf.commander.send_setpoint(r, p, y, thrust)
    time.sleep(1.35)
    
    # first criss cross
    # cf.param.set_value("flightmode.althold", "False")
    ### go up
    r, p, y = 0, 15, 0
    thrust = 42000
    cf.commander.send_setpoint(r, p, y, thrust)
    time.sleep(1.15)
    ### go down
    r, p, y = 0, -15, 0
    thrust = 33500
    cf.commander.send_setpoint(r, p, y, thrust)
    time.sleep(1.15)
    
    # second criss cross
    ### go up
    r, p, y = 0, 15, 0
    thrust = 42000
    cf.commander.send_setpoint(r, p, y, thrust)
    time.sleep(1.15)
    ### go down
    r, p, y = 0, -15, 0
    thrust = 33500
    cf.commander.send_setpoint(r, p, y, thrust)
    time.sleep(1.15)
    
    
    # cha cha cha
    thrust = 37500
    # cf.param.set_value("flightmode.althold", "True")
    current_time = time.time()
    while time.time() < current_time + 3:
        r, p, y = random.choice([-15, 15]), 0, 0
        cf.commander.send_setpoint(r, p, y, thrust)
        time.sleep(0.5)

    cf.commander.send_velocity_world_setpoint(0, 0, 0, 0.0)

def circlestate(cf: Crazyflie):
    current_time = time.time()
    thrust = 37500
    t = time.time() - current_time
    while t < 2*np.pi:
        t = time.time() - current_time
        r, p, y = np.cos(t), np.sin(t), 0
        cf.commander.send_setpoint(r, p, y, thrust)
    cf.commander.send_velocity_world_setpoint(0, 0, 0, 0.0)


def errorstate():
    exit(-1)

def command(cf: Crazyflie):
    cf.commander.send_setpoint(0, 0, 0, 0)
    # cf.open_link(uri)

    global STATE

    while True:
        # executes function based on state.
        if STATE == OFF:
            offstate(cf)
            print(bt_vars, 'OFFSTATE')
        elif STATE == ON:
            onstate(cf)
            print(bt_vars, 'ONSTATE')
        elif STATE == ASCEND:
            ascendstate(cf)
            print(bt_vars, 'ASCENDSTATE')
        elif STATE == DESCEND:
            descendstate(cf)
            print(bt_vars, 'DESCENDSTATE')
        elif STATE == CHACHA:
            chachastate(cf)
            print(bt_vars, 'CHACHASTATE')
        elif STATE == CIRCLE:
            chachastate(cf)
            print(bt_vars, 'CIRCLESTATE')
        else:
            print(bt_vars, 'ERRORSTATE')
            errorstate()

        if handshape() == ON:
            NEXTSTATE = ON
        elif handshape() == OFF:
            NEXTSTATE = OFF
        elif handshape() == CIRCLE:
            NEXTSTATE = CIRCLE
        elif handshape() == CHACHA:
            NEXTSTATE = CHACHA
        elif handshape() == DESCEND:
            NEXTSTATE = DESCEND
        elif handshape() == ASCEND:
            NEXTSTATE = ASCEND
        else:
            NEXTSTATE = STATE
        # convert to next state
        STATE = NEXTSTATE

        # iterate again after a pause
        time.sleep(0.1)


def initdrone():
    # URI to the Crazyflie to connect to
    uri = 'radio://0/10/250K/E7E7E7E7E7'
    logging.basicConfig(level=logging.ERROR)
    cflib.crtp.init_drivers()
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        command(scf.cf)


if __name__ == '__main__':
    drone = threading.Thread(target=initdrone)
    drone.start()
