from input_param_loader import InputParamLoader
from idrone_executor import IDroneExecutor
from impl.drone_plant_executor import DronePlantExecutor
from impl.drone_controller_executor_angle import DroneControllerExecutorAngle
from impl.drone_controller_executor_pos   import DroneControllerExecutorPos
from impl.drone_controller_executor_posz  import DroneControllerExecutorPosZ
from impl.drone_controller_executor_spd   import DroneControllerExecutorSpd
from impl.drone_controller_executor_spdz  import DroneControllerExecutorSpdZ

class DroneExecutorFactory:
    def __init__(self, param_loader):
        """
        Initializes the DroneExecutorFactory with an InputParamLoader instance.
        
        Parameters:
        param_loader (InputParamLoader): Instance of InputParamLoader to load parameters from.
        """
        self.param_loader = param_loader
        self.params = self.param_loader.load_params()

    def create_executor(self, client, logger):
        """
        Creates a DroneExecutor instance based on the loaded parameters.
        
        Parameters:
        client: Client instance for communication.
        logger: Logger instance for logging messages.
        
        Returns:
        IDroneExecutor: An instance of a specific DroneExecutor subclass.
        """
        simulation_type = self.params['simulation']['type']
        
        if simulation_type == 'plant':
            return DronePlantExecutor(client, logger)
        elif simulation_type == 'controller':
            simulation_time_step = self.params['simulation']['simulation_time_step']
            controller_type = self.params['simulation'].get('controller_type', 'angle')
            if controller_type == 'angle':
                return DroneControllerExecutorAngle(client, logger, self.params['simulation']['height'], simulation_time_step)
            elif controller_type == 'spd':
                return DroneControllerExecutorAngle(client, logger, self.params['simulation']['height'], simulation_time_step)
            elif controller_type == 'spd_z':
                return DroneControllerExecutorPos(client, logger)
            elif controller_type == 'pos':
                return DroneControllerExecutorPos(client, logger, self.params['simulation']['height'], self.params['simulation']['speed'])
            elif controller_type == 'pos_z':
                return DroneControllerExecutorPosZ(client, logger, self.params['simulation']['speed'])
            else:
                raise ValueError(f"Unsupported controller type: {controller_type}")
        else:
            raise ValueError(f"Unsupported simulation type: {simulation_type}")

# Example usage
if __name__ == "__main__":
    from input_param_loader import InputParamLoader
    import logging

    # Setup logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Assume we have a JSON file named 'simulation_params.json'
    loader = InputParamLoader('simulation_params.json')
    factory = DroneExecutorFactory(loader)

    client = "mock_client"
    try:
        executor = factory.create_executor(client, logger)
        print(f"Created executor: {type(executor).__name__}")
    except ValueError as e:
        print(e)