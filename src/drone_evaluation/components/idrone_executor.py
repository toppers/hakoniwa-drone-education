from abc import ABC, abstractmethod

class IDroneExecutor(ABC):
    @abstractmethod
    def __init__(self, client, logger, *args, **kwargs):
        """
        Initializes the DroneExecutor with the required dependencies.
        
        Parameters:
        client: Client instance for communication.
        logger: Logger instance for logging messages.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.
        """
        pass

    @abstractmethod
    def takeoff(self):
        pass

    @abstractmethod
    def run(self, simulation_time, signals):
        pass

