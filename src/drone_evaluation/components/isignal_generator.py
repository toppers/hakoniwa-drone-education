from abc import ABC, abstractmethod

class ISignalGenerator(ABC):
    @abstractmethod
    def generate_signal(self, interval, total_time, **kwargs):
        """
        Abstract method to generate a signal.
        
        Parameters:
        interval (float): Time interval between samples.
        total_time (float): Total duration for the signal.
        kwargs: Additional parameters for signal generation.
        
        Returns:
        list: List of generated signal values.
        """
        pass
