from abc import ABC, abstractmethod

class ISignalGenerator(ABC):
    @abstractmethod
    def generate_signal(self, interval_sec, total_time_sec):
        pass
