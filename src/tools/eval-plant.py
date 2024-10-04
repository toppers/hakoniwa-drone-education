#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import hakosim
import hakopy
import hako_pdu
import pdu_info
import os
import numpy as np
import pandas as pd
from utils.signal import signal_generate
from utils.logger import Logger
from utils.target_value import TargetValues
from utils.constants import HEADING_AXIS, UP_DOWN_AXIS, ROLL_AXIS, PITCH_AXIS
from utils.misc import button_event, save_evaluation_start_time, my_on_reset, send_and_wait, stop_control, should_stop

config_path = ''
pdu_manager = None
client = None
delta_time_usec = 1000
stop_time_sec = 10
in_frequency = 1

def my_on_initialize(context):
    global config_path
    robot_name = 'DroneTransporter'
    hako_binary_path = os.getenv('HAKO_BINARY_PATH', '/usr/local/lib/hakoniwa/hako_binary/offset')
    pdu_manager = hako_pdu.HakoPduManager(hako_binary_path, config_path)

    pdu_channels = [
        pdu_info.HAKO_AVATOR_CHANNLE_ID_COLLISION,
        pdu_info.HAKO_AVATOR_CHANNEL_ID_DISTURB,
        pdu_info.HAKO_AVATOR_CHANNEL_ID_CAMERA_DATA,
        pdu_info.HAKO_AVATOR_CHANNEL_ID_CAMERA_INFO,
        pdu_info.HAKO_AVATOR_CHANNEL_ID_LIDAR_DATA,
        pdu_info.HAKO_AVATOR_CHANNEL_ID_LIDAR_POS,
        pdu_info.HAKO_AVATOR_CHANNEL_ID_STAT_MAG,
    ]

    for channel in pdu_channels:
        pdu = pdu_manager.get_pdu(robot_name, channel)
        pdu_data = pdu.get()
        pdu.write()

    return 0

def my_on_manual_timing_control(context):
    global target_values
    global delta_time_usec
    global stop_time_sec
    global in_frequency
    logger = Logger(filename='in.csv')
    button_event(client, 0)

    thrust   = target_values.value('T')
    torque_x = target_values.value('Tx')
    torque_y = target_values.value('Ty')
    torque_z = target_values.value('Tz')

    key_index = UP_DOWN_AXIS
    off_value = thrust
    if target_values.first_key == 'Tx':
        key_index = ROLL_AXIS
        off_value = torque_x
    elif target_values.first_key == 'Ty':
        key_index = PITCH_AXIS
        off_value = torque_y
    elif target_values.first_key == 'Tz':
        key_index = HEADING_AXIS
        off_value = torque_z

    step_index = 0
    stop_time_usec = stop_time_sec * 1000000
    values = signal_generate(interval = 1.0/float(delta_time_usec), total_time= stop_time_sec, offset = off_value, type = 'sine', frequency=in_frequency)
    print(f"START CONTROL: thrust({thrust}) torque_x({torque_x}) torque_y({torque_y} torque_z({torque_z})")
    while True:
        data = client.getGameJoystickData()
        data['axis'] = list(data['axis'])
        for index in range(0, 4):
            if index == key_index:
                data['axis'][key_index] = values[step_index]
            else:
                data['axis'][index] = 0.0
        client.putGameJoystickData(data)

        logger.log(hakopy.simulation_time(), values[step_index])
        step_index = (step_index + 1) % len(values)
        #print(f"index: {step_index} value: {values[step_index]}")
        hakopy.usleep(delta_time_usec)
        if should_stop(stop_time_usec):
            break
    logger.save()
    print ("DONE")
    return 0

my_callback = {
    'on_initialize': my_on_initialize,
    'on_simulation_step': None,
    'on_manual_timing_control': my_on_manual_timing_control,
    'on_reset': my_on_reset
}

def main():
    global client
    global config_path
    global target_values
    global stop_time_sec
    global in_frequency
    
    if len(sys.argv) != 8:
        print(f"Usage: {sys.argv[0]} <config_path> <stop_time_sec> <freq> <tkey:tvalue> <key:value> <key:value> <key:value>")
        return 1

    asset_name = 'DronePlantEvalModel'
    config_path = sys.argv[1]
    stop_time_sec = int(sys.argv[2])
    in_frequency = float(sys.argv[3])
    delta_time_usec = 1000

    target_values = TargetValues()
    for i in range(4, 8):
        target_values.set_target(sys.argv[i].split(':')[0], sys.argv[i].split(':')[1])

    # connect to the HakoSim simulator
    client = hakosim.MultirotorClient(config_path)
    client.default_drone_name = "DroneTransporter"
    hako_binary_path = os.getenv('HAKO_BINARY_PATH', '/usr/local/lib/hakoniwa/hako_binary/offset')
    client.pdu_manager = hako_pdu.HakoPduManager(hako_binary_path, config_path)
    client.enableApiControl(True)
    client.armDisarm(True)

    ret = hakopy.asset_register(asset_name, config_path, my_callback, delta_time_usec, hakopy.HAKO_ASSET_MODEL_PLANT)
    if ret == False:
        print(f"ERROR: hako_asset_register() returns {ret}.")
        return 1

    ret = hakopy.start()
    print(f"INFO: hako_asset_start() returns {ret}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
