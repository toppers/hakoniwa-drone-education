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

config_path = ''
HEADING_AXIS = 0
UP_DOWN_AXIS = 1
ROLL_AXIS = 2
PITCH_AXIS = 3

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

def my_on_reset(context):
    return 0


def button_event(client, index):
    data = client.getGameJoystickData()
    data['button'] = list(data['button'])

    hakopy.usleep(500000)
    data['button'][index] = True
    client.putGameJoystickData(data)
    hakopy.usleep(500000)
    data['button'][index] = False
    client.putGameJoystickData(data)


def reply_and_wait_res(command):
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


def should_stop():
    global target_values
    stop_time = target_values.stop_time_usec
    return (stop_time > 0) and (hakopy.simulation_time() >= stop_time)

# ここで設定した値が、そのまま、制御側に渡る
# 入力はROS座標系なので、NED座標系に変換する
def joystick_control_angular(client, x=0, y=0, z=0, height=3.0, slp_usec = 30000):
    global target_values
    print(f"START CONTROL(ROS Frame): x({x}) y({y}) z({z})")
    x = float(x)
    y = float(y)
    z = float(z)
    height = float(height)
    while True:
        data = client.getGameJoystickData()
        # USER INPUT は ROS座標系。
        # NED座標系で渡す必要があるので、変換する。
        data['axis'] = list(data['axis'])
        data['axis'][HEADING_AXIS] = -z
        data['axis'][UP_DOWN_AXIS] = -height
        data['axis'][ROLL_AXIS]    =  x
        data['axis'][PITCH_AXIS]   = -y
        client.putGameJoystickData(data)
        hakopy.usleep(slp_usec)
        if should_stop():
            break

def joystick_control_spd(client, x=0, y=0, z=0, height=3.0, slp_usec = 30000):
    global target_values
    print(f"START CONTROL(ROS Frame): x({x}) y({y}) z({z})")
    x = float(x)
    y = float(y)
    z = float(z)
    height = float(height)
    while True:
        data = client.getGameJoystickData()
        # USER INPUT は ROS座標系。
        # NED座標系で渡す必要があるので、変換する。
        data['axis'] = list(data['axis'])
        data['axis'][HEADING_AXIS] = 0.0
        data['axis'][UP_DOWN_AXIS] = -height
        data['axis'][ROLL_AXIS]    = -y
        data['axis'][PITCH_AXIS]   =  x
        client.putGameJoystickData(data)
        hakopy.usleep(slp_usec)
        if should_stop():
            break

def joystick_control_alt_spd(client, vz, slp_usec=30000, logger = None):
    global target_values
    if not isinstance(vz, list):
        vz = [vz]

    index = 0
    vz_length = len(vz)

    while True:
        current_vz = vz[index]

        data = client.getGameJoystickData()
        data['axis'] = list(data['axis'])
        data['axis'][HEADING_AXIS] = 0.0
        data['axis'][UP_DOWN_AXIS] = -current_vz  # ROS -> NED座標系
        data['axis'][ROLL_AXIS] = 0
        data['axis'][PITCH_AXIS] = 0
        client.putGameJoystickData(data)

        if logger is not None:
            # ログデータを記録
            logger.log(hakopy.simulation_time(), -current_vz)
            if index >= vz_length - 1:
                logger.save()
        hakopy.usleep(slp_usec)

        index = (index + 1) % vz_length
        if should_stop():
            break

pdu_manager = None
client = None
class TargetValues:
    def __init__(self):
        self.values = {}
        self.stop_time_usec = -1
        self.first_key = None

    def set_stop_time(self, value: int):
        self.stop_time_usec = value
    
    def set_target(self, key, value):
        if self.first_key is None:
            self.first_key = key
        self.values[key] = float(value)
        print(f"Target {key}: {value}")

    def has_key(self, key):
        return key in self.values

    def value(self, key):
        if self.has_key(key):
            return self.values[key]
        return None

target_values = TargetValues()

def api_control(client, X = 0, Y = 0, speed = 5):
    global target_values
    print(f"START CONTROL(ROS Frame): X({X}) Y({Y}) S({speed})")
    #call api
    pose = client.simGetVehiclePose()
    command, pdu_cmd = client.get_packet(pdu_info.HAKO_AVATOR_CHANNEL_ID_CMD_MOVE, client.get_vehicle_name(client.default_drone_name))
    pdu_cmd['x'] = X # USER INPUT IS ROS frame
    pdu_cmd['y'] = Y # USER INPUT IS ROS frame
    pdu_cmd['z'] = pose.position.z_val # PDU is ROS frame
    pdu_cmd['speed'] = speed
    pdu_cmd['yaw_deg'] = 0
    reply_and_wait_res(command)
    print("reply done")
    while True:
        hakopy.usleep(30000)
        if should_stop():
            break

