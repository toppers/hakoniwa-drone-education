from drone_evaluation.components.idrone_executor import IDroneExecutor
from drone_evaluation.components.impl.drone_contants import HEADING_AXIS, UP_DOWN_AXIS, ROLL_AXIS, PITCH_AXIS

class DroneControllerExecutorSpdZ(IDroneExecutor):
    def __init__(self, client, logger):
        self.client = client
        self.logger = logger
        self.logger.set_columns(["timestamp", "target_vz"])

    def takeoff(self):
        #nothing to do
        pass

    def run(self, simulation_time, signals):
        data = self.client.getGameJoystickData()
        ros_vz = -signals[0]
        data['axis'] = list(data['axis'])
        data['axis'][HEADING_AXIS] = 0.0
        data['axis'][UP_DOWN_AXIS] = ros_vz  # ROS -> NED座標系
        data['axis'][ROLL_AXIS]    = 0
        data['axis'][PITCH_AXIS]   = 0
        self.logger.log(simulation_time, ros_vz)

