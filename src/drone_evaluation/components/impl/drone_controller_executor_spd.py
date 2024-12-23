from drone_evaluation.components.idrone_executor import IDroneExecutor
from drone_evaluation.components.impl.drone_contants import HEADING_AXIS, UP_DOWN_AXIS, ROLL_AXIS, PITCH_AXIS
from drone_evaluation.components.impl.drone_executor import joystick_takeoff, joystick_init

class DroneControllerExecutorSpd(IDroneExecutor):
    def __init__(self, client, logger, height, slp_usec):
        self.client = client
        self.height = float(height)
        self.slp_usec = slp_usec
        self.logger = logger
        self.logger.set_columns(["timestamp", "target_vx", "target_vy"])

    def takeoff(self):
        joystick_init(self.client)
        joystick_takeoff(self.client, self.height, self.slp_usec)

    def _run(self, ned_vx, ned_vy):
        data = self.client.getGameJoystickData()
        data['axis'] = list(data['axis'])
        data['axis'][HEADING_AXIS]  =  0.0
        data['axis'][UP_DOWN_AXIS]  = -self.height
        data['axis'][ROLL_AXIS]     =  ned_vy   #target_vy
        data['axis'][PITCH_AXIS]    =  ned_vx   #target_vx
        self.client.putGameJoystickData(data)

    def run(self, simulation_time, signals):
        ned_vx =  signals[0]
        ned_vy = -signals[1]
        self._run([ned_vx, ned_vy])
        self.logger.log(simulation_time, ned_vx, ned_vy)

