# import logging
import logging
import time
# import keyboard
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

# predefined states for keyboard
# OFF = 0
# ON = 1
# ASCEND = 2
# LAND = 3
# MOVE = 4

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


def update_vars(new_vars: dict):
    """Updates the current variables obtained from bluetooth to the new ones received."""
    for key in new_vars:
        bt_vars[key] = new_vars[key]

def is_valid():
    """Returns true if bluetooth signals can be used"""
    return bt_vars['valid'] == sigs.ALLVALID

def obtain_values_from_bt(only_bluetooth=False):
    """obtains new updated values from bluetooth_sigs python process."""
    global HAND_SIG

    p = Popen('python bluetooth_sigs.py'.split(), stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    if p.stdout is None:
        print('Unable to open STDOUT for bluetooth')
        exit(1)

    for line in p.stdout:
        if not line:
            continue
        obj = json.loads(line.decode())
        update_vars(obj)
        HAND_SIG = (bt_vars['f0'] << 0) | (bt_vars['f1'] << 1) | (bt_vars['f2'] << 2) | (bt_vars['f3'] << 3)
        if only_bluetooth:
            print(bt_vars, handshape_str(), bin(HAND_SIG))


# state functions
def offstate(cf: Crazyflie):
    global NEXTSTATE

    # Keyboard Debugging
    """
    # if keyboard.is_pressed('backspace'):
    #     NEXTSTATE = OFF
    # elif keyboard.is_pressed('space'):
    #     NEXTSTATE = ASCEND
    """
    # Glove Interface
    if not is_valid():
        NEXTSTATE = OFF
    elif handshape() == ASCEND:
        NEXTSTATE = ASCEND
    elif handshape() == UNDEFINED:
        NEXTSTATE = STATE
    else:
        NEXTSTATE = OFF

    cf.commander.send_stop_setpoint()

def onstate(cf: Crazyflie):
    global NEXTSTATE

    r, p, y = 0, 0, 0

    if handshape() == ASCEND:
        NEXTSTATE = ASCEND
    elif handshape() == ON:
        NEXTSTATE = ON
    elif handshape() == CIRCLE:
        NEXTSTATE = CIRCLE
    elif handshape() == CHACHA:
        NEXTSTATE = CHACHA
    elif handshape() == DESCEND:
        NEXTSTATE = DESCEND
    elif handshape() == UNDEFINED:
        NEXTSTATE = STATE
    else:
        NEXTSTATE = OFF
        return
    
    # For Keyboard use DEBUGGING
    """
    if keyboard.is_pressed('v'):
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
    """
    # For Glove use
    # Moves the drone in the appropiate direction according to the user's hand movements
    if bt_vars["Ay"] == 1:
        p += 15
    if bt_vars["Ax"] == -1:
        r -= 15
    if bt_vars["Ay"] == -1:
        p -= 15
    if bt_vars["Ax"] == 1:
        r += 15

    thrust = 37000
    # print(f'{r:.2f} {p:.2f} {y:.2f}')
    # cf.commander.send_setpoint(r, p, y, thrust)
    # cf.param.set_value("flightmode.althold", "True")
    # commander.send_velocity_world_setpoint(0, 0, 0, 0.0)
    # switch to using vx, vy, vz, yaw instead.
    # vx = MAX_VEL * np.sin(np.deg2rad(r))
    # vy = MAX_VEL * np.cos(np.deg2rad(p))
    # vz = 0.0
    # yawrate = 0.0
    # cf.commander.send_velocity_world_setpoint(vx, vy, vz, yawrate)
    cf.commander.send_setpoint(r, p, y, thrust)
    cf.param.set_value("flightmode.althold", "True")
    vx = MAX_VEL * np.sin(np.deg2rad(r))
    vy = MAX_VEL * np.sin(np.deg2rad(p))
    vz = 0.0
    yawrate = 0.0
    cf.commander.send_velocity_world_setpoint(vx, vy, vz, yawrate)


def ascendstate(cf: Crazyflie):
    global NEXTSTATE

    # Keyboard Debugging
    """
    if keyboard.is_pressed('b'):
        NEXTSTATE = ON
    elif keyboard.is_pressed('backspace'):
        NEXTSTATE = OFF
        return
    """

    if handshape() == ASCEND:
        NEXTSTATE = ASCEND
    elif handshape() == ON:
        NEXTSTATE = ON
    elif handshape() == CIRCLE:
        NEXTSTATE = CIRCLE
    elif handshape() == DESCEND:
        NEXTSTATE = DESCEND
    elif handshape() == UNDEFINED:
        NEXTSTATE = STATE
    else:
        NEXTSTATE = OFF
        return

    r, p, y = 0, 0, 0
    thrust = 42000
    cf.commander.send_setpoint(r, p, y, thrust)
    # cf.commander.send_velocity_world_setpoint(0.0, 0.0, MAX_VEL, 0.0)


def descendstate(cf: Crazyflie):
    global NEXTSTATE

    # Glove interface
    if handshape() == ASCEND:
        NEXTSTATE = ASCEND
    elif handshape() == ON:
        NEXTSTATE = ON
    elif handshape() == CIRCLE:
        NEXTSTATE = CIRCLE
    elif handshape() == DESCEND:
        NEXTSTATE = DESCEND
    elif handshape() == UNDEFINED:
        NEXTSTATE = STATE
    else:
        NEXTSTATE = OFF
        return

    # Keyboard Debugging
    """
    if keyboard.is_pressed('space'):
        NEXTSTATE = ASCEND
    if keyboard.is_pressed('backspace'):
        NEXTSTATE = OFF
        return
    """

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
    cf.commander.send_setpoint(r, p, y, thrust)
    time.sleep(1.15)
    ### go down
    r, p, y = 0, -15, 0
    cf.commander.send_setpoint(r, p, y, thrust)
    time.sleep(1.15)
    
    # second criss cross
    ### go up
    r, p, y = 0, 15, 0
    cf.commander.send_setpoint(r, p, y, thrust)
    time.sleep(0.97)
    ### go down
    r, p, y = 0, -15, 0
    cf.commander.send_setpoint(r, p, y, thrust)
    time.sleep(0.97)
    
    # cha cha cha
    # cf.param.set_value("flightmode.althold", "True")
    current_time = time.time()
    while time.time() < current_time + 3:
        r, p, y = random.choice([-15, 15]), 0, 0
        cf.commander.send_setpoint(r, p, y, thrust)
        time.sleep(0.5)

    cf.commander.send_velocity_world_setpoint(0, 0, 0, 0.0)
    NEXTSTATE = OFF

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

def handshape():
    # States based only on the flex sensors
    if HAND_SIG == 0b0000:
        return OFF
    elif HAND_SIG == 0b0011:
        return ASCEND
    elif HAND_SIG == 0b1111:
        return ON
    elif HAND_SIG == 0b0001:
        return DESCEND
    elif HAND_SIG == 0b1001:
        return CHACHA
    elif HAND_SIG == 0b0111:
        return CIRCLE
    # elif bt_vars['f0'] and bt_vars['f1'] and bt_vars['f2'] and bt_vars['f3']:
    #     return CIRCLE
    else:
        return UNDEFINED


def handshape_str():
    hand_out = handshape()
    if hand_out == ON:
        return "ON"
    elif hand_out == ASCEND:
        return "ASCEND"
    elif hand_out == DESCEND:
        return "DESCEND"
    elif hand_out == CIRCLE:
        return "CIRCLE"
    elif hand_out == OFF:
        return "OFF"
    elif hand_out == CHACHA:
        return "CHACHA"
    else:
        return "UNDEFINED"

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
    # used for debugging bluetooth connection. Add 'bluetooth' to program arguments.
    only_bluetooth = len(sys.argv) > 1 and sys.argv[1] == 'bluetooth'

    if not only_bluetooth:
        drone = threading.Thread(target=initdrone)
        drone.start()

    # receive inputs from bluetooth
    obtain_values_from_bt(only_bluetooth)
