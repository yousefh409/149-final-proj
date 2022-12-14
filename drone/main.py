# import logging
import logging
import time
# import keyboard
import numpy as np
import threading

# from pygame import mixer

from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
import cflib.crtp

import bluetooth_sigs as sigs
from bluetooth_sigs import vars as bt_vars

from subprocess import Popen, PIPE, STDOUT
import json

# predefined states
OFF = 0
ON = 1
ASCEND = 2
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

def update_vars(new_vars: dict):
    """Updates the current variables obtained from bluetooth to the new ones received."""
    for key in new_vars:
        bt_vars[key] = new_vars[key]

def is_valid(var_name: str):
    """Returns true if variable is valid (e.g. Ax, Ay, etc)."""
    shift_bit = sigs.shifts[var_name]
    return (bt_vars['valid'] & shift_bit) != 0

def obtain_values_from_bt():
    """obtains new updated values from bluetooth_sigs python process."""
    p = Popen('python bluetooth_sigs.py'.split(), stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    if p.stdout is None:
        print('Unable to open STDOUT for bluetooth')
        exit(1)

    for line in p.stdout:
        obj = json.loads(line.decode())
        update_vars(obj)
        # print(bt_vars)


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
    if handshape() == ASCEND:
        NEXTSTATE = ASCEND
    elif handshape() == UNDEFINED:
        NEXTSTATE = UNDEFINED
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
    elif handshape() == DESCEND:
        NEXTSTATE = DESCEND
    elif handshape() == DEFAULT:
        NEXTSTATE = NEXTSTATE
    elif handshape() == UNDEFINED:
        NEXTSTATE = UNDEFINED
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

    thrust = 37500

    # print(f'{r:.2f} {p:.2f} {y:.2f}')
    cf.commander.send_setpoint(r, p, y, thrust)
    cf.param.set_value("flightmode.althold", "True")
    # commander.send_velocity_world_setpoint(0, 0, 0, 0.0)

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
    elif handshape() == DEFAULT:
        NEXTSTATE = NEXTSTATE
    elif handshape() == UNDEFINED:
        NEXTSTATE = UNDEFINED
    else:
        NEXTSTATE = OFF
        return

    r, p, y = 0, 0, 0
    thrust = 38000
    cf.commander.send_setpoint(r, p, y, thrust)


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
    elif handshape() == DEFAULT:
        NEXTSTATE = NEXTSTATE
    elif handshape() == UNDEFINED:
        NEXTSTATE = UNDEFINED
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
    thrust = 32500
    cf.param.set_value("flightmode.althold", "False")
    cf.commander.send_setpoint(r, p, y, thrust)

# def chachastate(cf: Crazyflie):
#     thrust = 37500
#     cf.param.set_value("flightmode.althold", "True")
# 
#     mixer.init()
#     mixer.music.load("sounds/cha-cha-slide.mp3")
#     mixer.music.play()
# 
#     # slide to the left
#     r, p, y = -15, 0, 0
#     cf.commander.send_setpoint(r, p, y, thrust)
#     time.sleep(1.45)
#     
#     # slide to the right
#     r, p, y = 15, 0, 0
#     cf.commander.send_setpoint(r, p, y, thrust)
#     time.sleep(1.35)
#     
#     # first criss cross
#     cf.param.set_value("flightmode.althold", "False")
#     ### go up
#     r, p, y = 15, 15, 0
#     cf.commander.send_setpoint(r, p, y, thrust)
#     time.sleep(1.15)
#     ### go down
#     r, p, y = -15, -15, 0
#     cf.commander.send_setpoint(r, p, y, thrust)
#     time.sleep(1.15)
#     
#     # second criss cross
#     ### go up
#     r, p, y = 15, 15, 0
#     cf.commander.send_setpoint(r, p, y, thrust)
#     time.sleep(0.97)
#     ### go down
#     r, p, y = -15, -15, 0
#     cf.commander.send_setpoint(r, p, y, thrust)
#     time.sleep(0.97)
#     
#     # cha cha cha
#     cf.param.set_value("flightmode.althold", "True")
#     current_time = time.time()
#     while time.time() < current_time + 3:
#         r, p, y = random.choice([-15, 15]), 0, 0
#         cf.commander.send_setpoint(r, p, y, thrust)
#         time.sleep(0.5)
# 
#     cf.commander.send_velocity_world_setpoint(0, 0, 0, 0.0)

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
    if not (bt_vars['f0'] or bt_vars['f1'] or bt_vars['f2'] or bt_vars['f3']):
        return DEFAULT
    elif not (bt_vars['f1'] or bt_vars['f2'] or bt_vars['f3']) and bt_vars['f0']:
        return ASCEND
    elif bt_vars['f0'] and bt_vars['f1'] and bt_vars['f2'] and bt_vars['f3']:
        return DESCEND
    elif not (bt_vars['f0'] or bt_vars['f1']) and bt_vars['f2'] and bt_vars['f3']:
        return CIRCLE
    else:
        return UNDEFINED


def command(cf: Crazyflie):
    cf.commander.send_setpoint(0, 0, 0, 0)
    # cf.open_link(uri)

    global STATE

    while True:
        # executes function based on state.
        if STATE == OFF:
            offstate(cf)
            # print('OFFSTATE')
        elif STATE == ON:
            onstate(cf)
            # print('ONSTATE')
        elif STATE == ASCEND:
            ascendstate(cf)
            # print('ASCENDSTATE')
        elif STATE == LAND:
            descendstate(cf)
            # print('DESCENDSTATE')
        else:
            # print('ERRORSTATE')
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
    drone = threading.Thread(target=initdrone)
    drone.start()

    # receive inputs from bluetooth
    obtain_values_from_bt()