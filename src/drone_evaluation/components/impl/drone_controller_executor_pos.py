from drone_evaluation.components.idrone_executor import IDroneExecutor
from drone_evaluation.components.impl.drone_contants import HEADING_AXIS, UP_DOWN_AXIS, ROLL_AXIS, PITCH_AXIS
from drone_evaluation.components.impl.drone_controller_executor import api_takeoff, api_send_and_wait
import pdu_info

class DroneControllerExecutorPos(IDroneExecutor):
    def __init__(self, client, logger, height, speed):
        self.client = client
        self.height = float(height)
        self.speed = speed
        self.logger = logger
        self.logger.set_columns(["timestamp", "target_x", "target_y"])

    def takeoff(self):
        api_takeoff(self.client, self.height)

    def _run(self, simulation_time, ros_x, ros_y):
        pose = self.client.simGetVehiclePose()
        command, pdu_cmd = self.client.get_packet(pdu_info.HAKO_AVATOR_CHANNEL_ID_CMD_MOVE, client.get_vehicle_name(client.default_drone_name))
        pdu_cmd['x'] = ros_x
        pdu_cmd['y'] = ros_y
        pdu_cmd['z'] = pose.position.z_val # PDU is ROS frame
        pdu_cmd['speed'] = self.speed
        pdu_cmd['yaw_deg'] = 0
        api_send_and_wait(command)

    def run(self, simulation_time, signals):
        # USER INPUT IS ROS frame
        ros_x =  signals[0]
        ros_y =  signals[1]
        self._run([ros_x, ros_y])
        self.logger.log(simulation_time, ros_x, ros_y)

