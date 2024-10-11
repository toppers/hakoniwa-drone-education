import sys
import hakopy
import hako_pdu
import pdu_info
import os
from components.simulation_executor import SimulationExecutor

simulation_executor = None

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
        _ = pdu.get()
        pdu.write()

    return 0

def my_on_manual_timing_control(context):
    global simulation_executor

    simulation_executor.run()
    return 0

def my_on_reset(context):
    return 0

my_callback = {
    'on_initialize': my_on_initialize,
    'on_simulation_step': None,
    'on_manual_timing_control': my_on_manual_timing_control,
    'on_reset': my_on_reset
}

def main():
    global simulation_executor

    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <drone_config_path> <pdu_config_path> <evaluation_config_path>")
        return 1

    simulation_executor = SimulationExecutor(sys.argv[1], sys.argv[2], sys.argv[3])
    if simulation_executor.initialize(my_callback) == False:
        return 1

    ret = hakopy.start()

    return 0

if __name__ == "__main__":
    sys.exit(main())
