from drone_evaluation.components.idrone_executor import IDroneExecutor
from drone_evaluation.components.impl.drone_contants import HEADING_AXIS, UP_DOWN_AXIS, ROLL_AXIS, PITCH_AXIS
from drone_evaluation.components.impl.drone_executor import joystick_init, joystick_takeoff

class DroneControllerExecutorPos(IDroneExecutor):
    def __init__(self, client, logger, height, speed, slp_usec):
        self.client = client
        self.height = float(height)
        self.speed = speed
        self.logger = logger
        self.slp_usec = slp_usec
        self.logger.set_columns(["timestamp", "target_x", "target_y"])

    def takeoff(self):
        joystick_init(self.client)
        joystick_takeoff(self.client, self.height, self.slp_usec)


    def run(self, simulation_time, signals):
        # USER INPUT IS ROS frame
        ned_x =   signals[0]
        ned_y =  -signals[1]
        data = self.client.getGameJoystickData()
        data['axis'] = list(data['axis'])
        data['axis'][HEADING_AXIS]  =  self.speed      #target_speed
        data['axis'][UP_DOWN_AXIS]  =  -self.height    #target_z
        data['axis'][ROLL_AXIS]     =  ned_y           #target_y
        data['axis'][PITCH_AXIS]    =  ned_x           #target_x
        self.client.putGameJoystickData(data)
        self.logger.log(simulation_time, ned_x, ned_y)

