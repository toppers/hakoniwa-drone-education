from drone_evaluation.components.idrone_executor import IDroneExecutor
from drone_evaluation.components.impl.drone_contants import HEADING_AXIS, UP_DOWN_AXIS, ROLL_AXIS, PITCH_AXIS
from drone_evaluation.components.impl.drone_executor import joystick_takeoff, joystick_init

class DroneControllerExecutorAngle(IDroneExecutor):
    def __init__(self, client, logger, height, slp_usec):
        self.client = client
        self.height = float(height)
        self.slp_usec = slp_usec
        self.logger = logger
        self.logger.set_columns(["timestamp", "target_rx", "target_ry", "target_rz"])

    def takeoff(self):
        joystick_init(self.client)
        joystick_takeoff(self.client, self.height, self.slp_usec)

    def run(self, simulation_time, signals):
        data = self.client.getGameJoystickData()
        ros_rx =  signals[0]
        ros_ry = -signals[1]
        ros_rz = -signals[2]
        data['axis'] = list(data['axis'])
        data['axis'][HEADING_AXIS]  =  ros_rz   #target_rz
        data['axis'][UP_DOWN_AXIS]  = -self.height
        data['axis'][ROLL_AXIS]     =  ros_rx   #target_rx
        data['axis'][PITCH_AXIS]    =  ros_ry   #target_ry
        self.logger.log(simulation_time, ros_rx, ros_ry, ros_rz)

