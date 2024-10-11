from drone_evaluation.components.idrone_executor import IDroneExecutor
from drone_evaluation.components.impl.drone_contants import HEADING_AXIS, UP_DOWN_AXIS, ROLL_AXIS, PITCH_AXIS
from drone_evaluation.components.impl.drone_controller_executor import api_send_and_wait
import pdu_info

class DroneControllerExecutorPosZ(IDroneExecutor):
    def __init__(self, client, logger, speed):
        self.client = client
        self.logger = logger
        self.speed = speed
        self.logger.set_columns(["timestamp", "target_z"])

    def takeoff(self):
        #nothing to do
        pass

    def _run(self, simulation_time, ros_z):
        command, pdu_cmd = self.client.get_packet(pdu_info.HAKO_AVATOR_CHANNEL_ID_CMD_MOVE, client.get_vehicle_name(client.default_drone_name))
        pdu_cmd['x'] = 0.0
        pdu_cmd['y'] = 0.0
        pdu_cmd['z'] = ros_z
        pdu_cmd['speed'] = self.speed
        pdu_cmd['yaw_deg'] = 0
        api_send_and_wait(command)

    def run(self, simulation_time, signals):
        # USER INPUT IS ROS frame
        ros_z =  signals[0]
        self._run(ros_z)
        self.logger.log(simulation_time, ros_z)
