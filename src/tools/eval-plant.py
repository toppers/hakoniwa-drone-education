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
in_amplitude = 1

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
    logger.set_columns(["timestamp", "c1", "c2", "c3", "c4"])
    button_event(client, 0)

    c1 = target_values.value('c1')
    c2 = target_values.value('c2')
    c3 = target_values.value('c3')
    c4 = target_values.value('c4')

    offsets = [ c1, c2, c3, c4 ]

    values_list = []
    for off in offsets:
        values = signal_generate(interval = 1.0/float(delta_time_usec), total_time= stop_time_sec, offset = off, type = 'sine', frequency=in_frequency, amp = in_amplitude)
        values_list.append(values)

    step_index = 0
    stop_time_usec = stop_time_sec * 1000000
    print(f"START CONTROL: c1({c1}) c2({c2}) c3({c3}) c4({c4})")
    while True:
        data = client.getGameJoystickData()
        data['axis'] = list(data['axis'])
        for index in range(0, 4):
            data['axis'][index] = values_list[index][step_index]
        client.putGameJoystickData(data)

        logger.log(hakopy.simulation_time(), data['axis'][0], data['axis'][1], data['axis'][2], data['axis'][3])
        step_index = (step_index + 1) % len(values_list[0])
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
    global in_amplitude
    
    if len(sys.argv) != 9:
        print(f"Usage: {sys.argv[0]} <config_path> <stop_time_sec> <freq> <amp> <c1:value> <c2:value> <c3:value> <c4:value>")
        return 1

    asset_name = 'DronePlantEvalModel'
    config_path = sys.argv[1]
    stop_time_sec = int(sys.argv[2])
    in_frequency = float(sys.argv[3])
    in_amplitude = float(sys.argv[4])
    delta_time_usec = 1000

    target_values = TargetValues()
    for i in range(5, 9):
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
