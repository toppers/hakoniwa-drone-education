import sys
import hakosim
import hakopy
import hako_pdu
import pdu_info
import os

from utils.constants import HEADING_AXIS, UP_DOWN_AXIS, ROLL_AXIS, PITCH_AXIS

def my_on_reset(context):
    return 0


def save_evaluation_start_time(evaluation_start_time):
    print("EVALUATION_START_TIME: ", evaluation_start_time)
    with open('/tmp/v.txt', 'w') as f:
        f.write(str(evaluation_start_time))


def button_event(client, index):
    data = client.getGameJoystickData()
    data['button'] = list(data['button'])

    hakopy.usleep(500000)
    data['button'][index] = True
    client.putGameJoystickData(data)
    hakopy.usleep(500000)
    data['button'][index] = False
    client.putGameJoystickData(data)

def send_and_wait(command):
    ret = command.write()
    if ret == False:
        print('"ERROR: hako_asset_pdu_write')
        return False
    while True:
        pdu = command.read()
        if pdu == None:
            print('ERROR: hako_asset_pdu_read')
            return 0
        if pdu['header']['result'] == 1:
            pdu['header']['result'] = 0
            command.write()
            print('DONE')
            break
        #print("result: ",  pdu['header']['result'])
        hakopy.usleep(30000)
    return True


def almost_equal_deg(target_deg, real_deg, diff_deg):
    if abs(target_deg - real_deg) <= diff_deg:
        return True
    else:
        return False

def stop_control(client, height):
    while True:
        data = client.getGameJoystickData()
        data['axis'] = list(data['axis'])
        data['axis'][HEADING_AXIS] = 0.0    #heading
        data['axis'][UP_DOWN_AXIS] = float(height) #up/down
        data['axis'][ROLL_AXIS] = 0.0    #roll
        data['axis'][PITCH_AXIS] = 0.0    #pitch
        client.putGameJoystickData(data)
        hakopy.usleep(30000)


def should_stop(stop_time_usec):
    stop_time = stop_time_usec
    return (stop_time > 0) and (hakopy.simulation_time() >= stop_time)
