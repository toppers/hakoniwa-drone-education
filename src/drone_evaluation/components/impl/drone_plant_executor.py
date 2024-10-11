from ..idrone_executor import IDroneExecutor

class DronePlantExecutor(IDroneExecutor):
    def __init__(self, client, logger):
        self.client = client
        self.logger = logger
        self.logger.set_columns(["timestamp", "c1", "c2", "c3", "c4"])

    def takeoff(self):
        #nothing to do
        pass

    def run(self, simulation_time, signals):
        data = self.client.getGameJoystickData()
        data['axis'] = list(data['axis'])
        for index in range(0, 4):
            data['axis'][index] = signals[index]
        self.client.putGameJoystickData(data)
        self.logger.log(simulation_time, data['axis'][0], data['axis'][1], data['axis'][2], data['axis'][3])