def is_joystick_control():
    if (target_values.has_key('X')):
        return False
    else:
        return True

def is_alt_control():
    return (target_values.first_key == 'Z')

def is_alt_spd_control():
    return (target_values.first_key == 'Vz')

def joystick_takeoff(client, height, slp_usec = 30000):
    print("JOYSTICK TAKEOFF(ROS Frame): ", height)
    pose = client.simGetVehiclePose()
    while (pose.position.z_val) < height:
        pose = client.simGetVehiclePose()
        data = client.getGameJoystickData()
        data['axis'] = list(data['axis']) 
        data['axis'][UP_DOWN_AXIS] = float(-height) #NED座標系
        client.putGameJoystickData(data)
        hakopy.usleep(slp_usec)
    print("DONE")

def api_takeoff(client, height):
    # do takeoff
    print("INFO: API TAKEOFF")
    command, pdu_cmd = client.get_packet(pdu_info.HAKO_AVATOR_CHANNEL_ID_CMD_TAKEOFF, client.get_vehicle_name(client.default_drone_name))
    pdu_cmd['height'] = height
    pdu_cmd['speed'] = 5
    pdu_cmd['yaw_deg'] = client._get_yaw_degree(client.default_drone_name)
    reply_and_wait_res(command)

    if is_alt_control():
        hakopy.usleep(10000000)

def save_evaluation_start_time(evaluation_start_time):
    print("EVALUATION_START_TIME: ", evaluation_start_time)
    with open('/tmp/v.txt', 'w') as f:
        f.write(str(evaluation_start_time))

def my_on_manual_timing_control(context):
    global pdu_manager
    global client
    global target_values
    print("INFO: on_manual_timing_control enter")

    # initialize for joystick control
    if is_joystick_control():
        button_event(client, 0)
    # takeoff
    height = 3.0
    if is_alt_control() or is_alt_spd_control():
        evaluation_start_time = hakopy.simulation_time() * 1e-06
    else:
        evaluation_start_time = None

    if is_alt_spd_control():
        # nothing to do
        pass
    elif is_joystick_control():
        joystick_takeoff(client, height)
    else:
        api_takeoff(client, height)

    if evaluation_start_time is None:
        evaluation_start_time = hakopy.simulation_time() * 1e-06

    save_evaluation_start_time(evaluation_start_time)

    # do control
    if is_alt_spd_control():
        #TODO FIX ME
        #my_logger = Logger(filename='out.csv')
        #values = signal_generate(interval = 0.001, total_time= 10, offset = target_values.value('Vz'), type = 'sine')
        #joystick_control_alt_spd(client, values, slp_usec=1000, logger=my_logger)
        joystick_control_alt_spd(client, target_values.value('Vz'))
    elif (target_values.has_key('Rx')):
        joystick_control_angular(client, target_values.value('Rx'), target_values.value('Ry'), target_values.value('Rz'), height)
    elif (target_values.has_key('Vx')):
        joystick_control_spd(client, target_values.value('Vx'), target_values.value('Vy'), target_values.value('Vz'), height)
    elif not is_alt_control():
        api_control(client, target_values.value('X'), target_values.value('Y'), target_values.value('S'))

    if is_joystick_control():
        print("INFO: start stop control")
        evaluation_start_time = hakopy.simulation_time() * 1e-06
        save_evaluation_start_time(evaluation_start_time)
        stop_control(client, height)

    print("INFO: on_manual_timing_control exit")
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

    if len(sys.argv) != 6 and len(sys.argv) != 7:
        print(f"Usage: {sys.argv[0]} <config_path> <stop_time> <tkey:tvalue> <key:value> <key:value> [S:TargetSpeed]")
        return 1

    asset_name = 'DronePlantModel'
    config_path = sys.argv[1]
    delta_time_usec = 1000

    stop_time = int(sys.argv[2])
    target_values.set_stop_time(stop_time)
    target_values.set_target(sys.argv[3].split(':')[0], sys.argv[3].split(':')[1])
    target_values.set_target(sys.argv[4].split(':')[0], sys.argv[4].split(':')[1])
    target_values.set_target(sys.argv[5].split(':')[0], sys.argv[5].split(':')[1])

    if len(sys.argv) == 7:
        target_values.set_target(sys.argv[6].split(':')[0], sys.argv[6].split(':')[1])
    else:
        target_values.set_target('S', 5)

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
