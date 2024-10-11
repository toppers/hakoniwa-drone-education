from ..idrone_executor import IDroneExecutor
from drone_contants import HEADING_AXIS, UP_DOWN_AXIS, ROLL_AXIS, PITCH_AXIS
from drone_controller_executor import joystick_takeoff

class DroneControllerExecutorSpd(IDroneExecutor):
    def __init__(self, client, logger, height, slp_usec):
        self.client = client
        self.height = float(height)
        self.slp_usec = slp_usec
        self.logger = logger
        self.logger.set_columns(["timestamp", "target_vx", "target_vy"])

    def takeoff(self):
        joystick_takeoff(self.client, self.height, self.slp_usec)

    def _run(self, simulation_time, ros_vx, ros_vy):
        data = self.client.getGameJoystickData()
        data['axis'] = list(data['axis'])
        data['axis'][HEADING_AXIS]  =  0.0
        data['axis'][UP_DOWN_AXIS]  = -self.height
        data['axis'][ROLL_AXIS]     =  ros_vy   #target_vy
        data['axis'][PITCH_AXIS]    =  ros_vx   #target_vx

    def run(self, simulation_time, signals):
        ros_vx =  signals[0]
        ros_vy = -signals[1]
        self._run([ros_vx, ros_vy])
        self.logger.log(simulation_time, ros_vx, ros_vy)

