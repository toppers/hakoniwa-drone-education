from drone_evaluation.components.idrone_executor import IDroneExecutor
from drone_evaluation.components.impl.drone_contants import HEADING_AXIS, UP_DOWN_AXIS, ROLL_AXIS, PITCH_AXIS
from drone_evaluation.components.impl.drone_executor import joystick_init

class DroneControllerExecutorPosZ(IDroneExecutor):
    def __init__(self, client, logger, speed):
        self.client = client
        self.logger = logger
        self.speed = speed
        self.logger.set_columns(["timestamp", "target_z"])

    def takeoff(self):
        joystick_init(self.client)

    def run(self, simulation_time, signals):
        # USER INPUT IS ROS frame
        ned_z =  -signals[0]
        data = self.client.getGameJoystickData()
        data['axis'] = list(data['axis'])
        data['axis'][HEADING_AXIS]  =  self.speed
        data['axis'][UP_DOWN_AXIS]  =  ned_z    #target_z
        data['axis'][ROLL_AXIS]     =  0.0
        data['axis'][PITCH_AXIS]    =  0.0
        self.client.putGameJoystickData(data)
        self.logger.log(simulation_time, ned_z)
