import hakopy
import pdu_info
from drone_evaluation.components.impl.drone_contants import UP_DOWN_AXIS

def joystick_takeoff(client, height, slp_usec = 30000):
    print("JOYSTICK TAKEOFF(ROS Frame): ", height)
    pose = client.simGetVehiclePose()
    while (pose.position.z_val) < (height - 0.1):
        pose = client.simGetVehiclePose()
        data = client.getGameJoystickData()
        data['axis'] = list(data['axis']) 
        data['axis'][UP_DOWN_AXIS] = float(-height) #NED座標系
        client.putGameJoystickData(data)
        hakopy.usleep(slp_usec)

def joystick_init(client):
    data = client.getGameJoystickData()
    data['button'] = list(data['button'])

    hakopy.usleep(500000)
    data['button'][0] = True
    client.putGameJoystickData(data)
    hakopy.usleep(500000)
    data['button'][0] = False
    client.putGameJoystickData(data)

def api_send_and_wait(command):
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

def api_takeoff(client, height):
    # do takeoff
    print("INFO: API TAKEOFF")
    command, pdu_cmd = client.get_packet(pdu_info.HAKO_AVATOR_CHANNEL_ID_CMD_TAKEOFF, client.get_vehicle_name(client.default_drone_name))
    pdu_cmd['height'] = height
    pdu_cmd['speed'] = 5
    pdu_cmd['yaw_deg'] = client._get_yaw_degree(client.default_drone_name)
    api_send_and_wait(command)

